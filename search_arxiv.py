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
BOOL_PRINT_ARTICLES  = 1
BOOL_SAVE_ARTICLES   = 1
CONFIG_DIRECTORY     = "./configs"
CONFIG_MODELNAME      = "plasma"
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
    self.list_article_dicts   = []
    self.client = arxiv.Client(
      page_size     = 200,
      delay_seconds = 1,
      num_retries   = 100
    )

  def search(self, dict_search_criteria):
    for search_category in dict_search_criteria["list_categories"]:
      HelperFuncs.print2Terminal(f"Searching: {search_category}")
      HelperFuncs.print2Terminal(f"Date range: {HelperFuncs.castDate2String(self.start_date)} to {HelperFuncs.castDate2String(self.end_date)}")
      num_looked_at_in_category = 0
      num_saved_in_category     = 0
      for article in self.client.results(self._createSearchQuery(search_category)):
        self._displayProgress(num_looked_at_in_category)
        num_looked_at_in_category += 1
        if not(self._isWithinDateRange(article)): break
        arxiv_id = article.pdf_url.split("/")[-1].split("v")[0]
        if self._isDuplicate(arxiv_id): continue
        bool_relevant, list_bool_reasons = self._checkConfigConditions(article, dict_search_criteria)
        if bool_relevant:
          dict_config_results = { dict_search_criteria["config_tag"] : list_bool_reasons }
          dict_article_info = HelperFuncs.getDictOfArticleInfo(article, dict_config_results=dict_config_results)
          self.list_article_dicts.append(dict_article_info)
          num_saved_in_category += 1
      HelperFuncs.print2Terminal(f"\nFound {num_saved_in_category} useful files from the {num_looked_at_in_category} looked at.\n")

  def getSortedArticles(self):
    return sorted(
      self.list_article_dicts,
      key     = lambda dict_article_info: dict_article_info["date_updated"],
      reverse = True
    )

  def _createSearchQuery(self, category):
    return arxiv.Search(
      query       = category,
      max_results = float(np.inf),
      sort_by     = arxiv.SortCriterion.SubmittedDate
    )

  def _isWithinDateRange(self, article):
    article_date = article.updated.date()
    return (self.start_date.date() <= article_date) and (article_date <= self.end_date.date())

  def _isDuplicate(self, this_arxiv_id):
    return any([
      this_arxiv_id == article_dict["arxiv_id"]
      for article_dict in self.list_article_dicts
    ])

  def _checkConfigConditions(self, article, dict_search_criteria):
    bool_satisfied_title    = False
    bool_satisfied_abstract = False
    bool_satisfied_authors  = False
    if self.bool_search_title:
      if HelperFuncs.meetsSearchCriteria(article.title.lower(), dict_search_criteria["list_keywords_exclude"]): return False, None
      bool_satisfied_title = HelperFuncs.meetsSearchCriteria(article.title.lower(), dict_search_criteria["list_keywords_include"])
    if self.bool_search_abstract:
      if HelperFuncs.meetsSearchCriteria(article.summary.lower(), dict_search_criteria["list_keywords_exclude"]): return False, None
      bool_satisfied_abstract = HelperFuncs.meetsSearchCriteria(article.summary.lower(), dict_search_criteria["list_keywords_include"])
    if self.bool_search_authors:
      list_author_lastnames = [
        unidecode(str(author).lower().split(" ")[-1])
        for author in article.authors
      ]
      bool_satisfied_authors = any(
        author.lower() in list_author_lastnames
        for author in dict_search_criteria["list_authors"]
      )
    list_bool_reasons = [
      bool_satisfied_title,
      bool_satisfied_abstract,
      bool_satisfied_authors
    ]
    return any(list_bool_reasons), list_bool_reasons

  def _displayProgress(self, num_looked_at_in_category):
    if num_looked_at_in_category == 0: HelperFuncs.print2Terminal("Progress:", end=" ")
    else:
      if (num_looked_at_in_category % 10) == 0: HelperFuncs.print2Terminal("x", end="")
      if (num_looked_at_in_category % 50) == 0: HelperFuncs.print2Terminal(" ", end="")


## ###############################################################
## MAIN PROGRAM
## ###############################################################
def main():
  time_start = time.time()
  HelperFuncs.createFolder(OUTPUT_DIRECTORY)
  end_date = HelperFuncs.getDateToday()
  if (end_date.date() - START_DATE.date()).days < 1:
    raise ValueError(
      "Error: invalid date range: the final date ({}) must be at least one day after the start date ({}). ".format(end_date, START_DATE),
      "Please ensure that the final date is the same or later than the start date."
    )
  filepath_config = f"{CONFIG_DIRECTORY}/{CONFIG_MODELNAME}.json"
  if not HelperFuncs.fileExists(filepath_config):
    raise FileNotFoundError(f"Error: the config file '{CONFIG_MODELNAME}.json' does not exist in: '{CONFIG_DIRECTORY}/'")
  dict_search_criteria = HelperFuncs.readSearchCriteria2Dict(CONFIG_DIRECTORY, CONFIG_MODELNAME)
  config_tag = dict_search_criteria["config_tag"]
  HelperFuncs.print2Terminal(f"Searching for articles:")
  HelperFuncs.print2Terminal("> from: {}".format(HelperFuncs.castDate2String(START_DATE)))
  HelperFuncs.print2Terminal("> to:   {}".format(HelperFuncs.castDate2String(end_date)))
  HelperFuncs.print2Terminal(" ")
  HelperFuncs.print2Terminal(f"> using the '#{config_tag}' config file")
  if BOOL_SEARCH_TITLE:    HelperFuncs.print2Terminal("> searching titles.")
  if BOOL_SEARCH_ABSTRACT: HelperFuncs.print2Terminal("> searching abstracts.")
  if BOOL_SEARCH_AUTHORS:  HelperFuncs.print2Terminal("> searching authors.")
  HelperFuncs.print2Terminal(" ")
  HelperFuncs.printSearchCriteria(dict_search_criteria, BOOL_SEARCH_AUTHORS)
  HelperFuncs.print2Terminal("Started executing at: {}".format(dt.datetime.now().strftime("%H:%M:%S")))
  HelperFuncs.print2Terminal(" ")
  obj_scraper = ArxivScraper(
    start_date           = START_DATE,
    end_date             = end_date,
    bool_search_title    = BOOL_SEARCH_TITLE,
    bool_search_abstract = BOOL_SEARCH_ABSTRACT,
    bool_search_authors  = BOOL_SEARCH_AUTHORS
  )
  obj_scraper.search(dict_search_criteria)
  list_article_dicts = obj_scraper.getSortedArticles()
  HelperFuncs.print2Terminal(f"Found a total of {len(list_article_dicts)} articles.")
  HelperFuncs.print2Terminal(f"Saving articles to: {OUTPUT_DIRECTORY}")
  num_articles = len(list_article_dicts)
  for article_index, dict_article_info in enumerate(list_article_dicts):
    if BOOL_PRINT_ARTICLES:
      HelperFuncs.print2Terminal(f"({article_index+1}/{num_articles})")
      HelperFuncs.printArticle(dict_article_info)
    if BOOL_SAVE_ARTICLES:
      HelperFuncs.saveArticle(
        directory_output  = OUTPUT_DIRECTORY,
        dict_article_info = dict_article_info
      )
  time_elapsed = time.time() - time_start
  HelperFuncs.print2Terminal(" ")
  HelperFuncs.print2Terminal(f"Elapsed time: {time_elapsed:.2f} seconds.")


## ###############################################################
## PROGRAM ENTRY POINT
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit()


## END OF PROGRAM