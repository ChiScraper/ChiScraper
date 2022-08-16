#!/usr/bin/env python3

## arXiv scraper: search with criteria through categories
## Author: Neco Kriel 2022

import os, sys, time
import arxiv
import numpy as np
import datetime as dt

os.system("clear")

''' arXiv result properties:
  - entry_id:         A url http://arxiv.org/abs/{id}.
  - pdf_url:          A URL for the result's PDF if present.
  - doi:              A URL for the resolved DOI to an external resource if present.
  - published:        When the result was originally published.
  - updated:          When the result was last updated.
  - primary_category: The result's primary arXiv category.
  - categories:       All of the result's categories.
  - title:            The title of the result.
  - authors:          The result's authors, as arxiv.Authors.
  - summary:          The result abstract.
  - comment:          The authors' comment if present.
  - journal_ref:      A journal reference if present.
  - links:            Up to three URLs associated with this result, as arxiv.Links.
'''


## ###############################################################
## HELPER FUNCTIONS
## ###############################################################
def createFolder(filepath):
  if not(os.path.exists(filepath)):
    os.makedirs(filepath)
    print("Successfully created folder:")
    print(f"\t{filepath}\n")

def getDateToday():
  date      = dt.datetime.now()
  str_year  = str(date.year ).zfill(4)
  str_month = str(date.month).zfill(2)
  str_day   = str(date.day  ).zfill(2)
  return f"{str_year}-{str_month}-{str_day}"

def getDateNDaysAgo(num_days):
  date_today = dt.datetime.now()
  date_delta = dt.timedelta(days=num_days)
  date_num_days_ago = date_today - date_delta
  str_year  = str(date_num_days_ago.year ).zfill(4)
  str_month = str(date_num_days_ago.month).zfill(2)
  str_day   = str(date_num_days_ago.day  ).zfill(2)
  return f"{str_year}-{str_month}-{str_day}"

def getArticleDate(article):
  date      = article.published
  str_year  = str(date.year ).zfill(4)
  str_month = str(date.month).zfill(2)
  str_day   = str(date.day  ).zfill(2)
  return f"{str_year}-{str_month}-{str_day}"

def allKeywordsInPhrase(phrase, list_search_terms):
  list_bools = []
  for term in list_search_terms:
    if type(term) is str:
      term_bool = (term in phrase)
      list_bools.append(term_bool)
    elif type(term) is list:
      list_bools.append(
        anyKeywordsInPhrase(phrase, term)
      )
  return all(list_bools)

def anyKeywordsInPhrase(phrase, list_search_terms):
  list_bools = []
  for term in list_search_terms:
    if type(term) is str:
      term_bool = (term in phrase)
      list_bools.append(term_bool)
      if term_bool: break
    elif type(term) is list:
      list_bools.append(
        allKeywordsInPhrase(phrase, term)
      )
  return any(list_bools)

def printArticleInfo(article, bool_verbose=False):
  ## helper print function
  def printLine(name, content):
    print(f"{name.ljust(20)} {content}\n")
  ## remove primary category from list of other categories
  list_other_categories = [
    elem for elem in article.categories
    if (elem != article.primary_category)
  ]
  list_authors = [ str(author) for author in article.authors ]
  ## print article information
  printLine("arXiv URL:",        article.entry_id)
  printLine("Title:",            article.title)
  if bool_verbose: printLine("Date published:",   article.published)
  if bool_verbose: printLine("Primary category:", article.primary_category)
  if bool_verbose: printLine("Other categories:", ", ".join( list_other_categories ))
  printLine("Author(s)",         ", ".join( list_authors ))
  print(" ")

def saveArticleInfo(file, article):
  ## helper write function
  def writeLine(file, name, content):
    file.write(f"{name.ljust(20)} {content}\n")
  ## remove primary category from list of other categories
  list_other_categories = [
    elem for elem in article.categories
    if (elem != article.primary_category)
  ]
  list_authors = [ str(author) for author in article.authors ]
  ## save article information
  writeLine(file, "arXiv URL:",        article.entry_id)
  writeLine(file, "PDF URL:",          article.pdf_url)
  writeLine(file, "Title:",            article.title)
  writeLine(file, "Date published:",   article.published)
  writeLine(file, "Date updated:",     article.updated)
  writeLine(file, "Primary category:", article.primary_category)
  writeLine(file, "Other categories:", ", ".join( list_other_categories ))
  writeLine(file, "Author(s)",         ", ".join( list_authors ))
  file.write("Abstract:\n")
  file.write(article.summary)
  file.write("\n\n")


## ###############################################################
## MAIN PROGRAM
## ###############################################################
DATE_START           = getDateNDaysAgo(31 * 6) # approx 6 months ago
DATE_FINAL           = getDateToday()
NUM_ARTICLES         = float(np.inf)
BOOL_PRINT           = 1
BOOL_PRINT_VERBOSE   = 1
BOOL_SAVE            = 1
BOOL_SEARCH_TITLE    = 1
BOOL_SEARCH_ABSTRACT = 0
BOOL_SEARCH_AUTHORS  = 0
LIST_CATEGORIES = [
  # "astro-ph.HE", "astro-ph.GA", "astro-ph.SR", # astrophysics
  # "astro-ph.IM",                               # method papers
  "physics.flu-dyn", "physics.plasm-ph",       # fluid physics
]
LIST_AUTHORS = [
  "schekochihin", "federrath", "krumholz", "beattie", "seta", "sampson"
]
LIST_KEYWORDS = [
  # "turbulen", # covers: "turbulence", "turbulent"
  # "magneti",  # covers: "magnetic", "magnetism", "magnetized"
  "dynamo",
  "magnetohydrodynamic", "mhd",
  "galactic wind"
]
LIST_KEYWORDS_GROUPED = [
  [ "cloud", [ "survival", "wind", "shock", "launch"] ],
  [ "starburst", "outflows" ]
]

def main():
  time_start = time.time()
  ## initialise list of articles
  list_articles = []
  ## search different categories
  for search_category in LIST_CATEGORIES:
    print("Searching:", search_category)
    ## create search generator to fetch all available articles in category
    search = arxiv.Search(
      query       = search_category,
      max_results = NUM_ARTICLES,
      sort_by     = arxiv.SortCriterion.SubmittedDate
    )
    ## loop through articles
    for article in search.results():
      ## check if the article was published within the desired date-range
      date_published = getArticleDate(article)
      if (DATE_START <= date_published) and (date_published <= DATE_FINAL):
        ## don't look at the article if it has appeared before
        if any(
            stored_article.title == article.title
            for stored_article in list_articles
          ):
          continue
        ## check if one of the keywords appears in the title / abstract
        bool_keywords_title = BOOL_SEARCH_TITLE and any(
          keyword in article.title.lower()
          for keyword in LIST_KEYWORDS
        )
        bool_keywords_abstract = BOOL_SEARCH_ABSTRACT and any(
          keyword in article.summary.lower()
          for keyword in LIST_KEYWORDS
        )
        ## check if one of the authors appear on the article
        list_article_authors = [
          str(author).lower().split(" ")[-1] # grab the author's last name
          for author in article.authors
        ]
        bool_authors = BOOL_SEARCH_AUTHORS and any(
          author in list_article_authors
          for author in LIST_AUTHORS
        )
        ## if any of the criteria are satisfied
        if (bool_keywords_title or bool_keywords_abstract) or bool_authors:
          list_articles.append(article)
      else: break # break out of loop: because articles are ordered by date
  print(" ")
  if BOOL_PRINT:
    print(f"{len(list_articles)} articles found:")
    ## print articles to terminal
    for article_index, article in enumerate(list_articles):
      print(f"({article_index+1})")
      printArticleInfo(article, BOOL_PRINT_VERBOSE)
  if BOOL_SAVE:
    ## create output directory
    filepath_base = os.path.dirname(os.path.realpath(__file__))
    filename_file = f"arxiv {DATE_FINAL} to {DATE_START} (test).txt"
    filepath_output_folder = f"{filepath_base}/output"
    filepath_output_file   = f"{filepath_output_folder}/{filename_file}"
    createFolder(filepath_output_folder)
    ## save articles to file
    with open(filepath_output_file, "w") as txt_file:
      for article_index, article in enumerate(list_articles):
        txt_file.write(f"({article_index+1})\n")
        saveArticleInfo(txt_file, article)
    print("Saved:", filepath_output_file)
    time_elapsed = time.time() - time_start
    print(f"Elapsed time: {time_elapsed:.2f} seconds.")



## ###############################################################
## RUN PROGRAM
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit()


## END OF PROGRAM