#!/usr/bin/env python3

## arXiv scraper: search for latest in category
## Author: Neco Kriel 2022

import os, arxiv
os.system("clear")


## ###############################################################
## HELPER FUNCTIONS
## ###############################################################
def shortenList(lst, max_num_elems=5):
  list_sub_step = [
    str(item) if index < (max_num_elems+1)
    else "..." if index == (max_num_elems+1)
    else None
    for index, item in enumerate(lst)
  ]
  return [
    item for item in list_sub_step
    if item is not None
  ]

def printArticleInfo(article, num_pad_chars=20):
  list_other_categories = [
    elem for elem in shortenList(article.categories)
    if (elem != article.primary_category)
  ]
  print("arXiv URL:".ljust(num_pad_chars),        article.entry_id)
  if BOOL_VERBOSE:
    print("PDF URL:".ljust(num_pad_chars),        article.pdf_url)
  print("Title:".ljust(num_pad_chars),            article.title)
  print("Date published:".ljust(num_pad_chars),   article.published)
  if BOOL_VERBOSE:
    print("Date updated:".ljust(num_pad_chars),   article.updated)
    print("Primary category:".ljust(num_pad_chars), article.primary_category)
    print("Other categories:".ljust(num_pad_chars), ", ".join( list_other_categories) )
  print("Author(s)".ljust(num_pad_chars),         ", ".join( shortenList(article.authors)) )
  if BOOL_VERBOSE:
    print("Abstract:")
    print(article.summary)
  print(" ")


## ###############################################################
## MAIN PROGRAM
## ###############################################################
BOOL_VERBOSE = 0
SEARCH_TERM  = "dynamo"
NUM_ARTICLES = 250

def main():
  search = arxiv.Search(
    query       = SEARCH_TERM,
    max_results = NUM_ARTICLES,
    sort_by     = arxiv.SortCriterion.SubmittedDate
  )
  for article_index, article in enumerate(search.results()):
    print(f"({article_index+1})")
    printArticleInfo(article)


## ###############################################################
## RUN PROGRAM
## ###############################################################
if __name__ == "__main__":
  main()


## END OF PROGRAM