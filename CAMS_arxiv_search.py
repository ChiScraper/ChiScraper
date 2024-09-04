#!/usr/bin/env python3


## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, time, arxiv
import datetime as dt
import numpy as np
from unidecode import unidecode
from MyLibrary import HelperFuncs


## ###############################################################
## SEARCH PARAMETERS
## ###############################################################
## search configuration
CONFIG_FILENAME      = "FSOC" # excluding the .json extension
START_DATE           = HelperFuncs.getDateNDaysAgo(14)
BOOL_SEARCH_TITLE    = 1
BOOL_SEARCH_ABSTRACT = 1
BOOL_SEARCH_AUTHORS  = 0

## output options
DIRECTORY_OUTPUT = "./articles"
BOOL_SAVE_ARTICLES  = 1
BOOL_PRINT_ARTICLES = 0


## ###############################################################
## OPERATOR CLASS
## ###############################################################
class ArxivScraper:
  def __init__(
      self,
      start_date, end_date,
      bool_search_title    = True,
      bool_search_abstract = True,
      bool_search_authors  = True
    ):
    self.start_date           = start_date
    self.end_date             = end_date
    self.bool_search_title    = bool_search_title
    self.bool_search_abstract = bool_search_abstract
    self.bool_search_authors  = bool_search_authors
    self.client = arxiv.Client(
      page_size     = 200,
      delay_seconds = 1,
      num_retries   = 100
    )

  def search(self, dict_search):
    self.list_articles = []
    for search_category in dict_search["list_categories"]:
      HelperFuncs.printToTerminal(f"Searching: {search_category}")
      HelperFuncs.printToTerminal(f"Date range: {HelperFuncs.getDateString(self.start_date)} to {HelperFuncs.getDateString(self.end_date)}")
      HelperFuncs.printToTerminal("Progress: ", end="")
      num_saved = 0
      num_looked_at = 0
      for article in self.client.results(self._createSearchQuery(search_category)):
        num_looked_at += 1
        self._displayProgress(num_looked_at)
        if not(self._isWithinDateRange(article)): break
        if self._isDuplicate(article, self.list_articles): continue
        if self._meetsCondition(article, dict_search):
          self.list_articles.append(article)
          num_saved += 1
      HelperFuncs.printToTerminal(f"\nFound {num_saved} useful files from the {num_looked_at} looked at.\n")

  def getSortedArticles(self):
    return sorted(
      self.list_articles,
      key     = lambda article: article.updated,
      reverse = True
    )

  def _createSearchQuery(self, category):
    return arxiv.Search(
      query       = category,
      max_results = float(np.inf),
      sort_by     = arxiv.SortCriterion.SubmittedDate
    )

  def _isWithinDateRange(self, article):
    date_published = HelperFuncs.getArticleDate(article)
    return (self.start_date.date() <= date_published.date()) and (date_published.date() <= self.end_date.date())

  def _isDuplicate(self, article, list_articles):
    return any(
      stored_article.title == article.title
      for stored_article in list_articles
    )

  def _meetsCondition(self, article, dict_search):
    bool_satisfied_title    = True
    bool_satisfied_abstract = True
    bool_satisfied_authors  = True
    if self.bool_search_title:
      if HelperFuncs.containsAnyKeyword(article.title.lower(), dict_search["list_keywords_exclude"]): return False
      bool_satisfied_title = HelperFuncs.containsAnyKeyword(article.title.lower(), dict_search["list_keywords_include"])
    if self.bool_search_abstract:
      if HelperFuncs.containsAnyKeyword(article.summary.lower(), dict_search["list_keywords_exclude"]): return False
      bool_satisfied_abstract = HelperFuncs.containsAnyKeyword(article.summary.lower(), dict_search["list_keywords_include"])
    if self.bool_search_authors:
      list_author_lastnames = [
        unidecode(str(author).lower().split(" ")[-1])
        for author in article.authors
      ]
      bool_satisfied_authors = any(
        author.lower() in list_author_lastnames
        for author in dict_search["list_authors"]
      )
    return (bool_satisfied_title or bool_satisfied_abstract) and bool_satisfied_authors

  def _displayProgress(self, num_looked_at):
    if (num_looked_at % 10) == 0: HelperFuncs.printToTerminal("x", end="")
    if (num_looked_at % 50) == 0: HelperFuncs.printToTerminal(" ", end="")


## ###############################################################
## MAIN PROGRAM
## ###############################################################
def main():
  HelperFuncs.createFolder(DIRECTORY_OUTPUT)
  end_date = HelperFuncs.getDateToday()
  if (end_date.date() - START_DATE.date()).days < 1:
    raise ValueError(
      "Error: invalid date range: the final date ({}) must be at least one day after the start date ({}). ".format(end_date, START_DATE),
      "Please ensure that the final date is the same or later than the start date."
    )
  time_start  = time.time()
  dict_search = HelperFuncs.readSearchCriteria(CONFIG_FILENAME)
  config_tag  = "#{}".format(dict_search["config_tag"])
  HelperFuncs.printToTerminal(f"Searching for articles:")
  HelperFuncs.printToTerminal("\t> from: {}".format(HelperFuncs.getDateString(START_DATE)))
  HelperFuncs.printToTerminal("\t> to:   {}".format(HelperFuncs.getDateString(end_date)))
  HelperFuncs.printToTerminal(f"\t> using the {config_tag} config file")
  HelperFuncs.printToTerminal("Started executing at: {}".format(dt.datetime.now().strftime("%H:%M:%S")))
  HelperFuncs.printToTerminal(" ")
  obj_scraper = ArxivScraper(
    start_date           = START_DATE,
    end_date             = end_date,
    bool_search_title    = BOOL_SEARCH_TITLE,
    bool_search_abstract = BOOL_SEARCH_ABSTRACT,
    bool_search_authors  = BOOL_SEARCH_AUTHORS
  )
  obj_scraper.search(dict_search)
  list_articles = obj_scraper.getSortedArticles()
  HelperFuncs.printToTerminal(f"Found a total of {len(list_articles)} articles.")
  HelperFuncs.printToTerminal(f"Saving articles to: {DIRECTORY_OUTPUT}")
  num_articles = len(list_articles)
  for article_index, article in enumerate(list_articles):
    if BOOL_PRINT_ARTICLES:
      HelperFuncs.printToTerminal(f"({article_index+1}/{num_articles})")
      HelperFuncs.printArticle(article)
    if BOOL_SAVE_ARTICLES:
      HelperFuncs.saveArticle(
        article          = article,
        directory_output = DIRECTORY_OUTPUT,
        config_tag       = config_tag
      )
  time_elapsed = time.time() - time_start
  HelperFuncs.printToTerminal(" ")
  HelperFuncs.printToTerminal(f"Elapsed time: {time_elapsed:.2f} seconds.")


## ###############################################################
## RUN PROGRAM
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit()


## END OF PROGRAM
