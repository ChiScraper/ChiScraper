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
OUTPUT_DIRECTORY     = "/Users/necoturb/Library/CloudStorage/OneDrive-Personal/Obsidian/arXiv-articles"
BOOL_SAVE_ARTICLES   = 1
BOOL_PRINT_ARTICLES  = 0
CONFIG_DIRECTORY     = "./configs"
CONFIG_FILENAME      = "dynamo" # excluding the .json extension
START_DATE           = HelperFuncs.getDateNDaysAgo(14)
BOOL_SEARCH_TITLE    = 1
BOOL_SEARCH_ABSTRACT = 1
BOOL_SEARCH_AUTHORS  = 0


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
    self.list_results = []
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
        if self._isDuplicate(article, self.list_results): continue
        bool_result, list_config_reason = self._checkConditions(article, dict_search)
        if bool_result:
          self.list_results.append({
            "article" : article,
            "list_config_reason" : [
              "1" if _bool else "0"
              for _bool in list_config_reason
            ]
          })
          num_saved += 1
      HelperFuncs.printToTerminal(f"\nFound {num_saved} useful files from the {num_looked_at} looked at.\n")

  def getSortedArticles(self):
    return sorted(
      self.list_results,
      key     = lambda result: result["article"].updated,
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

  def _isDuplicate(self, article, list_results):
    this_title = article.title.lower()
    return any(
      this_title == result["article"].title.lower()
      for result in list_results
    )

  def _checkConditions(self, article, dict_search):
    bool_satisfied_title    = False
    bool_satisfied_abstract = False
    bool_satisfied_authors  = False
    if self.bool_search_title:
      if HelperFuncs.meetsSearchCriteria(article.title.lower(), dict_search["list_keywords_exclude"]): return False, None
      bool_satisfied_title = HelperFuncs.meetsSearchCriteria(article.title.lower(), dict_search["list_keywords_include"])
    if self.bool_search_abstract:
      if HelperFuncs.meetsSearchCriteria(article.summary.lower(), dict_search["list_keywords_exclude"]): return False, None
      bool_satisfied_abstract = HelperFuncs.meetsSearchCriteria(article.summary.lower(), dict_search["list_keywords_include"])
    if self.bool_search_authors:
      list_author_lastnames = [
        unidecode(str(author).lower().split(" ")[-1])
        for author in article.authors
      ]
      bool_satisfied_authors = any(
        author.lower() in list_author_lastnames
        for author in dict_search["list_authors"]
      )
    list_config_reason = [
      bool_satisfied_title,
      bool_satisfied_abstract,
      bool_satisfied_authors
    ]
    return any(list_config_reason), list_config_reason

  def _displayProgress(self, num_looked_at):
    if (num_looked_at % 10) == 0: HelperFuncs.printToTerminal("x", end="")
    if (num_looked_at % 50) == 0: HelperFuncs.printToTerminal(" ", end="")


## ###############################################################
## MAIN PROGRAM
## ###############################################################
def main():
  HelperFuncs.createFolder(OUTPUT_DIRECTORY)
  end_date = HelperFuncs.getDateToday()
  if (end_date.date() - START_DATE.date()).days < 1:
    raise ValueError(
      "Error: invalid date range: the final date ({}) must be at least one day after the start date ({}). ".format(end_date, START_DATE),
      "Please ensure that the final date is the same or later than the start date."
    )
  time_start  = time.time()
  filepath_config = f"{CONFIG_DIRECTORY}/{CONFIG_FILENAME}.json"
  if not HelperFuncs.fileExists(filepath_config):
    raise FileNotFoundError(f"Error: the config file '{CONFIG_FILENAME}.json' does not exist in: '{CONFIG_DIRECTORY}/'")
  dict_criteria = HelperFuncs.readSearchCriteria(CONFIG_DIRECTORY, CONFIG_FILENAME)
  config_tag = dict_criteria["config_tag"]
  HelperFuncs.printToTerminal(f"Searching for articles:")
  HelperFuncs.printToTerminal("> from: {}".format(HelperFuncs.getDateString(START_DATE)))
  HelperFuncs.printToTerminal("> to:   {}".format(HelperFuncs.getDateString(end_date)))
  HelperFuncs.printToTerminal(" ")
  HelperFuncs.printToTerminal(f"> using the '#{config_tag}' config file")
  if BOOL_SEARCH_TITLE:    HelperFuncs.printToTerminal("> searching titles.")
  if BOOL_SEARCH_ABSTRACT: HelperFuncs.printToTerminal("> searching abstracts.")
  if BOOL_SEARCH_AUTHORS:  HelperFuncs.printToTerminal("> searching authors.")
  HelperFuncs.printToTerminal(" ")
  HelperFuncs.printSearchCriteria(dict_criteria, BOOL_SEARCH_AUTHORS)
  HelperFuncs.printToTerminal("Started executing at: {}".format(dt.datetime.now().strftime("%H:%M:%S")))
  HelperFuncs.printToTerminal(" ")
  obj_scraper = ArxivScraper(
    start_date           = START_DATE,
    end_date             = end_date,
    bool_search_title    = BOOL_SEARCH_TITLE,
    bool_search_abstract = BOOL_SEARCH_ABSTRACT,
    bool_search_authors  = BOOL_SEARCH_AUTHORS
  )
  obj_scraper.search(dict_criteria)
  list_results = obj_scraper.getSortedArticles()
  HelperFuncs.printToTerminal(f"Found a total of {len(list_results)} articles.")
  HelperFuncs.printToTerminal(f"Saving articles to: {OUTPUT_DIRECTORY}")
  num_articles = len(list_results)
  for article_index, result in enumerate(list_results):
    if BOOL_PRINT_ARTICLES:
      HelperFuncs.printToTerminal(f"({article_index+1}/{num_articles})")
      HelperFuncs.printArticle(result["article"])
    if BOOL_SAVE_ARTICLES:
      HelperFuncs.saveArticle(
        article            = result["article"],
        directory_output   = OUTPUT_DIRECTORY,
        config_tag         = config_tag,
        list_config_reason = result["list_config_reason"]
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