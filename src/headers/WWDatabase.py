import sqlite3
import os
from datetime import datetime
from src.headers import WWArticles
from src.headers import WWFnFs
import logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')  # Default to INFO if not set
LOG_FILE = os.getenv('LOG_FILE', 'app.log')  # Default to app.log if not set
logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL)



class ArticleDatabase:
  def __init__(self, db_name='articles.db', overwrite_duplicates=False, start_fresh=False):
    self.db_name = db_name
    # If start_fresh is True, delete the existing database
    if start_fresh and os.path.exists(self.db_name):
      os.remove(self.db_name)
      
    self.overwrite_duplicates = overwrite_duplicates

    self.conn = sqlite3.connect(self.db_name)
    self.cursor = self.conn.cursor()
    self.create_database()

    # # Check if the database exists, create it if it doesn't
    # if not os.path.exists(self.db_name):
    #     self.create_database()
    # else:
    #     print(f"Database '{self.db_name}' already exists.")
  
  def create_database(self):
    logging.info("Creating database and tables")
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()

    # Create article_metadata table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS article_metadata (
      id INTEGER PRIMARY KEY,
      title TEXT NOT NULL,
      arxiv_id TEXT UNIQUE NOT NULL,
      url_pdf TEXT,
      date_published DATE,
      date_updated DATE,
      category_primary TEXT,
      category_others TEXT,
      authors TEXT,
      abstract TEXT
    )
    ''')

    # Create article_ratings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS article_ratings (
      id INTEGER PRIMARY KEY,
      article_id INTEGER UNIQUE,
      arxiv_id INTEGER,
      ai_rating REAL,
      ai_reason TEXT,
      user_rating INTEGER,
      FOREIGN KEY (article_id) REFERENCES article_metadata (id)
    )
    ''')

    # Create tag_labels table, this is JUST known tags, 
    # no article information is stored here
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tag_labels (
      tag_id INTEGER PRIMARY KEY,
      tag TEXT NOT NULL UNIQUE
    )
    ''')
    # Create article_tags table. 
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS article_tags (
      article_id INTEGER PRIMARY KEY,
      tags INTEGER NOT NULL,
      processed INTEGER DEFAULT 0,
      FOREIGN KEY (article_id) REFERENCES article_metadata (id)
    )
    ''')

    # Create file_metadata table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS file_metadata (
      article_id INTEGER PRIMARY KEY,
      last_updated DATETIME,
      FOREIGN KEY (article_id) REFERENCES article_metadata (id)
    )
    ''')

    # Create settings table, to internally store state and settings
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
      key TEXT PRIMARY KEY,
      theme TEXT,
      filter_process INTEGER,
      filter_tag INTEGER,
      sort_by INTEGER
    )
    ''')

    conn.commit()
    conn.close()
    print("Database and tables created successfully.")

  def check_if_tag_exists(self, tag):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT tag_id FROM tag_labels WHERE tag = ?', (tag,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

  def find_articles_with_tag(self, tag):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT tag_id FROM tag_labels WHERE tag = ?', (tag,))
    result = cursor.fetchone()
    if result:
      tag_id = result[0]
      cursor.execute('SELECT article_id FROM article_tags WHERE (tags & ?) != 0', (1 << tag_id,))
      conn.close()
      return [row[0] for row in self.cursor.fetchall()]
    conn.close()
    return []

  def find_unranked_articles(self):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    # Grab all the article IDs from article_tags where processed = 0
    cursor.execute('SELECT article_id FROM article_tags WHERE processed = 0')
    article_ids = [row[0] for row in cursor.fetchall()]
    # Check if there is an entry in article_ratings for each of these article IDs
    cursor.execute('SELECT article_id FROM article_ratings')
    existing_article_ids = [row[0] for row in cursor.fetchall()]
    # Find the difference between the two lists
    unranked_articles = [article_id for article_id in article_ids if article_id not in existing_article_ids]
    conn.close()
    return unranked_articles
  
  def update_article_tags(self, article_id, add_tags=None, remove_tags=None):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    if add_tags:
      for tag in add_tags:
        cursor.execute('SELECT tag_id FROM tag_labels WHERE tag = ?', (tag,))
        result = cursor.fetchone()
        if result:
          tag_id = result[0]
          cursor.execute('UPDATE article_tags SET tags = tags | ? WHERE article_id = ?', 
                    (1 << tag_id, article_id))
    if remove_tags:
      for tag in remove_tags:
        cursor.execute('SELECT tag_id FROM tag_labels WHERE tag = ?', (tag,))
        result = cursor.fetchone()
        if result:
          tag_id = result[0]
          cursor.execute('UPDATE article_tags SET tags = tags & ~? WHERE article_id = ?', 
                    (1 << tag_id, article_id))
    conn.commit()
    conn.close()
  
  def update_article_processed_status(self, arxiv_id,status):
    # Verify that the status is a valid int
    if type(status) != int:
      raise ValueError("Status must be an integer")

    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f'UPDATE article_tags SET processed = {status} WHERE article_id = (SELECT id FROM article_metadata WHERE arxiv_id = ?)', (arxiv_id,))
        conn.commit()

  def update_theme(self, theme_path):
    with self.get_connection() as conn:
      logging.info(f"Updating theme to {theme_path}")
      cursor = conn.cursor()
      cursor.execute('SELECT * FROM settings')
      if cursor.fetchone():
        cursor.execute('UPDATE settings SET theme = ?', (theme_path,))
      else:
        cursor.execute('INSERT INTO settings (theme, key) VALUES (?, ?)', (theme_path, 0))
      conn.commit()

  def list_table_columns(self):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()

    tables = ['article_metadata', 'article_ratings', 'article_tags', 'file_metadata']

    for table in tables:
      print(f"\n{table} table columns:")
      cursor.execute(f"PRAGMA table_info({table})")
      columns = cursor.fetchall()
      for column in columns:
        print(column[1])  # Column name is at index 1
    conn.close()

  def display_table_heads(self, limit=5):
    print("Article Metadata Table:")
    metadata_rows = self.get_article_metadata_head(limit)
    for row in metadata_rows:
      print(row)
    print("\nArticle Ratings Table:")
    ratings_rows = self.get_article_ratings_head(limit)
    for row in ratings_rows:
      print(row)
    print("\nArticle Tags Table:")
    tags_rows = self.get_article_tags_head(limit)
    for row in tags_rows:
      print(row)
    print("\nFile Metadata Table:")
    file_metadata_rows = self.get_file_metadata_head(limit)
    for row in file_metadata_rows:
      print(row)

  def get_unprocessed_articles(self):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT article_id FROM article_tags WHERE processed = 0')
    article_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return article_ids

  def get_article_tags(self, article_id):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT tags FROM article_tags WHERE article_id = ?', (article_id,))
    result = cursor.fetchone()
    if result:
      tag_mask = result[0]
      cursor.execute('SELECT tag FROM tag_labels WHERE (? & (1 << tag_id)) != 0', (tag_mask,))
      tags = [row[0] for row in cursor.fetchall()]
      conn.close()
      return tags
    conn.close()
    return []

  def get_article_metadata_head(self, limit=5):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM article_metadata LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

  def get_article_ratings_head(self, limit=5):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM article_ratings LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

  def get_article_tags_head(self, limit=5):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM article_tags LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

  def get_file_metadata_head(self, limit=5):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM file_metadata LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

  def get_article_index_by_id(self, article_id):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM article_metadata WHERE arxiv_id = ?", (article_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
      return row[0]
    else:
      raise ValueError(f"Article with ID {article_id} not found")

  def get_article_metadata_by_arxiv_id(self, arxiv_id):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM article_metadata WHERE arxiv_id = ?", (arxiv_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
      columns = ['id', 'title', 'arxiv_id', 'url_pdf', 'date_published', 'date_updated', 
             'category_primary', 'category_others', 'authors', 'abstract']
      return dict(zip(columns, row))
    else:
      return None

  def get_article_count(self):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM article_metadata")
    count = cursor.fetchone()[0]
    conn.close()
    return count

  def get_article_ratings(self, article_id):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT ai_rating, ai_reason, user_rating FROM article_ratings WHERE article_id = ?", (article_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
      return {
        'ai_rating': result[0],
        'ai_reason': result[1],
        'user_rating': result[2]
      }
    return None

  def get_connection(self):
    return sqlite3.connect(self.db_name)
  
  def get_all_unique_tags(self):
      with self.get_connection() as conn:
          cursor = conn.cursor()
          cursor.execute('SELECT DISTINCT tag FROM tag_labels')
          return [row[0] for row in cursor.fetchall()]

  def get_articles_list(self, filter_tag=None, show_processed=None, sort_by='ai_rating', show_date_between=(None,None)):
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
      
      showProcessedMap = {
        'a': None,
        'u': 0,
        'r': 1,
        'R': 2,
        'd': 3,
        'D': 4,
        '-': 5,
      }

      # If show_processed is set, filter by processed status
      if showProcessedMap[show_processed] is not None:
        query += 'AND at.processed = ?'
        params.append(showProcessedMap[show_processed])
      
      # Conditionally add date filters
      if show_date_between[0] is not None and show_date_between[0] != '':
          query += 'AND am.date_published >= ?'
          params.append(show_date_between[0])

      if show_date_between[1] is not None and show_date_between[1] != '':
          query += 'AND am.date_published <= ?'
          params.append(show_date_between[1])
          


      # Finish the query by grouping by article id and ordering by the selected column
      query += f'''
      GROUP BY am.id
      ORDER BY {sort_by} DESC
      '''
    
      logging.info(f"Query: \n {query}")
      try:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
      except Exception as e:
        logging.error(f"Failed to fetch articles: {e}")
        logging.error(f"Query: {query}")
        return []

  def get_theme(self):
    try:
      with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT theme FROM settings')
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
      logging.error(f"Failed to fetch theme: {e}")
      return None

  def get_filters_and_sort(self):
    try:
      with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT filter_process, filter_tag, sort_by FROM settings')
        result = cursor.fetchone()
        return result if result else None
    except Exception as e:
      logging.error(f"Failed to fetch filters: {e}")
      return None

  def add_article_metadata(self, overwrite_duplicates=None, **kwargs):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()

    # Determine whether to overwrite duplicates
    overwrite = overwrite_duplicates if overwrite_duplicates is not None else self.overwrite_duplicates

    fields = ['title', 'arxiv_id', 'url_pdf', 'date_published', 'date_updated',
          'category_primary', 'category_others', 'authors', 'abstract']

    present_fields = [field for field in fields if field in kwargs]
    values = []

    for field in present_fields:
      if field in ['date_published', 'date_updated']:
        # Convert date objects to strings
        values.append(kwargs[field].isoformat() if kwargs[field] else None)
      elif field == 'authors' and isinstance(kwargs[field], list):
        values.append(','.join(kwargs[field]))
      elif field == 'category_others' and isinstance(kwargs[field], list):
        values.append(','.join(kwargs[field]))
      else:
        values.append(kwargs[field])

    if overwrite:
      # Use INSERT OR REPLACE to overwrite existing entries
      query = f'''
      INSERT OR REPLACE INTO article_metadata ({', '.join(present_fields)})
      VALUES ({', '.join(['?' for _ in present_fields])})
      '''
    else:
      # Use INSERT OR IGNORE to skip existing entries
      query = f'''
      INSERT OR IGNORE INTO article_metadata ({', '.join(present_fields)})
      VALUES ({', '.join(['?' for _ in present_fields])})
      '''

    cursor.execute(query, values)
    article_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return article_id

  def add_article_rating(self, arxiv_id, **kwargs):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()

    # First, get the article_id from the arxiv_id
    cursor.execute("SELECT id FROM article_metadata WHERE arxiv_id = ?", (arxiv_id,))
    result = cursor.fetchone()
    if not result:
      conn.close()
      raise ValueError(f"Article with ArXiv ID {arxiv_id} not found")
    article_id = result[0]

    fields = ['ai_rating', 'ai_reason', 'user_rating']
    present_fields = ['article_id', 'arxiv_id'] + [field for field in fields if field in kwargs]
    values = [article_id, arxiv_id] + [kwargs[field] for field in fields if field in kwargs]

    query = f'''
    INSERT OR REPLACE INTO article_ratings ({', '.join(present_fields)})
    VALUES ({', '.join(['?' for _ in present_fields])})
    '''

    cursor.execute(query, values)
    conn.commit()
    conn.close()

    print(f"Added rating for arxiv_id: {arxiv_id}, article_id: {article_id}")  # Logging

  def get_connection(self):
    return sqlite3.connect(self.db_name)

  def add_tag(self, tag):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tag_labels (tag) VALUES (?)', (tag,))
    tag_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return tag_id
  
  def add_article_tag(self, article_id, tags):
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    tag_mask = 0
    for tag in tags:
      cursor.execute('SELECT tag_id FROM tag_labels WHERE tag = ?', (tag,))
      result = cursor.fetchone()
      # If the tag exists, add it to the tag_mask
      if result:
        tag_mask |= (1 << result[0])
      # If the tag does not exist, add it to the tag_labels table
      else:
        tag_id = self.add_tag(tag)
        tag_mask |= (1 << tag_id)
    
    # If article_id already exists in article_tags, update the tags, otherwise insert a new row
    cursor.execute('INSERT OR IGNORE INTO article_tags (article_id, tags) VALUES (?, ?)', (article_id, tag_mask))
    cursor.execute('UPDATE article_tags SET tags = ? WHERE article_id = ?', (tag_mask, article_id))
    conn.commit()
    conn.close()

  def add_full_article(self, metadata, ratings, tags, overwrite_duplicates=None):
    article_id = self.add_article_metadata(overwrite_duplicates=overwrite_duplicates, **metadata)
    if article_id:
      self.add_article_rating(article_id, **ratings)
      for tag, tag_type in tags:
        self.add_article_tag(article_id, tag, tag_type)
      print(f"Full article data added successfully with ID {article_id}")
    else:
      print("Article not added (likely due to existing entry and no overwrite)")
    return article_id
  
  def add_article_from_MD(self, filepath):
    try:
      article_dict = WWArticles.readMarkdownFile2Dict(filepath)
      # Add article metadata
      article_id = self.add_article_metadata(
        title=article_dict["title"],
        arxiv_id=article_dict["arxiv_id"],
        url_pdf=article_dict["url_pdf"],
        date_published=article_dict["date_published"],
        date_updated=article_dict["date_updated"],
        category_primary=article_dict["category_primary"],
        category_others=article_dict["category_others"],
        authors=article_dict["authors"],
        abstract=article_dict["abstract"]
      )
      self.add_article_tag(article_id, article_dict["config_tags"])
      # Add AI rating if available
      if "ai_rating" in article_dict and "ai_reason" in article_dict:
        self.add_article_rating(
          arxiv_id=article_dict["arxiv_id"],
          ai_rating=article_dict["ai_rating"],
          ai_reason=article_dict["ai_reason"]
        )
      # Add file modified time
      self.add_file_modified_time(filepath)
      logging.debug(f"Successfully loaded article: {article_dict['title']}")
    except Exception as e:
      logging.error(f"Failed to load article {filepath}: {e}")
  
  def add_articles_from_directory(self, directory):
    list_filenames = [
      filename
      for filename in os.listdir(directory)
      if filename.endswith(".md")
    ]

    for filename in list_filenames:
      filepath = WWFnFs.contstructPath(directory, filename)
      self.add_article_from_MD(filepath)

  def set_filters_and_sort(self, filter_process=None, filter_tag=None, sort_by=None):
    logging.info("Setting filters and sort")
    with self.get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute('SELECT * FROM settings')
      result = cursor.fetchone()
      if result:
        cursor.execute('UPDATE settings SET filter_process = ?, filter_tag = ?, sort_by = ?', (filter_process, filter_tag, sort_by))
      else:
        cursor.execute('INSERT INTO settings (filter_process, filter_tag, sort_by, key) VALUES (?, ?, ?)', (filter_process, filter_tag, sort_by, 0))
      conn.commit()
      logging.info("Filters and sort set successfully")

  def check_modified(self, filepath):
    try:
      arxiv_id = os.path.splitext(os.path.basename(filepath))[0]
      logging.debug(f"Checking modification for {arxiv_id}")
      try:
        article_id = self.get_article_index_by_id(arxiv_id)
      except ValueError:
        logging.debug(f"Article ID not found for {arxiv_id}")
        return True
      logging.debug(f"Article ID: {article_id}")

      article_id = self.get_article_index_by_id(arxiv_id)
      
      # Get the last modified time of the file
      file_modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
      logging.debug(f"File modified time: {file_modified_time}")
      conn = sqlite3.connect(self.db_name)
      logging.debug("Connected to database")
      cursor = conn.cursor()
      cursor.execute('SELECT last_updated FROM file_metadata WHERE article_id = ?', (article_id,))
      result = cursor.fetchone()
      logging.debug(f"Result: {result}")
      conn.close()
      
      if result:
        db_last_updated = datetime.fromisoformat(result[0])
        return file_modified_time > db_last_updated
      else:
        logging.debug("No record found")
        return True  # If no record exists, consider it as modified
    except Exception as e:
      logging.error(f"Failed to check modification for {filepath}: {e}")
      return False

  def add_file_modified_time(self, filepaths):
    if isinstance(filepaths, str):
      filepaths = [filepaths]
    
    for filepath in filepaths:
      try:
        arxiv_id = os.path.splitext(os.path.basename(filepath))[0]
        article_id = self.get_article_index_by_id(arxiv_id)
        
        # Get the last modified time of the file
        file_modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
          INSERT OR REPLACE INTO file_metadata (article_id, last_updated)
          VALUES (?, ?)
        ''', (article_id, file_modified_time.isoformat()))
        conn.commit()
        conn.close()
        print(f"File modified time for article ID {article_id} updated successfully.")
      except Exception as e:
        print(f"Failed to add file modified time for {filepath}: {e}")

  def find_modified_articles(self, directory):
    logging.info("Finding modified articles")
    modified_articles = []
    list_filenames = [
      filename
      for filename in os.listdir(directory)
      if filename.endswith(".md")
    ]

    for filename in list_filenames:
      filepath = WWFnFs.contstructPath(directory, filename)
      logging.debug(f"Checking file: {filepath}")

      if self.check_modified(filepath):
        modified_articles.append(filepath)
    
    return modified_articles # List of filepaths

  def clean_up_file_metadata(self, directory):
    # This function removes entries for articles that no longer have a 
    # corresponding file from every table, including tags.
    conn = sqlite3.connect(self.db_name)
    cursor = conn.cursor()
    
    cursor.execute('SELECT article_id FROM file_metadata')
    article_ids = [row[0] for row in cursor.fetchall()]
    
    for article_id in article_ids:
      cursor.execute('SELECT arxiv_id FROM article_metadata WHERE id = ?', (article_id,))
      result = cursor.fetchone()
      if result:
        arxiv_id = result[0]
        filepath = WWFnFs.contstructPath(directory, f"{arxiv_id}.md")
        if not os.path.exists(filepath):
          # Delete from file_metadata
          cursor.execute('DELETE FROM file_metadata WHERE article_id = ?', (article_id,))
          # Delete from article_metadata
          cursor.execute('DELETE FROM article_metadata WHERE id = ?', (article_id,))
          # Delete from article_ratings
          cursor.execute('DELETE FROM article_ratings WHERE article_id = ?', (article_id,))
          # Delete from tags
          cursor.execute('DELETE FROM article_tags WHERE article_id = ?', (article_id,))
          logging.info(f"Removed stale entries for article ID {article_id} from all tables")
    
    conn.commit()
    conn.close()

# Example usage
if __name__ == "__main__":
  db = ArticleDatabase()
  # db.add_articles_from_directory("articles")

  # Print the head of each table
  db.display_table_heads()
  modified_articles = db.find_modified_articles("articles")
  print(f"Found {len(modified_articles)} modified articles:")
  for article in modified_articles:
    print(article)

  # Update the file modified time for the modified articles
  db.add_file_modified_time(modified_articles)

  # Now verify that the modified articles are no longer detected as modified
  modified_articles = db.find_modified_articles("articles")
  print(f"Found {len(modified_articles)} after update")

  #  Clean up file metadata
  db.clean_up_file_metadata("articles")
  


  # db.create_database()

  # Adding a full article
  # metadata = {
  #     'title': "Example Article",
  #     'arxiv_id': "1234.56789",
  #     'url_pdf': "https://example.com/article.pdf",
  #     'date_published': datetime.now().date(),
  #     'date_updated': datetime.now().date(),
  #     'category_primary': "Computer Science",
  #     'category_others': "Artificial Intelligence",
  #     'authors': ["John Doe", "Jane Smith"],
  #     'abstract': "This is an example abstract."
  # }
  # ratings = {
  #     'ai_rating': 4.5,
  #     'ai_reason': "Well-structured and innovative",
  #     'user_rating': 5
  # }
  # tags = [
  #     ("machine learning", "config_tag"),
  #     ("neural networks", "config_tag"),
  #     ("novel approach", "config_reason_FSOC"),
  #     ("significant results", "config_reason_FSOC")
  # ]

  # db.add_full_article(metadata, ratings, tags)

  # Adding partial data
  # partial_metadata = {
  #     'title': "Partial Article",
  #     'arxiv_id': "9876.54321",
  #     'category_primary': "Physics"
  # }
  # partial_article_id = db.add_article_metadata(**partial_metadata)
  # db.add_article_rating(partial_article_id, ai_rating=3.8)
  # db.add_article_tag(partial_article_id, "quantum computing", "config_tag")
  # print("Partial article data added successfully")

  # print("\nDisplaying the head of each table:")
  # db.display_table_heads()

  # print("\nListing column titles for each table:")
  # table_columns = db.list_table_columns()
  # print(table_columns)

  # Get article metadata by index
  # article_index = 4
  # article_metadata = db.get_article_metadata_by_index(article_index)
  # print(f"\nArticle Metadata by Index {article_index}:")
  # for key, value in article_metadata.items():
  #     print(f"{key}: {value}")
  # # Get article tags
  # article_tags = db.get_article_tags(article_index)
  # print(f"\nArticle Tags for Article ID {article_index}:")
  # for tag in article_tags:
  #     print(tag)

