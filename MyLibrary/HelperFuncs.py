## ###############################################################
## IMPORT MODULES
## ###############################################################
import os, json
import datetime as dt
from unidecode import unidecode


## ###############################################################
## MISCELLANEOUS
## ###############################################################
def createFolder(filepath):
  if not(os.path.exists(filepath)):
    os.makedirs(filepath)
    print("Successfully created folder:")
    print(f"\t{filepath}\n")

def shortenList(lst, max_elems=5):
  list_sub_step = [
    str(item) if index < max_elems+1
    else "..." if index == max_elems+1
    else None
    for index, item in enumerate(lst)
  ]
  return [
    item for item in list_sub_step
    if item is not None
  ]

def readConfigFile(filename):
  ## READ IN CONFIG FILE
  ## -------------------
  filepath_file = f"Configs/{filename}.json"
  if os.path.isfile(filepath_file):
    with open(filepath_file, "r") as input:
      dict_config = json.load(input)
  else:
    raise Exception(f"The following config file could not be located: \n\t{filepath_file}")
  ## CHECK THAT THE CONFIG FILE HAS DEFINED ALL THE REQUIRED KEYS
  ## ------------------------------------------------------------
  list_missing_keys  = []
  list_required_keys = [
    "list_authors", "list_categories", "list_keywords_exclude", "list_keywords_include"
  ]
  for key in list_required_keys:
    if key not in dict_config:
      list_missing_keys.append(f"'{key}'")
  if len(list_missing_keys) > 0:
    print(f"Error: Config file '{filepath_file}' does not define the following required key(s):")
    print("\t", ", ".join(list_missing_keys), "\n")
    raise Exception("Config file is missing search key(s)")
  return dict_config

## ###############################################################
## FORMAT DATES
## ###############################################################
def getDateToday():
  date      = dt.datetime.now()
  str_year  = str(date.year ).zfill(4)
  str_month = str(date.month).zfill(2)
  str_day   = str(date.day  ).zfill(2)
  return f"{str_year}-{str_month}-{str_day}"

def getDateNDaysAgo(num_days):
  date_today = dt.datetime.now()
  date_delta = dt.timedelta(days=int(num_days))
  date_num_days_ago = date_today - date_delta
  str_year  = str(date_num_days_ago.year ).zfill(4)
  str_month = str(date_num_days_ago.month).zfill(2)
  str_day   = str(date_num_days_ago.day  ).zfill(2)
  return f"{str_year}-{str_month}-{str_day}"

def getArticleDate(article):
  date      = article.published
  str_year  = str(date.year ).zfill(4)
  str_month = str(date.month).zfill(2)
  str_day   = str(date.day  ).zfill(2)
  return f"{str_year}-{str_month}-{str_day}"


## ###############################################################
## SEARCH CRITERIA
## ###############################################################
def containsAllKeywords(phrase, list_search_terms):
  if len(list_search_terms) == 0: return False
  list_bools = []
  for term in list_search_terms:
    if type(term) is str:
      term_bool = (term in phrase)
      list_bools.append(term_bool)
    elif type(term) is list:
      list_bools.append(
        containsAnyKeyword(phrase, term)
      )
  return all(list_bools)

def containsAnyKeyword(phrase, list_search_terms):
  if len(list_search_terms) == 0: return False
  list_bools = []
  for term in list_search_terms:
    if type(term) is str:
      term_bool = (term in phrase)
      list_bools.append(term_bool)
      if term_bool: break
    elif type(term) is list:
      list_bools.append(
        containsAllKeywords(phrase, term)
      )
  return any(list_bools)


## ###############################################################
## DISPLAY ARTICLE INFORMATION
## ###############################################################
def printArticleInfo(article, num_pad_chars=20, bool_verbose=False):
  ## helper print function
  def printLine(name, content):
    if isinstance(content, list):
      content = ", ".join(content)
    print(f"{name.ljust(num_pad_chars)} {content}")
  ## extract author last names
  list_authors = [
    unidecode(str(author)) for author in shortenList(article.authors)
  ]
  ## extract other categories published under
  list_other_categories = [
    elem for elem in shortenList(article.categories)
    if (elem != article.primary_category)
  ]
  ## print article information
  printLine("arXiv URL:",          article.entry_id)
  if bool_verbose:
    printLine("PDF URL:",          article.pdf_url)
  printLine("Title:",              article.title)
  printLine("Date published:",     article.published)
  if bool_verbose:
    printLine("Date updated:",     article.updated)
    printLine("Primary category:", article.primary_category)
    printLine("Other categories:", list_other_categories)
  printLine("Author(s):",          list_authors)
  if bool_verbose:
    print("Abstract:")
    print(article.summary)
  print(" ")

def saveArticleInfo(file, article, num_pad_chars: int=20):
  ## helper write function
  def writeLine(file, name, content):
    if isinstance(content, list):
      content = ", ".join(content)
    file.write(f"{name.ljust(num_pad_chars)} {content}\n")
  ## remove primary category from list of other categories
  list_other_categories = [
    elem for elem in article.categories
    if (elem != article.primary_category)
  ]
  list_authors = [
    unidecode(str(author)) for author in article.authors
  ]
  ## save article information
  writeLine(file, "arXiv URL:",        article.entry_id)
  writeLine(file, "PDF URL:",          article.pdf_url)
  writeLine(file, "Title:",            article.title)
  writeLine(file, "Date published:",   article.published)
  writeLine(file, "Date updated:",     article.updated)
  writeLine(file, "Primary category:", article.primary_category)
  writeLine(file, "Other categories:", list_other_categories)
  writeLine(file, "Author(s):",        list_authors)
  file.write("Abstract:\n")
  file.write(article.summary)
  file.write("\n\n")


## END OF LIBRARY