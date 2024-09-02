## ###############################################################
## IMPORT MODULES
## ###############################################################
import os, sys, json, re, argparse
import datetime as dt
from unidecode import unidecode


## ###############################################################
## MISCELLANEOUS
## ###############################################################
def createFolder(filepath):
  if not(os.path.exists(filepath)):
    os.makedirs(filepath)
    print(f"Successfully created folder: {filepath}\n")

def shortenList(list_elems, max_elems=5):
  list_sub_elems = [
    str(elem)  if (elem_index <  max_elems+1)
    else "..." if (elem_index == max_elems+1)
    else None
    for elem_index, elem in enumerate(list_elems)
  ]
  return [
    elem
    for elem in list_sub_elems
    if elem is not None
  ]

def formatText(text):
  ## adjust text for things that go wrong with Obsidian's tex-rendering
  text = text.replace("\'", "")
  text = text.replace(":", "...")
  text = text.replace('"', "`")
  ## add spaces before and after text between two dollar signs (LaTeX math)
  text = re.sub(r"(\$.*?\$)", lambda m: f" {m.group(1)} ", text)
  ## remove any extra (eg, double) spaces that might have been added inadvertently
  text = re.sub(r"\s+", " ", text).strip()
  return text

def fileExists(filepath):
  return os.path.isfile(filepath)

def printToTerminal(message, end="\n"):
  print(message, end=end, flush=True)

class MyHelpFormatter(argparse.RawDescriptionHelpFormatter):
  def _format_action(self, action):
    parts = super(argparse.RawDescriptionHelpFormatter, self)._format_action(action)
    if action.nargs == argparse.PARSER:
      parts = "\n".join(parts.split("\n")[1:])
    return parts

class MyParser(argparse.ArgumentParser):
  def __init__(self, description):
    super(MyParser, self).__init__(
      description     = description,
      formatter_class = lambda prog: MyHelpFormatter(prog, max_help_position=50),
    )

  def error(self, message):
    sys.stderr.write("Error: {}\n\n".format(message))
    self.print_help()
    sys.exit(2)


## ###############################################################
## LOAD SEARCH CRITERIA
## ###############################################################
def readSearchCriteria(directory, filename):
  filepath_file = f"{directory}/{filename}.json"
  if fileExists(filepath_file):
    with open(filepath_file, "r") as input:
      dict_config = json.load(input)
  else: raise Exception(f"Error: '{filename}.json' config file does not exist in: '{directory}/'")
  list_missing_keys = []
  for key in [
      "config_tag",
      "list_authors",
      "list_categories",
      "list_keywords_exclude",
      "list_keywords_include"
    ]:
    if key not in dict_config: list_missing_keys.append(f"'{key}'")
  if len(list_missing_keys) > 0:
    print(f"The following config keys are missing:")
    print("\t", ", ".join(list_missing_keys), "\n")
    raise Exception("Error: Config file is missing search keys")
  return dict_config


## ###############################################################
## FORMAT DATES
## ###############################################################
def getDateString(date):
  str_year  = str(date.year ).zfill(4)
  str_month = str(date.month).zfill(2)
  str_day   = str(date.day  ).zfill(2)
  return f"{str_year}-{str_month}-{str_day}"

def getDateToday():
  return dt.datetime.now()

def getDateNDaysAgo(num_days):
  date_today = dt.datetime.now()
  date_delta = dt.timedelta(days=int(num_days))
  date_ago  = date_today - date_delta
  return date_ago

def getArticleDate(article):
  return article.published


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

def getArticleDetails(filepath_article):
  task_status_found = None
  list_tags_found = []
  with open(filepath_article, "r") as filepointer:
    for line in filepointer.readlines():
      if "#task" in line: task_status_found = line.split("[")[1].split("]")[0]
      if "Tags:" in line: list_tags_found = line.split(":")[1].strip().split(" ")
  task_status = task_status_found if task_status_found in ["u", "r", "d"] else "u"
  list_tags = [
    tag
    for tag in list_tags_found
    if (tag != "") and (tag[0] == "#")
  ]
  return {
    "task_status" : task_status,
    "list_tags"   : list_tags
  }


## ###############################################################
## SAVING ARTICLE INFORMATION
## ###############################################################
def printArticle(article, num_pad_chars=17):
  ## helper function
  def printLine(category, content):
    if isinstance(content, list): content = ", ".join(content)
    category = f"{category}:".ljust(num_pad_chars)
    print(f"{category} {content}")
  ## extract the author names
  list_authors = [
    unidecode(str(author))
    for author in shortenList(article.authors)
  ]
  ## print article information
  printLine("Title",          article.title)
  printLine("PDF URL",        article.pdf_url)
  printLine("Date Published", getDateString(article.published))
  printLine("Author(s)",      list_authors)
  print(" ")

def saveArticle(article, directory_output, config_tag):
  task_status = "u" # unread by default
  list_tags = []
  filename = article.pdf_url.split("/")[-1].split("v")[0]
  filepath_file = f"{directory_output}/{filename}.md"
  if fileExists(filepath_file):
    dict_details = getArticleDetails(filepath_file)
    task_status  = dict_details["task_status"]
    list_tags    = dict_details["list_tags"]
  if config_tag not in list_tags: list_tags.append(config_tag)
  with open(filepath_file, "w") as filepointer:
    ## overwrite the file if it exists, but retain the Obsidian task status and search category tags
    writeArticle2File(
      filepointer = filepointer,
      article     = article,
      task_status = task_status,
      list_tags   = list_tags
    )

def writeArticle2File(filepointer, article, task_status, list_tags):
  ## helper function
  def writeProperty(category, content):
    if isinstance(content, list): content = ", ".join(content)
    filepointer.write(f"{category}: {content}\n")
  ## extract the author names
  list_authors = [
    unidecode(str(author))
    for author in shortenList(article.authors)
  ]
  ## extract other categories the article is published under
  list_other_categories = [
    formatText(elem)
    for elem in shortenList(article.categories)
    if (elem != article.primary_category)
  ]
  ## save article information
  filepointer.write(f"---\n")
  writeProperty("title",            formatText(article.title))
  writeProperty("url_pdf",          article.pdf_url)
  writeProperty("date_published",   getDateString(article.published))
  writeProperty("date_updated",     getDateString(article.updated))
  writeProperty("category_primary", article.primary_category)
  writeProperty("category_others",  list_other_categories if len(list_other_categories) > 0 else "None")
  writeProperty("authors",          list_authors)
  writeProperty("abstract",         formatText(article.summary))
  filepointer.write(f"---\n")
  filepointer.write("# `$= dv.current().title`\n")
  filepointer.write("`$= dv.current().abstract`\n")
  filepointer.write("\n")
  str_tags = " ".join(list_tags)
  filepointer.write(f"Tags: {str_tags}\n")
  filepointer.write(f" - [{task_status}] #task status\n")


## END OF LIBRARY