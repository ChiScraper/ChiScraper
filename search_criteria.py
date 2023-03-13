#!/usr/bin/env python3

## arXiv scraper: search the arxiv using various criteria
## Author: Neco Kriel 2022

import os, sys, time, arxiv
import datetime as dt
import numpy as np
from unidecode import unidecode
from MyLibrary import HelperFuncs
os.system("clear")


## ###############################################################
## SEARCH ALGORITHM
## ###############################################################
def search(dict_search):
  list_articles = []
  ## configure arxiv API client
  small_fast_client = arxiv.Client(
    page_size     = 200,
    delay_seconds = 1,
    num_retries   = 100
  )
  ## search through categories
  for search_category in dict_search["list_categories"]:
    count = 1
    print("Searching:", search_category)
    ## comb through articles in category
    for article in small_fast_client.results(arxiv.Search(
        query       = search_category,
        max_results = NUM_ARTICLES,
        sort_by     = arxiv.SortCriterion.SubmittedDate
      )):
      ## check if this article meets criteria
      date_published = HelperFuncs.getArticleDate(article)
      if (DATE_START <= date_published) and (date_published <= DATE_FINAL):
        if any((stored_article.title == article.title) for stored_article in list_articles):
          continue
        ## initialise search outcomes
        bool_title    = False
        bool_abstract = False
        bool_authors  = False
        if BOOL_SEARCH_TITLE:
          if HelperFuncs.containsAnyKeyword(
            article.title.lower(),
            dict_search["list_keywords_exclude"]
          ): continue
          bool_title = HelperFuncs.containsAnyKeyword(
            article.title.lower(),
            dict_search["list_keywords_include"]
          )
        if BOOL_SEARCH_ABSTRACT:
          if HelperFuncs.containsAnyKeyword(
            article.summary.lower(),
            dict_search["list_keywords_exclude"]
          ): continue
          bool_abstract = HelperFuncs.containsAnyKeyword(
            article.summary.lower(),
            dict_search["list_keywords_include"]
          )
        if BOOL_SEARCH_AUTHORS:
          list_author_lastnames = [
            unidecode(str(author).lower().split(" ")[-1])
            for author in article.authors
          ]
          bool_authors = any(
            (author.lower() in list_author_lastnames)
            for author in dict_search["list_authors"]
          )
        if (bool_title or bool_abstract) or bool_authors:
          list_articles.append(article)
      else: break
      ## display search progress
      if (count % 100) == 0:
        print("x", end="")
      if (count % 500) == 0:
        print(" ", end="", flush=True)
      ## increment search count
      count += 1
    print("\n")
  ## return a list articles that met search criteria
  return list_articles


## ###############################################################
## SEARCH PARAMETERS
## ###############################################################
NUM_DAYS_IN_MONTH    = 31
DATE_START           = HelperFuncs.getDateNDaysAgo(NUM_DAYS_IN_MONTH * 3)
DATE_FINAL           = HelperFuncs.getDateToday()
NUM_ARTICLES         = float(np.inf)
BOOL_PRINT           = 0
BOOL_SAVE            = 1
FILENAME_CONFIG      = "winds" # excluding the .json extension
BOOL_SEARCH_TITLE    = 1
BOOL_SEARCH_ABSTRACT = 1
BOOL_SEARCH_AUTHORS  = 1


## ###############################################################
## MAIN PROGRAM
## ###############################################################
def main():
  if DATE_START > DATE_FINAL:
    raise Exception(f"Final date ({DATE_FINAL}) in the search window should be after the start date ({DATE_START}).")
  time_start = time.time()
  current_time = dt.datetime.now().strftime("%H:%M:%S")
  print(f"Started executing at: {current_time}")
  print(" ")
  ## read in search criteria
  dict_search = HelperFuncs.readConfigFile(FILENAME_CONFIG)
  ## search for files that meet criteria
  list_articles = search(dict_search)
  if BOOL_PRINT:
    ## print all the articles found to the terminal
    for article_index, article in enumerate(list_articles):
      print(f"({article_index+1})") # article index
      HelperFuncs.printArticleInfo(article) # save article details
  print(f"Found a total of {len(list_articles)} articles.")
  print(" ")
  if BOOL_SAVE:
    ## creating output filename
    filename = f"arxiv {DATE_FINAL} to {DATE_START}"
    filename += f" ({FILENAME_CONFIG})"
    filename += f" [{BOOL_SEARCH_TITLE} {BOOL_SEARCH_ABSTRACT} {BOOL_SEARCH_AUTHORS}]"
    ## creating directory where file will be saved
    filepath_program = os.path.dirname(os.path.realpath(__file__))
    filepath_output_folder = f"{filepath_program}/Output"
    HelperFuncs.createFolder(filepath_output_folder)
    filepath_output_file = f"{filepath_output_folder}/{filename}.txt"
    ## save all the articles found to file
    with open(filepath_output_file, "w") as txt_file:
      for article_index, article in enumerate(list_articles):
        txt_file.write(f"({article_index+1})\n") # article index
        HelperFuncs.saveArticleInfo(txt_file, article) # save article details
    print(f"Saved article details under: \n\t{filepath_output_file}")
  print(" ")
  time_elapsed = time.time() - time_start
  print(f"Elapsed time: {time_elapsed:.2f} seconds.")


## ###############################################################
## RUN PROGRAM
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit()


## END OF PROGRAM