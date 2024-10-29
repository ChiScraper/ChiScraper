## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, time, datetime, re

from ChiScraper.headers import Directories
from ChiScraper.headers import FileNames
from ChiScraper.headers import IO
from ChiScraper.headers import WWFnFs
from ChiScraper.headers import WWDates
from ChiScraper.headers import WWArgParse
from ChiScraper.headers import WWArticles

from ChiScraper.scripts import search_arxiv as SearchArxiv
from ChiScraper.scripts import score_article as ScoreArticle
from ChiScraper.scripts import fetch_from_arxiv as FetchFromArxiv
from ChiScraper.scripts import download_articles as DownloadArticles


## ###############################################################
## GET USER INPUT
## ###############################################################
def getUserInputs():
  dict_args = {
    "default"  : False,
    "required" : False,
    "action"   : "store_true",
    "help"     : "type: bool, default: %(default)s"
  }
  parser = WWArgParse.MyParser(description="Calculate kinetic and magnetic energy spectra.")
  parse_args = parser.add_argument_group(description="Optional arguments:")
  parse_args.add_argument("-s", "--search",   **dict_args)
  parse_args.add_argument("-f", "--fetch",    **dict_args)
  parse_args.add_argument("-r", "--rank",     **dict_args)
  parse_args.add_argument("-p", "--print",    **dict_args)
  parse_args.add_argument("-d", "--download", **dict_args)
  parse_args.add_argument("-w", "--webapp",   **dict_args)
  args = vars(parser.parse_args())
  print(args)
  # if all([
  #     not(value)
  #     for value, _ in parse_args
  #   ]):
  #   raise Exception("Error: At least one program flag/argument must be provided. Run `python main.py --help` (-h) for details.")
  return args


## ###############################################################
## OPERATOR CLASS
## ###############################################################
class ArxivScraper():
  def __init__(self, dict_yaml):
    self.current_date         = WWDates.getDateToday()
    ## TODO: do away with yaml file
    self.lookback_date        = WWDates.getDateNDaysAgo(dict_yaml["lookback_days"]) # run time param.
    self.bool_search_title    = dict_yaml["search_title"] # remove
    self.bool_search_abstract = dict_yaml["search_abstract"] # remove
    self.bool_search_authors  = dict_yaml["search_authors"] # remove
    self.config_name          = dict_yaml["config_name"] # run time param.

  def searchArxiv(self):
    obj_search_arxiv = SearchArxiv.SearchArxiv(
      current_date         = self.current_date,
      lookback_date        = self.lookback_date,
      bool_search_title    = self.bool_search_title,
      bool_search_abstract = self.bool_search_abstract,
      bool_search_authors  = self.bool_search_authors,
      config_name          = self.config_name,
    )
    obj_search_arxiv.search()
    return obj_search_arxiv.getSortedArticles()

  def fetchFromArxiv(self):
    print("Which article do you want to fetch from the Arxiv?\n")
    arxiv_id = input("Enter an arXiv ID: ")
    re_pattern = r"^\d{4}\.\d{4,5}$"
    if not re.match(re_pattern, arxiv_id): print(f"The ID you entered `{arxiv_id}` was invalid. Please enter it in the format `2310.17036`.")
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

  def downloadPDFs(
      self,
      list_article_dicts = [],
      bool_download_from_markdown = False
    ):
    WWFnFs.createDirectory(Directories.directory_pdfs, bool_add_space=True)
    if bool_download_from_markdown: list_article_dicts = WWArticles.readAllMarkdownFiles()
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
  dict_user_args = getUserInputs()
  dict_yaml = IO.readParameterFile(Directories.directory_config)
  obj_arxiv_scraper = ArxivScraper(dict_yaml)
  if dict_user_args["search"]:
    list_article_dicts = obj_arxiv_scraper.searchArxiv()
    if dict_user_args["rank"]: obj_arxiv_scraper.scoreArticles(list_article_dicts)
    if dict_user_args["print"]: obj_arxiv_scraper.printArticles(list_article_dicts)
    obj_arxiv_scraper.saveArticles(list_article_dicts)
  elif dict_user_args["rank"]:
    list_article_dicts = WWArticles.readAllMarkdownFiles()
    obj_arxiv_scraper.scoreArticles(list_article_dicts)
    obj_arxiv_scraper.saveArticles(list_article_dicts)
  elif dict_user_args["fetch"]:
    article_dict = obj_arxiv_scraper.fetchFromArxiv()
    if dict_user_args["download"]: obj_arxiv_scraper.downloadPDFs([ article_dict ]) # bug: does not download
  elif dict_user_args["download"]: obj_arxiv_scraper.downloadPDFs(bool_download_from_markdown=True)
  if dict_user_args["webapp"]: obj_arxiv_scraper.launchWebApp()
  time_elapsed = time.time() - time_start
  print(f"Elapsed time: {time_elapsed:.2f} seconds.")


## ###############################################################
## PROGRAM ENTRY POINT
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit(0)


## END OF PROGRAM