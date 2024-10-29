## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, time, datetime, re

from headers import Directories
from headers import FileNames
from headers import IO
from headers import WWFnFs
from headers import WWDates
from headers import WWArgParse
from headers import WWArticles

from scripts import search_arxiv as SearchArxiv
from scripts import score_article as ScoreArticle
from scripts import fetch_from_arxiv as FetchFromArxiv
from scripts import download_articles as DownloadArticles


## ###############################################################
## OPERATOR CLASS
## ###############################################################
class ArxivScraper():
  def __init__(self, obj_user_inputs: WWArgParse.GetUserInputs):
    self.obj_user_inputs = obj_user_inputs

  def searchArxiv(self):
    dict_search_params = self.obj_user_inputs.getSearchInputs()
    obj_search_arxiv = SearchArxiv.SearchArxiv(
      current_date  = WWDates.getDateToday(),
      lookback_date = WWDates.getDateNDaysAgo(dict_search_params["lookback_days"]),
      config_name   = dict_search_params["config_name"],
    )
    obj_search_arxiv.search()
    return obj_search_arxiv.getSortedArticles()

  def fetchFromArxiv(self):
    arxiv_id = self.obj_user_inputs.getFetchInputs()
    article_dict = FetchFromArxiv.fetchFromArxiv(arxiv_id)
    return article_dict

  def scoreArticles(self, list_article_dicts):
    num_articles    = len(list_article_dicts)
    prompt_rules    = IO.readTextFile(f"{Directories.directory_config}/{FileNames.filename_ai_rules}")
    prompt_criteria = IO.readTextFile(f"{Directories.directory_config}/{FileNames.filename_ai_criteria}")
    for article_index, dict_article in enumerate(list_article_dicts):
      print(f"({article_index+1}/{num_articles})")
      ScoreArticle.getAIScore(
        dict_article    = dict_article,
        prompt_rules    = prompt_rules,
        prompt_criteria = prompt_criteria,
      )
      print(" ")

  def printArticles(self, list_article_dicts):
    num_articles = len(list_article_dicts)
    print(f"Found {num_articles} articles:\n")
    for article_index, dict_article in enumerate(list_article_dicts):
      print(f"({article_index+1}/{num_articles})")
      WWArticles.printArticle(dict_article)
      print(" ")

  def saveArticles(self, list_article_dicts):
    WWFnFs.createDirectory(Directories.directory_mdfiles, bool_add_space=True)
    num_articles = len(list_article_dicts)
    for dict_article in list_article_dicts:
      WWArticles.saveArticle2Markdown(
        directory_output = Directories.directory_mdfiles,
        dict_article     = dict_article
      )
    print(f"Saved {num_articles} articles.")
    print(" ")

  def downloadPDFs(self):
    WWFnFs.createDirectory(Directories.directory_pdfs, bool_add_space=True)
    list_article_dicts = WWArticles.readAllMarkdownFiles()
    ## download markdown files (articles) that have been flaged `-d`
    DownloadArticles.downloadPDFs(list_article_dicts)

  def launchWebApp(self):
    ## check database against md-files
    ## 1. database exists + no disagreement -> launch webserver
    ## 2. database exists + some disagreement -> update misalignments + add new entries -> launch webserver
    ## 3. no database -> create a database -> launch webserver
    ## manual button to save to md-file (webserver tracks which entries have been edited)
    ## when the webserver is closed -> unsaved database entries are saved to md-files
    pass


## ###############################################################
## MAIN PROGRAM
## ###############################################################
def main():
  time_start = time.time()
  print("Program started at {}\n".format(
    datetime.datetime.now().strftime("%H:%M:%S")
  ))
  obj_user_inputs = WWArgParse.GetUserInputs()
  dict_program_flags = obj_user_inputs.getMainProgramInputs()
  obj_arxiv_scraper = ArxivScraper(obj_user_inputs)
  if dict_program_flags["search"]:
    list_article_dicts = obj_arxiv_scraper.searchArxiv()
    if dict_program_flags["rank"]: obj_arxiv_scraper.scoreArticles(list_article_dicts)
    if dict_program_flags["print"]: obj_arxiv_scraper.printArticles(list_article_dicts)
    obj_arxiv_scraper.saveArticles(list_article_dicts)
  elif dict_program_flags["rank"]:
    list_article_dicts = WWArticles.readAllMarkdownFiles()
    obj_arxiv_scraper.scoreArticles(list_article_dicts)
  elif dict_program_flags["fetch"]:
    dict_article = obj_arxiv_scraper.fetchFromArxiv()
    if dict_program_flags["download"]: DownloadArticles.downloadPDF(dict_article)
  elif dict_program_flags["download"]: obj_arxiv_scraper.downloadPDFs()
  if dict_program_flags["webapp"]: obj_arxiv_scraper.launchWebApp()
  time_elapsed = time.time() - time_start
  print(f"Elapsed time: {time_elapsed:.2f} seconds.")


## ###############################################################
## PROGRAM ENTRY POINT
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit(0)


## END OF PROGRAM