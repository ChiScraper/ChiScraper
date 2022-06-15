#!/usr/bin/env python3

## arXiv scraper: search with criteria through categories
## Author: Neco Kriel 2022

import os, sys
import arxiv
import numpy as np
import datetime as dt

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
    print("SUCCESS: Folder created. \n\t" + filepath + "\n")
  else: print("WARNING: Folder already exists (folder not created). \n\t" + filepath + "\n")

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

def printArticleInfo(article):
  ## helper print function
  def printLine(name, content):
    print("{}{}".format( name.ljust(20), content ))
  ## extract lists
  list_other_categories = [
    elem for elem in article.categories
    if (elem != article.primary_category)
  ]
  list_authors = [ str(author) for author in article.authors ]
  ## print article information
  printLine("arXiv URL:",        article.entry_id)
  printLine("Title:",            article.title)
  printLine("Date published:",   article.published)
  printLine("Primary category:", article.primary_category)
  printLine("Other categories:", ", ".join( list_other_categories ))
  printLine("Author(s)",         ", ".join( list_authors ))
  print(" ")

def saveArticleInfo(file, article):
  ## helper write function
  def writeLine(file, name, content):
    file.write("{}{}\n".format( name.ljust(20), content ))
  ## extract lists
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
  writeLine(file, "Other categories:", ", ".join( list_other_categories))
  writeLine(file, "Author(s)",         ", ".join( list_authors ))
  file.write("Abstract:\n")
  file.write(article.summary)
  file.write("\n\n")


## ###############################################################
## MAIN PROGRAM
## ###############################################################
BOOL_PRINT           = 1
BOOL_SAVE            = 1
DATE_END             = getDateToday()
DATE_START           = getDateNDaysAgo(30)
NUM_ARTICLES         = float(np.inf)
FILEPATH_BASE        = os.getcwd()
SUBFOLDER_OUTPUT     = "output"
FILENAME_OUTPUT      = f"arxiv_{DATE_START}_{DATE_END}.txt"
BOOL_SEARCH_TITLE    = 1
BOOL_SEARCH_ABSTRACT = 0
BOOL_SEARCH_AUTHORS  = 0
LIST_CATEGORIES      = [
  "astro-ph.HE", "astro-ph.GA", "astro-ph.SR", # astrophysics
  "astro-ph.IM",                               # method papers
  "physics.flu-dyn", "physics.plasm-ph",       # fluid physics
]
LIST_KEYWORDS = [
  "turbulen", # covers: "turbulence", "turbulent"
  "magneti",  # covers: "magnetic", "magnetism", "magnetized"
  "dynamo",
  "magnetohydrodynamic", "mhd"
]
LIST_AUTHORS = [
  "schekochihin", "federrath", "krumholz", "beattie", "sampson", "seta"
]

def main():
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
      if (DATE_START <= date_published) and (date_published <= DATE_END):
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
          list_articles.append(article) # store article
      else: break # break out of loop: because articles are ordered by date
  print(" ")
  if BOOL_PRINT:
    print(f"{len(list_articles)} articles found:")
    ## print articles to terminal
    for article_index, article in enumerate(list_articles):
      print(f"({article_index+1})")
      printArticleInfo(article)
  if BOOL_SAVE:
    ## create output directory
    filepath_output = f"{FILEPATH_BASE}/{SUBFOLDER_OUTPUT}"
    filepath_file   = f"{filepath_output}/{FILENAME_OUTPUT}"
    createFolder(filepath_output)
    ## save articles to file
    with open(filepath_file, "w") as txt_file:
      for article_index, article in enumerate(list_articles):
        txt_file.write(f"({article_index+1})\n")
        saveArticleInfo(txt_file, article)
    print("Saved:", filepath_file)



## ###############################################################
## RUN PROGRAM
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit()


## END OF PROGRAM