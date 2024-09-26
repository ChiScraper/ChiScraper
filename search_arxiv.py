#!/usr/bin/env python3


## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, time, arxiv
import datetime as dt
import yaml
import numpy as np
from unidecode import unidecode
from MyLibrary import HelperFuncs
from articleDB import ArticleDatabase


## ###############################################################
## SEARCH PARAMETERS
## ###############################################################
# Load configuration from config.yaml
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

OUTPUT_DIRECTORY     = config['output_directory']
BOOL_PRINT_ARTICLES  = config['print_articles']
BOOL_SAVE_ARTICLES   = config['save_articles']
BOOL_SAVE_DATABASE   = config['output_db']
CONFIG_DIRECTORY     = config['config_directory']
CONFIG_MODEL         = config['config_modelname']
LOOKBACK_DATE        = HelperFuncs.getDateNDaysAgo(config['lookback_date'])
BOOL_SEARCH_TITLE    = config['search_title']
BOOL_SEARCH_ABSTRACT = config['search_abstract']
BOOL_SEARCH_AUTHORS  = config['search_authors']

## ###############################################################
## OPERATOR CLASS
## ###############################################################
class ArxivScraper:
  def __init__(
      self,
      lookback_date, current_date,
      bool_search_title    = True,
      bool_search_abstract = True,
      bool_search_authors  = True
    ):
    self.lookback_date        = lookback_date
    self.current_date         = current_date
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
      HelperFuncs.print2Terminal(f"Date range: {HelperFuncs.castDate2String(self.lookback_date)} to {HelperFuncs.castDate2String(self.current_date)}")
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
    return (self.lookback_date.date() <= article_date) and (article_date <= self.current_date.date())

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
  if BOOL_SAVE_DATABASE:
    # Initialize the database
    articleDB = ArticleDatabase('articles.db')
 
  time_start = time.time()
  HelperFuncs.createFolder(OUTPUT_DIRECTORY)
  current_date = HelperFuncs.getDateToday()
  if (current_date.date() - LOOKBACK_DATE.date()).days < 1:
    raise ValueError(
      "Error: Invalid date range: The final date '{}' must be at least one day after the start date '{}'.".format(
        HelperFuncs.castDate2String(current_date),
        HelperFuncs.castDate2String(LOOKBACK_DATE)
      )
    )
  filepath_config = f"{CONFIG_DIRECTORY}/{CONFIG_MODEL}.json"
  if not HelperFuncs.fileExists(filepath_config):
    raise FileNotFoundError(f"Error: the config file '{CONFIG_MODEL}.json' does not exist in: '{CONFIG_DIRECTORY}/'")
  dict_search_criteria = HelperFuncs.readSearchCriteria2Dict(CONFIG_DIRECTORY, CONFIG_MODEL)
  config_tag = dict_search_criteria["config_tag"]
  HelperFuncs.print2Terminal(f"Searching for articles:")
  HelperFuncs.print2Terminal("> from: {}".format(HelperFuncs.castDate2String(LOOKBACK_DATE)))
  HelperFuncs.print2Terminal("> to:   {}".format(HelperFuncs.castDate2String(current_date)))
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
    lookback_date        = LOOKBACK_DATE,
    current_date         = current_date,
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
    if BOOL_SAVE_DATABASE:
        # print(result)
        articleMetadata = {
            'title': dict_article_info['title'],
            'arxiv_id': dict_article_info['arxiv_id'],
            'url_pdf': dict_article_info['url_pdf'],
            'date_published': dict_article_info['date_published'],
            'date_updated': dict_article_info['date_updated'],
            'category_primary': dict_article_info['category_primary'],
            'authors': [
                unidecode(str(author))
                for author in HelperFuncs.shortenList(dict_article_info['authors'])
            ],
            'abstract': dict_article_info['abstract']
        }
        article_id = articleDB.add_article_metadata(**articleMetadata)
        articleDB.add_article_tag(article_id, [config_tag])


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