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
    printToTerminal(f"Successfully created folder: {filepath}\n")

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
  text = text.replace("#", "")
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
    printToTerminal(f"The following config keys are missing:")
    printToTerminal("\t", ", ".join(list_missing_keys), "\n")
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
    if isinstance(term, str):
      bool_term_contained = term.lower() in phrase
      list_bools.append(bool_term_contained)
    elif isinstance(term, list):
      list_bools.append(
        containsAnyKeywords(phrase, term)
      )
  return all(list_bools)

def containsAnyKeywords(phrase, list_search_terms):
  if len(list_search_terms) == 0: return False
  list_bools = []
  for term in list_search_terms:
    if isinstance(term, str):
      bool_term_contained = term.lower() in phrase.lower()
      list_bools.append(bool_term_contained)
      if bool_term_contained: break
    elif isinstance(term, list):
      list_bools.append(
        containsAllKeywords(phrase, term)
      )
  return any(list_bools)

def meetsSearchCriteria(phrase, list_search_conditions):
  return containsAnyKeywords(phrase, list_search_conditions)

def getStringOperator(count_operator):
  if count_operator % 2 == 1: return "OR"
  else: return "AND"

def printSearchCriteria(dict_search, bool_search_authors=False):
  list_keywords_include = dict_search["list_keywords_include"]
  list_keywords_exclude = dict_search["list_keywords_exclude"]
  printToTerminal("> including articles with phrases:")
  printToTerminal(lolsToSetNotation(list_keywords_include))
  printToTerminal(" ")
  if len(list_keywords_exclude) > 0:
    printToTerminal("> excluding articles with phrases:")
    printToTerminal(lolsToSetNotation(list_keywords_exclude))
    printToTerminal(" ")
  if bool_search_authors:
    list_authors = dict_search["list_authors"]
    printToTerminal("> including articles with authors:", end="")
    printToTerminal(joinList(list_authors, str_pre="\n\t- "))
    printToTerminal(" ")

# def lolsToSetNotation(lst, level=0):
#   ## unwrap single-element lists to remove unnecessary nesting
#   while isinstance(lst, list) and len(lst) == 1:
#     lst = lst[0]
#     level += 1
#   if not isinstance(lst, list):
#     return f"'{lst.lower()}'"
#   if level % 2 == 1: operator = " AND "
#   else: operator = " OR "
#   result = ""
#   for i, item in enumerate(lst):
#     if i > 0:                  result += operator
#     if isinstance(item, list): result += f"({lolsToSetNotation(item, level + 1)})"
#     else:                      result += f"'{item.lower()}'"
#   return result

def lolsToSetNotation(lst, level=0):
  while isinstance(lst, list) and (len(lst) == 1):
    lst = lst[0]
    level += 1
  if not isinstance(lst, list): return f"'{lst}'"
  if level % 2 == 1: operator = " AND "
  else: operator = " OR "
  return operator.join(
    f"({lolsToSetNotation(item, level + 1)})"
    if isinstance(item, list)
    else f"'{item}'"
    for item in lst
  )

def getArticleDetails(filepath_article):
  task_status_found = None
  list_config_tags_found = []
  list_dict_config_reasons = []
  bool_reading_tags = False
  with open(filepath_article, "r") as filepointer:
    for line in filepointer.readlines():
      ## usually at the end of the file
      if ("#task" in line):
        task_status_found = line.split("[")[1].split("]")[0]
        continue
      ## condition for when you have found the line where config tags are listed
      if ("config_tags" in line):
        bool_reading_tags = True
        continue
      elif bool_reading_tags and ("#" in line):
        str_tag = line.split("- ")[1].strip()
        list_config_tags_found.append(str_tag)
        continue
      ## once you had found the list of config tags, this indicates when you have transitioned to another section
      elif (":" in line) or ("---" in line):
        bool_reading_tags = False
      if ("config_reason" in line):
        str_config_tag = line.split("_reason_")[1].split(":")[0]
        str_config_reason = line.split(":")[1].strip()
        list_dict_config_reasons.append({
          "tag"    : str_config_tag,
          "reason" : str_config_reason
        })
        continue
  task_status = task_status_found if task_status_found in ["u", "r", "d"] else "u"
  list_config_tags = [
    tag.lower()
    for tag in list_config_tags_found
    if (tag != "")
  ]
  return {
    "task_status" : task_status,
    "list_config_tags" : list_config_tags,
    "list_dict_config_reasons" : list_dict_config_reasons
  }

def printHeading(str):
  printToTerminal(str)
  printToTerminal("=" * len(str))

def joinList(list_elems, str_pre):
  return str_pre + str_pre.join(list_elems)


## ###############################################################
## SAVING ARTICLE INFORMATION
## ###############################################################
def printArticle(article, num_pad_chars=17):
  ## helper function
  def _printLine(category, content):
    if isinstance(content, list): content = ", ".join(content)
    category = f"{category}:".ljust(num_pad_chars)
    printToTerminal(f"{category} {content}")
  ## extract the author names
  list_authors = [
    unidecode(str(author))
    for author in shortenList(article.authors)
  ]
  ## printToTerminal article information
  _printLine("Title",          article.title)
  _printLine("PDF URL",        article.pdf_url)
  _printLine("Date Published", getDateString(article.published))
  _printLine("Author(s)",      list_authors)
  printToTerminal(" ")

def saveArticle(article, directory_output, config_tag, list_config_reason=[]):
  task_status = "u" # unread by default
  list_config_tags = []
  list_dict_config_reasons = []
  filename = article.pdf_url.split("/")[-1].split("v")[0]
  filepath_file = f"{directory_output}/{filename}.md"
  if fileExists(filepath_file):
    dict_details = getArticleDetails(filepath_file)
    task_status = dict_details["task_status"]
    list_config_tags = dict_details["list_config_tags"]
    list_dict_config_reasons = dict_details["list_dict_config_reasons"]
  str_config_tag = f'"#{config_tag}"'
  if str_config_tag not in list_config_tags: list_config_tags.append(str_config_tag)
  if len(list_config_reason) > 0: str_config_reason = ",".join(list_config_reason)
  else: str_config_reason = "None"
  ## if the tag is already in the list of config reasons, replace it
  bool_config_reason_replaced = False
  for dict_config_reason in list_dict_config_reasons:
    if config_tag == dict_config_reason["tag"]:
      bool_config_reason_replaced = True
      dict_config_reason["reason"] = str_config_reason
      break
  if not(bool_config_reason_replaced):
    list_dict_config_reasons.append({
      "tag"    : config_tag,
      "reason" : str_config_reason
    })
  ## overwrite the file if it exists, but retain the Obsidian task status and search category tags
  with open(filepath_file, "w") as filepointer:
    writeArticle2File(
      filepointer         = filepointer,
      article             = article,
      task_status         = task_status,
      list_config_tags    = sorted(list_config_tags),
      list_dict_config_reasons = sorted(list_dict_config_reasons, key=lambda x: x['tag']),
    )

def writeArticle2File(filepointer, article, task_status, list_config_tags, list_dict_config_reasons):
  ## helper function
  def _writeProperty(category, content):
    if isinstance(content, list): content = ", ".join(content)
    filepointer.write(f"{category}: {content}\n")
  def _createTagList(_list_tags):
    return joinList(_list_tags, str_pre="\n    - ")
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
  str_other_categories = ", ".join(list_other_categories) if len(list_other_categories) > 0 else "None"
  str_config_tags = _createTagList(list_config_tags)
  ## save article information
  filepointer.write(f"---\n")
  ## print all article properties
  _writeProperty("title",            formatText(article.title))
  _writeProperty("arxiv_id",         article.pdf_url.split("/")[-1].split("v")[0])
  _writeProperty("url_pdf",          article.pdf_url)
  _writeProperty("date_published",   getDateString(article.published))
  _writeProperty("date_updated",     getDateString(article.updated))
  _writeProperty("category_primary", article.primary_category)
  _writeProperty("category_others",  str_other_categories)
  _writeProperty("authors",          list_authors)
  _writeProperty("abstract",         formatText(article.summary))
  _writeProperty("config_tags",      str_config_tags)
  for dict_config_reason in list_dict_config_reasons:
    _writeProperty(
      "config_reason_{}".format(dict_config_reason["tag"]),
      dict_config_reason["reason"]
    )
  filepointer.write(f"---\n")
  filepointer.write(f" - [{task_status}] #task status\n")


## END OF LIBRARY