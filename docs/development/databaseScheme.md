# Article Database Documentation

## Database Tables Overview

| Table Name | Purpose | Key Fields |
|------------|---------|------------|
| `article_metadata` | Stores core article information | `id`, `arxiv_id`, `title`, `abstract` |
| `article_ratings` | Tracks AI and user ratings | `article_id`, `ai_rating`, `user_rating` |
| `tag_labels` | Maintains tag dictionary | `tag_id`, `tag` |
| `article_tags` | Links articles to tags | `article_id`, `tags`, `processed` |
| `file_metadata` | Tracks file modifications | `article_id`, `last_updated` |

## Detailed Table Schemas

### 1. article_metadata
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique identifier |
| `title` | TEXT | NOT NULL | Article title |
| `arxiv_id` | TEXT | UNIQUE NOT NULL | ArXiv paper ID |
| `url_pdf` | TEXT | | PDF URL |
| `date_published` | DATE | | Publication date |
| `date_updated` | DATE | | Last update date |
| `category_primary` | TEXT | | Primary arXiv category |
| `category_others` | TEXT | | Additional categories |
| `authors` | TEXT | | Comma-separated author list |
| `abstract` | TEXT | | Article abstract |

### 2. article_ratings
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Unique identifier |
| `article_id` | INTEGER | UNIQUE, FOREIGN KEY | Reference to article_metadata |
| `arxiv_id` | INTEGER | | ArXiv ID reference |
| `ai_rating` | REAL | | AI-generated rating |
| `ai_reason` | TEXT | | Explanation for AI rating |
| `user_rating` | INTEGER | | User-provided rating |

### 3. tag_labels
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `tag_id` | INTEGER | PRIMARY KEY | Unique identifier |
| `tag` | TEXT | NOT NULL UNIQUE | Tag name |

### 4. article_tags
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `article_id` | INTEGER | PRIMARY KEY, FOREIGN KEY | Reference to article_metadata |
| `tags` | INTEGER | NOT NULL | Bitwise storage of tags |
| `processed` | INTEGER | DEFAULT 0 | Processing status flag |

### 5. file_metadata
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `article_id` | INTEGER | PRIMARY KEY, FOREIGN KEY | Reference to article_metadata |
| `last_updated` | DATETIME | | Last file modification time |


# B. Using the Database Methods

### 1. Database Initialization
```python
from article_database import ArticleDatabase

# Create new database or connect to existing
db = ArticleDatabase(db_name='articles.db')

# Create fresh database (deletes existing)
db = ArticleDatabase(db_name='articles.db', start_fresh=True)
```

### 2. Adding Articles

#### Single Article Metadata
```python
article_id = db.add_article_metadata(
    title="Understanding Attention Mechanisms",
    arxiv_id="2310.12345",
    url_pdf="https://arxiv.org/pdf/2310.12345.pdf",
    date_published="2023-10-15",
    date_updated="2023-10-16",
    category_primary="cs.AI",
    category_others=["cs.LG", "cs.CL"],
    authors=["John Doe", "Jane Smith"],
    abstract="This paper explores..."
)
```

#### Adding Ratings
```python
db.add_article_rating(
    arxiv_id="2310.12345",
    ai_rating=4.5,
    ai_reason="Novel approach with strong empirical results",
    user_rating=5
)
```

#### Adding Tags
```python
# Add new tag
tag_id = db.add_tag("transformer")

# Add tags to article
db.add_article_tag(article_id, ["transformer", "attention", "neural-networks"])
```

### 3. Loading from Markdown Files
```python
# Load single article from markdown
db.add_article_from_MD("path/to/article.md")

# Load entire directory of markdown files
db.add_articles_from_directory("path/to/articles/")
```

### 4. Querying Articles

#### Get Article Metadata
```python
# Get by ArXiv ID
metadata = db.get_article_metadata_by_arxiv_id("2310.12345")

# Get article count
count = db.get_article_count()
```

#### Get Ratings and Tags
```python
# Get ratings
ratings = db.get_article_ratings(article_id)

# Get tags for article
tags = db.get_article_tags(article_id)

# Find articles with specific tag
articles = db.find_articles_with_tag("transformer")
```

## C. Additional Features

### 1. File Modification Tracking
```python
# Check if articles have been modified
modified = db.check_modified("path/to/article.md")

# Find all modified articles in directory
modified_articles = db.find_modified_articles("path/to/articles/")

# Update file modification time
db.add_file_modified_time("path/to/article.md")
```

### 2. Database Maintenance
```python
# Clean up stale entries
db.clean_up_file_metadata("path/to/articles/")

# Display database structure
db.list_table_columns()

# View sample data
db.display_table_heads(limit=5)
```

### 3. Bitwise Tag Operations
The system uses bitwise operations for efficient tag storage:
```python
# Add tags
db.update_article_tags(article_id, add_tags=["transformer", "attention"])

# Remove tags
db.update_article_tags(article_id, remove_tags=["attention"])
```

### 4. Unprocessed Articles Management
```python
# Get articles pending processing
unprocessed = db.get_unprocessed_articles()

# Find articles without ratings
unranked = db.find_unranked_articles()
```

### 5. Important Notes
- The database uses SQLite for storage
- ArXiv IDs must be unique
- Tag operations use bitwise storage for efficiency
- File modification tracking helps maintain synchronization with markdown files
- The system supports both AI and user ratings
- Authors and category_others are stored as comma-separated strings
- All database operations are automatically committed