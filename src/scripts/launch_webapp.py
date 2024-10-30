## ###############################################################
## LOAD MODULES
## ###############################################################
# from flask import Flask, render_template, request
from flask import Flask, render_template, request, redirect, url_for

import os, sys, re, yaml
from datetime import datetime

import WWDatabase


## ###############################################################
## FUNCTIONS
## ###############################################################
def load_colors_from_css(file_path):
  colors = {}
  with open(file_path, 'r') as file:
    css_content = file.read()
    # Use regex to find color variables
    matches = re.findall(r'--(.*?):\s*(.*?);', css_content)
    for name, value in matches:
      colors[name.strip()] = value.strip()
  return colors

def setup_database(article_dir):
  print(f"Setting up database")
  db = WWDatabase.ArticleDatabase(start_fresh=False)
  print(f"Loading articles from {article_dir}")
  # db.add_articles_from_directory(article_dir)
  # First check if the file_metadata is up to date
  modified_articles = db.find_modified_articles(article_dir)
  print(f"detected {len(modified_articles)} modified articles")
  # Add all articles if the file_metadata is not up to date
  for articlePath in modified_articles:
    print(f"Updating article {articlePath}")
    db.add_article_from_MD(articlePath)
  # And clean up stale entries
  db.clean_up_file_metadata(article_dir)
  print(f"Database setup complete")
  return db

def get_theme():
  with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)
  THEME = config['default_theme']
  theme = request.args.get('theme', THEME)  # Get selected theme
  return theme

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    # Save the selected theme
    selected_theme = request.form.get('theme')
    with open('config.yaml', 'r') as config_file:
      config = yaml.safe_load(config_file)
    config['default_theme'] = selected_theme
    with open('config.yaml', 'w') as config_file:
      yaml.safe_dump(config, config_file)
    return redirect(url_for('index'))

  theme = get_theme()
  print(f"Loading theme: {theme}")  # Debug statement
  colors = load_colors_from_css(f'static/themes/{theme}.css')  # Load colors based on selected theme

  # List all theme files in the static/themes directory
  theme_dir = 'static/themes'
  available_themes = [f[:-4] for f in os.listdir(theme_dir) if f.endswith('.css')]  # Remove .css extension
  print(f"Available themes: {available_themes}")  # Debug statement

  sort_by = request.args.get('sort_by', 'ai_rating')
  filter_tag = request.args.get('filter_tag', '')
  show_processed = request.args.get('show_processed', 'unprocessed')

  # Create a new connection for each request
  with db.get_connection() as conn:
    cursor = conn.cursor()
  
    query = '''
      SELECT am.*, GROUP_CONCAT(tl.tag) as tags, ar.ai_rating, ar.ai_reason, at.processed
      FROM article_metadata am
      LEFT JOIN article_tags at ON am.id = at.article_id
      LEFT JOIN tag_labels tl ON (at.tags & (1 << tl.tag_id)) != 0
      LEFT JOIN article_ratings ar ON am.id = ar.article_id
      WHERE 1=1
    '''
    params = []

    if filter_tag:
      query += '''
      AND EXISTS (
          SELECT 1 FROM tag_labels tl2
          WHERE (at.tags & (1 << tl2.tag_id)) != 0
          AND tl2.tag = ?
          )
        '''
      params.append(filter_tag)

    if show_processed == 'processed':
      query += ' AND at.processed = 1'
    elif show_processed == 'unprocessed':
      query += ' AND at.processed = 0'
    
    query += f'''
    GROUP BY am.id
    ORDER BY {sort_by} DESC
    '''
    cursor.execute(query, params)
    
    articles = cursor.fetchall()
    # Get all unique tags for the filter dropdown
    cursor.execute('SELECT DISTINCT tag FROM tag_labels')
    all_tags = [row[0] for row in cursor.fetchall()]
  
  formatted_articles = []
  for article in articles:
    formatted_article = list(article)
    # Format date_published (index 4) and date_updated (index 5)
    if formatted_article[4]:
      formatted_article[4] = datetime.fromisoformat(formatted_article[4]).strftime('%d-%m-%Y')
    if formatted_article[5]:
      formatted_article[5] = datetime.fromisoformat(formatted_article[5]).strftime('%d-%m-%Y')

    formatted_articles.append(formatted_article)

  return render_template('index.html', articles=formatted_articles, all_tags=all_tags, 
               current_sort=sort_by, current_filter=filter_tag, 
               show_processed=show_processed, colors=colors, current_theme=theme,
               available_themes=available_themes)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
  theme = get_theme()
  
  print(f"Loading theme: {theme}")  # Debug statement
  colors = load_colors_from_css(f'static/themes/{theme}.css')  # Load colors based on selected theme
  config_path = 'config.yaml'
  
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

@app.route('/process/<string:arxiv_id>')
def process_article(arxiv_id):
  with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('UPDATE article_tags SET processed = 1 WHERE article_id = (SELECT id FROM article_metadata WHERE arxiv_id = ?)', (arxiv_id,))
    conn.commit()
  return redirect(url_for('index'))

@app.route('/link/<string:arxiv_id>')
def link_article(arxiv_id):
  # Constrct the arXiv URL
  url = f'https://arxiv.org/abs/{arxiv_id}'
  return redirect(url)

with open('config.yaml', 'r') as config_file:
  config = yaml.safe_load(config_file)
ARTICLES_DIR = config['output_directory']
DEFAULT_THEME = config['default_theme']
# db = setup_database(ARTICLES_DIR)


## ###############################################################
## MAIN PROGRAM
## ###############################################################
def main():
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