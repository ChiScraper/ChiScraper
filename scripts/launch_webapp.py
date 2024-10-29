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

from headers import Directories
from headers import FileNames
from headers import WWDatabase
from headers import WWArticles


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
  THEME = 'default_theme'
  theme = request.args.get('theme', THEME)  # Get selected theme
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
  show_processed = request.args.get('show_processed', 'unprocessed')

  with app.config['db'].get_connection() as conn:
    cursor = conn.cursor()

    # This SQL query selects all columns from article_metadata (am), 
    # concatenates all tags from tag_labels (tl) into a single string, 
    # and also selects ai_rating, ai_reason from article_ratings (ar), 
    # and processed status from article_tags (at). 
    # It joins these tables based on their relationships and applies no specific condition.
    query = '''
      SELECT am.*, GROUP_CONCAT(tl.tag) as tags, ar.ai_rating, ar.ai_reason, at.processed
      FROM article_metadata am
      LEFT JOIN article_tags at ON am.id = at.article_id
      LEFT JOIN tag_labels tl ON (at.tags & (1 << tl.tag_id)) != 0
      LEFT JOIN article_ratings ar ON am.id = ar.article_id
      WHERE 1=1
    '''
    params = []

    # If a tag is selected, filter by that tag
    if filter_tag:
      query += '''
      AND EXISTS (
          SELECT 1 FROM tag_labels tl2
          WHERE (at.tags & (1 << tl2.tag_id)) != 0
          AND tl2.tag = ?
          )
        '''
      params.append(filter_tag)

    # If show_processed is set, filter by processed status
    if show_processed == 'processed':
      query += ' AND at.processed = 1'
    elif show_processed == 'unprocessed':
      query += ' AND at.processed = 0'
    
    # Finish the query by grouping by article id and ordering by the selected column
    query += f'''
    GROUP BY am.id
    ORDER BY {sort_by} DESC
    '''
    # Now actually execute the SQL query we constructed
    cursor.execute(query, params)

    # Once the query is executed, fetch all the results 
    articles = cursor.fetchall()

    # Generate a new query, this one is to grab all the unique tags for the filter dropdown
    # cursor.execute('SELECT DISTINCT tag FROM tag_labels')
    # all_tags = [row[0] for row in cursor.fetchall()]
    all_tags = app.config['db'].get_all_unique_tags()
  
  formatted_articles = []
  for article in articles:
    # For each article returned by the query, format it into a list
    formatted_article = list(article)
    # These indexes correspong to the columns of the SQL Tables. 
    # TODO: Document the schema of the tables
    # Format date_published (index 4) and date_updated (index 5)
    if formatted_article[4]:
      formatted_article[4] = datetime.fromisoformat(formatted_article[4]).strftime('%d-%m-%Y')
    if formatted_article[5]:
      formatted_article[5] = datetime.fromisoformat(formatted_article[5]).strftime('%d-%m-%Y')

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
  config_path = os.path.join(Directories.directory_config, FileNames.filename_yaml)
  
  if request.method == 'POST':
    # Save the settings
    new_config = request.form.to_dict()
    with open(config_path, 'w') as config_file:
      yaml.safe_dump(new_config, config_file)
    success_message = 'Settings saved successfully!'
    return redirect(url_for('settings'))
  
  # Load the settings
  with open(config_path, 'r') as config_file:
    config = yaml.safe_load(config_file)
  
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
  with app.config['db'].get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('UPDATE article_tags SET processed = 1 WHERE article_id = (SELECT id FROM article_metadata WHERE arxiv_id = ?)', (arxiv_id,))
    conn.commit()
  articlePath = os.path.join(Directories.directory_mdfiles, f'{arxiv_id}.md')
  article = WWArticles.readMarkdownFile2Dict(articlePath)
  article['task_status'] = 'r' # TODO:  Add multiple types of tagging
  WWArticles.saveArticle2Markdown(Directories.directory_mdfiles, article)
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