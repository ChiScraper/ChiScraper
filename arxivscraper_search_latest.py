#!/usr/bin/env python3

## arXiv scraper: search for latest in category
## Author: Neco Kriel 2022

import arxiv

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
def shortenList(lst, max_num_elems=5):
  lst_sub_step = [
    str(item) if index < (max_num_elems+1)
    else "..." if index == (max_num_elems+1)
    else None
    for index, item in enumerate(lst)
  ]
  return [
    item
    for item in lst_sub_step
    if item is not None
  ]

def printArticleInfo(article, num_pad_chars=20):
  list_other_categories = [
    elem
    for elem in shortenList(article.categories)
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
BOOL_VERBOSE = 1
SEARCH_TERM  = "physics.pop-ph" # science communication
# SEARCH_TERM  = "magneti"
NUM_ARTICLES = 50

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