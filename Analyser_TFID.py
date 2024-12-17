## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, time, datetime, re, os
import logging

from src.headers import Directories
from src.headers import FileNames
from src.headers import IO
from src.headers import WWFnFs
from src.headers import WWDates
from src.headers import WWArgParse
from src.headers import WWArticles
from src.headers import WWDatabase

from src.scripts import search_arxiv as SearchArxiv
from src.scripts import score_article as ScoreArticle
from src.scripts import fetch_from_arxiv as FetchFromArxiv
from src.scripts import download_articles as DownloadArticles
from src.scripts import launch_webapp as WebApp


import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer

## ###############################################################



# Define a function to preprocess the text
def preprocess_text(articleTuple):
    title = articleTuple[1]
    abstract = articleTuple[9]
    text = title + ' ' + abstract
    # Remove punctuation and convert to lowercase
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text.lower())
    return text

# Get the database
dbPath = 'articles.db'
db = WWDatabase.ArticleDatabase(dbPath)

filter_tag = None
show_processed = 'R'
sort_by = 'date'
published_after = None
published_before = None


articles = db.get_articles_list(
    show_processed=show_processed,
)


textsList = [preprocess_text(article) for article in articles]

# Create the vectorizer
tfidf_vectorizer = TfidfVectorizer()



# Fit and transform the texts to get the TF-IDF matrix
tfidf_matrix = tfidf_vectorizer.fit_transform(textsList)

# Get the feature names (words) from the vectorizer
feature_names = tfidf_vectorizer.get_feature_names_out()

# Sort the terms by their TF-IDF scores in descending order
sorted_terms = sorted(zip(tfidf_vectorizer.idf_, feature_names), reverse=True)

# Print the top N terms with their TF-IDF scores
top_n = 20
for term_score, term in sorted_terms[:top_n]:
    print(f"{term}: {term_score:.4f}")
