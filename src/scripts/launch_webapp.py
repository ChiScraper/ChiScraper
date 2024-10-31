## ###############################################################
## LOAD MODULES
## ###############################################################
from flask import Flask, render_template, request, redirect, url_for
import os, sys, re, yaml, logging
# Import the logging environment variables, 
# IT IS IMPORTANT TO DO THIS BEFORE IMPORTING ANY OTHER MODULES,
# OTHERWISE THE LOGGING CONFIGURATION WILL NOT BE SET FOR THEM
LOG_LEVEL = os.getenv('LOG_LEVVEL', 'INFO')  # Default to INFO if not set
LOG_FILE = os.getenv('LOG_FILE', 'app.log')  # Default to app.log if not set
logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL)

from datetime import datetime

from src.headers import Directories
from src.headers import FileNames
from src.headers import WWDatabase
from src.headers import WWArticles


## ###############################################################
## HELPER FUNCTIONS
## ###############################################################

def setup_database(article_dir):
  logging.info("Setting up database")
  db = WWDatabase.ArticleDatabase(start_fresh=False)
  logging.info(f"Loading articles from {article_dir}")

  # First check if the file_metadata is up to date
  modified_articles = db.find_modified_articles(article_dir)
  logging.info(f"detected {len(modified_articles)} modified articles")

  # Add all articles if the file_metadata is not up to date
  for articlePath in modified_articles:
    logging.debug(f"Updating article {articlePath}")
    db.add_article_from_MD(articlePath)
  
  logging.info(f"Checked all the articles. Now clean up any stale entries")
  db.clean_up_file_metadata(article_dir)

  logging.info(f"Database setup complete")
  return db

def get_theme():
  # THEME = 'default_theme'
  THEME = app.config['db'].get_theme() if app.config['db'].get_theme() else 'default_theme'
  theme = request.args.get('theme', THEME)  # Get selected theme
  app.config['db'].update_theme(theme)
  return theme

def load_colors_from_css(file_path):
  colors = {}
  with open(file_path, 'r') as file:
    css_content = file.read()
    # Use regex to find color variables
    matches = re.findall(r'--(.*?):\s*(.*?);', css_content)
    for name, value in matches:
      colors[name.strip()] = value.strip()
  return colors

## ###############################################################
## FLASK APPLICATION
## ###############################################################

# Setup the paths for the css and html files
templatesPath = os.path.join(Directories.directory_webApp, 'templates')
staticPath = os.path.join(Directories.directory_webApp, 'static')
# Create the Flask app
app = Flask(__name__,
             static_url_path=staticPath,static_folder=staticPath,
             template_folder=templatesPath
             )

## ##############
## Pages
## ##############
@app.route('/', methods=['GET', 'POST'])
def index():

  theme = get_theme()
  logging.info(f"Loading theme: {theme}")  
  theme_dir = os.path.join(staticPath, 'themes')

  # Variables Accessed in the HTML

  ## Colour Variables
  colors = load_colors_from_css(os.path.join(theme_dir, f'{theme}.css'))  # Load colors based on selected theme
  # List all theme files in the static/themes directory
  available_themes = [f[:-4] for f in os.listdir(theme_dir) if f.endswith('.css')]  

  ## Filtering and Sorting Variables
  sort_by = request.args.get('sort_by', 'ai_rating')
  filter_tag = request.args.get('filter_tag', '')
  show_processed = request.args.get('show_processed', 'u')

  # Access the database to get the articles
  articles = app.config['db'].get_articles_list(filter_tag, show_processed, sort_by)
  # ... and the tags
  all_tags = app.config['db'].get_all_unique_tags()
  
  formatted_articles = []
  for index, article in enumerate(articles):
    # For each article returned by the query, format it into a list
    formatted_article = list(article)
    # These indexes correspond to the columns of the SQL Tables. 
    # TODO: Document the schema of the tables
    # Format date_published (index 4) and date_updated (index 5)
    if formatted_article[4]:
      formatted_article[4] = datetime.fromisoformat(formatted_article[4]).strftime('%d-%m-%Y')
    if formatted_article[5]:
      formatted_article[5] = datetime.fromisoformat(formatted_article[5]).strftime('%d-%m-%Y')
    # Insert the index of the article at position 0
    formatted_article.insert(0, index+1)


    formatted_articles.append(formatted_article)

  # Now all the variables are ready, we can render the page using the `index.html` template
  return render_template('index.html', articles=formatted_articles, all_tags=all_tags, 
               current_sort=sort_by, current_filter=filter_tag, 
               show_processed=show_processed, colors=colors, current_theme=theme,
               available_themes=available_themes)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
  # This is the settings page, where the user can change the settings of the webapp
  theme = get_theme()
  logging.info(f"Loading theme: {theme}")  # Debug statement
  colorPath = os.path.join(staticPath, 'themes', f'{theme}.css')
  colors = load_colors_from_css(colorPath)  # Load colors based on selected theme

  # NOTE: Remove the YAML File Handling
  # NOTE: This will be replaced with a database in the future
  # NOTE: At the moment it is a place holder
  # config_path = os.path.join(Directories.directory_config, FileNames.filename_yaml)
  # if request.method == 'POST':
  #   # Save the settings
  #   new_config = request.form.to_dict()
  #   with open(config_path, 'w') as config_file:
  #     yaml.safe_dump(new_config, config_file)
  #   success_message = 'Settings saved successfully!'
  #   return redirect(url_for('settings'))
  
  # # Load the settings
  # with open(config_path, 'r') as config_file:
  #   config = yaml.safe_load(config_file)

  config = {}
  
  # Categorize settings
  ai_settings = {k: v for k, v in config.items() if k.startswith('ai_') or k.startswith('Run_AI') or k == 'host'}
  search_settings = {k: v for k, v in config.items() if k.startswith('search_') or k in ['config_name', 'lookback_date']}
  output_settings = {k: v for k, v in config.items() if k.startswith('output_')}
  misc_settings = {k: v for k, v in config.items() if k not in ai_settings and k not in search_settings and k not in output_settings}
  
  return render_template('settings.html', ai_settings=ai_settings, search_settings=search_settings, 
               output_settings=output_settings, misc_settings=misc_settings, colors=colors)

###################
## Actions 
###################

@app.route('/process/<string:arxiv_id>')
def process_article(arxiv_id):
  status = request.args.get('status')  # Get status from query parameters
  logging.info(f"Processing article {arxiv_id}, Status: {status}")

  # Step 1, lets load it into the database. 
  # 1.1: Convert the status into an integer
  statusDict = {'u':0,
                'r':1,
                'R':2,
                'd':3,
                'D':4,
                '-':5
                }
  # This determines how to save the status into the database
  statusInt = statusDict[status]
  # 1.2: Update the database
  app.config['db'].update_article_processed_status(arxiv_id,statusInt)

  # Step 2, lets update the markdown file
  # 2.1: Find the article path
  articlePath = os.path.join(Directories.directory_mdfiles, f'{arxiv_id}.md')
  # 2.2: Load the article into a dictionary
  article = WWArticles.readMarkdownFile2Dict(articlePath)
  # 2.3: Update the status
  article['task_status'] = status 
  # 2.4: Save the article back to the markdown file
  WWArticles.saveArticle2Markdown(article, bool_overwrite=True)
  
  # Now we can exit, and refresh the page
  return redirect(url_for('index'))

@app.route('/link/<string:arxiv_id>')
def link_article(arxiv_id):
  # Constrct the arXiv URL
  url = f'https://arxiv.org/abs/{arxiv_id}'
  return redirect(url)





## ###############################################################
## MAIN PROGRAM
## ###############################################################
def main():
  
  ARTICLES_DIR = Directories.directory_mdfiles
  DEFAULT_THEME = "default_theme" 

  if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    db = setup_database(ARTICLES_DIR)
    # db.display_table_heads()
  app.run(debug=True)


## ###############################################################
## PROGRAM ENTRY POINT
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit(0)


## END OF PROGRAM