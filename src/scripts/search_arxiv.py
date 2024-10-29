## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, arxiv, numpy, unidecode

from ChiScraper.headers import Directories
from ChiScraper.headers import IO
from ChiScraper.headers import WWFnFs
from ChiScraper.headers import WWDates
from ChiScraper.headers import WWLists
from ChiScraper.headers import WWArticles


## ###############################################################
## OPPERATOR CLASS
## ###############################################################
class SearchArxiv:
  def __init__(
      self,
      lookback_date, current_date, config_name,
      bool_search_title    = True,
      bool_search_abstract = True,
      bool_search_authors  = True,
    ):
    self.lookback_date        = lookback_date
    self.current_date         = current_date
    self.bool_search_title    = bool_search_title
    self.bool_search_abstract = bool_search_abstract
    self.bool_search_authors  = bool_search_authors
    self.config_name          = config_name
    ## initialise results
    self.list_article_dicts   = []

  def search(self):
    self._readSearchCriteria()
    for search_category in self.dict_search_criteria["list_categories"]:
      print(f"Searching: {search_category}")
      print(f"Date range: {WWDates.castDate2String(self.lookback_date)} to {WWDates.castDate2String(self.current_date)}")
      self.client = arxiv.Client(
        page_size     = 200,
        delay_seconds = 1,
        num_retries   = 100
      )
      num_articles_looked_at_in_category = 0
      num_new_articles_saved_in_category = 0
      for dict_arxiv in self.client.results(self._createSearchQuery(search_category)):
        self._displayProgress(num_articles_looked_at_in_category)
        num_articles_looked_at_in_category += 1
        if not(self._isWithinDateRange(dict_arxiv)): break
        arxiv_id = dict_arxiv.pdf_url.split("/")[-1].split("v")[0]
        if self._isDuplicate(arxiv_id): continue
        bool_relevant, list_bool_reasons = self._checkConfigConditions(dict_arxiv)
        if bool_relevant:
          dict_config_results = { self.dict_search_criteria["config_tag"] : list_bool_reasons }
          dict_article = WWArticles.getArticleSummaryDict(
            dict_arxiv          = dict_arxiv,
            dict_config_results = dict_config_results
          )
          self.list_article_dicts.append(dict_article)
          num_new_articles_saved_in_category += 1
      print(f"\nFound {num_new_articles_saved_in_category} interesting articles from the {num_articles_looked_at_in_category} looked at.\n")

  def getSortedArticles(self):
    return sorted(
      self.list_article_dicts,
      key     = lambda dict_article: dict_article["date_updated"],
      reverse = True
    )

  def _readSearchCriteria(self):
    self.dict_search_criteria = IO.readSearchCriteria2Dict(
      directory = Directories.directory_config,
      filename  = self.config_name,
    )
    config_tag = self.dict_search_criteria["config_tag"]
    print(f"Searching for articles:")
    print("> from: {}".format(WWDates.castDate2String(self.lookback_date)))
    print("> to:   {}".format(WWDates.castDate2String(self.current_date)))
    print(" ")
    print(f"> using the `#{config_tag}` config file")
    if self.bool_search_title:    print("> searching titles.")
    if self.bool_search_abstract: print("> searching abstracts.")
    if self.bool_search_authors:  print("> searching authors.")
    if all([
        not(self.bool_search_title),
        not(self.bool_search_abstract),
        not(self.bool_search_authors)
      ]):
      raise Exception("Error: you have not specified where to apply search criteria (i.e., title, abstract, authors).")
    print(" ")
    WWLists.printSearchCriteria(self.dict_search_criteria, self.bool_search_authors)

  def _createSearchQuery(self, category):
    return arxiv.Search(
      query       = category,
      max_results = float(numpy.inf),
      sort_by     = arxiv.SortCriterion.SubmittedDate
    )

  def _isWithinDateRange(self, dict_arxiv):
    article_date = dict_arxiv.updated.date()
    return (self.lookback_date.date() <= article_date) and (article_date <= self.current_date.date())

  def _isDuplicate(self, this_arxiv_id):
    return any([
      this_arxiv_id == article_dict["arxiv_id"]
      for article_dict in self.list_article_dicts
    ])

  def _checkConfigConditions(self, dict_arxiv):
    bool_satisfied_title    = False
    bool_satisfied_abstract = False
    bool_satisfied_authors  = False
    if self.bool_search_title:
      if WWLists.meetsSearchCriteria(dict_arxiv.title.lower(), self.dict_search_criteria["list_keywords_exclude"]): return False, None
      bool_satisfied_title = WWLists.meetsSearchCriteria(dict_arxiv.title.lower(), self.dict_search_criteria["list_keywords_include"])
    if self.bool_search_abstract:
      if WWLists.meetsSearchCriteria(dict_arxiv.summary.lower(), self.dict_search_criteria["list_keywords_exclude"]): return False, None
      bool_satisfied_abstract = WWLists.meetsSearchCriteria(dict_arxiv.summary.lower(), self.dict_search_criteria["list_keywords_include"])
    if self.bool_search_authors:
      list_author_lastnames = [
        unidecode.unidecode(str(author).lower().split(" ")[-1])
        for author in dict_arxiv.authors
      ]
      bool_satisfied_authors = any(
        author.lower() in list_author_lastnames
        for author in self.dict_search_criteria["list_authors"]
      )
    list_bool_reasons = [
      bool_satisfied_title,
      bool_satisfied_abstract,
      bool_satisfied_authors
    ]
    return any(list_bool_reasons), list_bool_reasons

  def _displayProgress(self, num_articles_looked_at_in_category):
    if num_articles_looked_at_in_category == 0: print("Progress:", end=" ")
    else:
      if (num_articles_looked_at_in_category % 10) == 0: print("x", end="")
      if (num_articles_looked_at_in_category % 50) == 0: print(" ", end="")


## ###############################################################
## MAIN PROGRAM
## ###############################################################
def main():
  dict_yaml = IO.readParameterFile(Directories.directory_config)
  obj_search_arxiv = SearchArxiv(
    current_date         = WWDates.getDateToday(),
    lookback_date        = WWDates.getDateNDaysAgo(dict_yaml["lookback_days"]),
    bool_search_title    = dict_yaml["search_title"],
    bool_search_abstract = dict_yaml["search_abstract"],
    bool_search_authors  = dict_yaml["search_authors"],
    config_name          = dict_yaml["config_name"],
  )
  obj_search_arxiv.search()
  list_article_dicts = obj_search_arxiv.getSortedArticles()
  WWFnFs.createDirectory(Directories.directory_mdfiles, bool_add_space=True)
  for dict_article in list_article_dicts:
    WWArticles.saveArticle2Markdown(
      directory_output = Directories.directory_mdfiles,
      dict_article     = dict_article
    )
  print(f"Saved {len(list_article_dicts)} articles.")
  print(" ")


## ###############################################################
## PROGRAM ENTRY POINT
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit(0)


## END OF PROGRAM