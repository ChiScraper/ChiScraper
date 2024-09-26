## ###############################################################
## IMPORT MODULES
## ###############################################################
import os, sys, json, re, argparse, yaml
import datetime as dt
from unidecode import unidecode


## ###############################################################
## MISCELLANEOUS
## ###############################################################
def createFolder(filepath):
  if not(os.path.exists(filepath)):
    os.makedirs(filepath)
    print2Terminal(f"Successfully created folder: {filepath}\n")

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

def print2Terminal(message, end="\n"):
  print(message, end=end, flush=True)

def printHeading(str):
  print2Terminal(str)
  print2Terminal("=" * len(str))

def joinList(list_elems, str_sep="", bool_pre=False):
  list_elems = map(str, list_elems)
  if bool_pre: str_pre = str_sep
  else:        str_pre = ""
  return str_pre + str_sep.join(list_elems)

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
def readSearchCriteria2Dict(directory, filename):
  dict_config = readFile(f"{directory}/{filename}.json", ".json")
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
    print2Terminal(f"The following config keys are missing:")
    print2Terminal("\t", ", ".join(list_missing_keys), "\n")
    raise Exception("Error: Config file is missing search keys")
  return dict_config


## ###############################################################
## FORMAT DATES
## ###############################################################
def castDate2String(date):
  str_year  = str(date.year ).zfill(4)
  str_month = str(date.month).zfill(2)
  str_day   = str(date.day  ).zfill(2)
  return f"{str_year}-{str_month}-{str_day}"

def castString2Date(str_date):
  return dt.datetime.strptime(str_date, "%Y-%m-%d").date()

def getDateToday():
  return dt.datetime.now()

def getDateNDaysAgo(num_days):
  date_today = dt.datetime.now()
  date_delta = dt.timedelta(days=int(num_days))
  date_ago  = date_today - date_delta
  return date_ago


## ###############################################################
## SEARCH CRITERIA
## ###############################################################
def containsAllKeywords(phrase, list_search_keywords):
  if len(list_search_keywords) == 0: return False
  list_bools = []
  for keyword in list_search_keywords:
    if isinstance(keyword, str):
      bool_term_contained = keyword.lower() in phrase
      list_bools.append(bool_term_contained)
    elif isinstance(keyword, list):
      list_bools.append(
        containsAnyKeywords(phrase, keyword)
      )
  return all(list_bools)

def containsAnyKeywords(phrase, list_search_keywords):
  if len(list_search_keywords) == 0: return False
  list_bools = []
  for keyword in list_search_keywords:
    if isinstance(keyword, str):
      bool_term_contained = keyword.lower() in phrase.lower()
      list_bools.append(bool_term_contained)
      if bool_term_contained: break
    elif isinstance(keyword, list):
      list_bools.append(
        containsAllKeywords(phrase, keyword)
      )
  return any(list_bools)

def meetsSearchCriteria(phrase, list_search_conditions):
  return containsAnyKeywords(phrase, list_search_conditions)

def printSearchCriteria(dict_search, bool_search_authors=False):
  list_keywords_include = dict_search["list_keywords_include"]
  list_keywords_exclude = dict_search["list_keywords_exclude"]
  print2Terminal("> including articles with phrases:")
  print2Terminal(lolsToSetNotation(list_keywords_include))
  print2Terminal(" ")
  if len(list_keywords_exclude) > 0:
    print2Terminal("> excluding articles with phrases:")
    print2Terminal(lolsToSetNotation(list_keywords_exclude))
    print2Terminal(" ")
  if bool_search_authors:
    list_authors = dict_search["list_authors"]
    print2Terminal("> including articles with authors:", end="")
    print2Terminal(joinList(list_authors, str_sep="\n\t- ", bool_pre=True))
    print2Terminal(" ")

def printDict2Terminal(input_dict, indent=0):
  def _printWithIndent(indent, key, value, bool_print_type=True):
    if bool_print_type: print(" " * indent + f"'{key}' ({type(value).__name__}) : {value}")
    else:               print(" " * indent + f"'{key}' : {value}")
  def _printDict(d, indent):
    for key in sorted(d.keys()):
      value = d[key]
      if isinstance(value, dict):
        _printWithIndent(indent, key, "[dict]", False)
        _printDict(value, indent+4)
      elif isinstance(value, list):
        _printWithIndent(indent, key, "[list]", False)
        for idx, item in enumerate(value):
          if isinstance(item, dict) or isinstance(item, list):
            _printDict(item, indent+4)
          else: _printWithIndent(indent+4, f"{idx}->", item)
      else: _printWithIndent(indent, key, value)
  _printDict(input_dict, indent)

def lolsToSetNotation(list_elems, set_level=0):
  while isinstance(list_elems, list) and (len(list_elems) == 1):
    list_elems = list_elems[0]
    set_level += 1
  if not isinstance(list_elems, list): return f"'{list_elems}'"
  if set_level % 2 == 1: operator = " AND "
  else: operator = " OR "
  return operator.join(
    f"({lolsToSetNotation(elem, set_level+1)})"
    if isinstance(elem, list)
    else f"'{elem}'"
    for elem in list_elems
  )

def readFile(filepath_file, expected_file_extension):
  if not(filepath_file.endswith(expected_file_extension)):
      raise ValueError(f"Error: File must use a '{expected_file_extension}' extension. Input filepath: {filepath_file}")
  try:
    if expected_file_extension == ".json":
      with open(filepath_file, "r") as fp:
        file_content = json.load(fp)
    else:
      with open(filepath_file, "r", encoding="utf-8") as fp:
        file_content = fp.read()
  except Exception as e: raise IOError(f"Error reading file {filepath_file}: {e}")
  return file_content

REQUIRED_METADATA = [
  "title",
  "authors",
  "abstract",
  "arxiv_id",
  "url_pdf",
  "date_published",
  "date_updated",
  "category_primary",
  "category_others",
  "config_tags",
]

def readMarkdownFile2Dict(md_file):
  content = readFile(md_file, ".md")
  ## split the file into frontmatter (YAML) and body (markdown)
  match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
  if match:
    frontmatter_content = match.group(1)
    body = match.group(2)
  else: raise ValueError("Missing frontmatter section in the Markdown file.")
  # Parse the YAML frontmatter
  try:
    metadata = yaml.safe_load(frontmatter_content)
  except yaml.YAMLError as e: raise ValueError(f"Error parsing YAML frontmatter: {e}")
  # Ensure all required keys are present in the metadata
  missing_keys = [
    key
    for key in REQUIRED_METADATA
    if key not in metadata
  ]
  if missing_keys: raise ValueError("Missing required keys in frontmatter:", ", ".join(missing_keys))
  # Extract all config_reason_* keys
  config_reasons = {k: v for k, v in metadata.items() if k.startswith("config_reason_")}
  # Find the character inside the brackets [] on the same line as `#task`
  task_status = "u"
  task_match = re.search(r"^\s*-\s+\[([^\]]+)\].*#task", body, re.MULTILINE)
  if task_match: task_status = task_match.group(1)
  ## collect all the properties
  properties = {
    "title"            : metadata.get("title"),
    "authors"          : metadata.get("authors"),
    "abstract"         : metadata.get("abstract"),
    "arxiv_id"         : metadata.get("arxiv_id"),
    "url_pdf"          : metadata.get("url_pdf"),
    "date_published"   : castString2Date(metadata.get("date_published")),
    "date_updated"     : castString2Date(metadata.get("date_updated")),
    "category_primary" : metadata.get("category_primary"),
    "category_others"  : metadata.get("category_others", None),
    "config_tags"      : metadata.get("config_tags", []),
    "ai_rating"        : metadata.get("ai_rating", None),
    "ai_reason"        : metadata.get("ai_reason", None),
    "task_status"      : task_status,
    **config_reasons
  }
  return dict(sorted(properties.items()))

def getDictOfArticleInfo(article, dict_config_results={}, dict_ai_results={}, task_status="u"):
  list_authors = [
    unidecode(str(author))
    for author in shortenList(article.authors)
  ]
  list_other_categories = [
    formatText(elem)
    for elem in shortenList(article.categories)
    if (elem != article.primary_category)
  ]
  list_config_tags = [
    f"#{key}"
    if "#" not in key
    else key
    for key in dict_config_results.keys()
  ]
  dict_article_info = {
    "title"               : formatText(article.title),
    "arxiv_id"            : article.pdf_url.split("/")[-1].split("v")[0],
    "url_pdf"             : article.pdf_url,
    "authors"             : list_authors,
    "abstract"            : formatText(article.summary),
    "date_published"      : article.published.date(),
    "date_updated"        : article.updated.date(),
    "category_primary"    : article.primary_category,
    "category_others"     : list_other_categories,
    "config_tags"         : list_config_tags,
    "task_status"         : task_status,
  }
  for config_tag, list_bool_reasons in dict_config_results.items():
    dict_article_info[f"config_reason_{config_tag}"] = list_bool_reasons
  for ai_key, ai_value in dict_ai_results.items():
    if   ai_key == "ai_rating": dict_article_info["ai_rating"] = ai_value
    elif ai_key == "ai_reason": dict_article_info["ai_reason"] = ai_value
  return dict_article_info


## ###############################################################
## SAVING ARTICLE INFORMATION
## ###############################################################
def printArticle(dict_article_info, num_pad_chars=17):
  ## helper function
  def _printLine(category, content):
    if isinstance(content, list): content = ", ".join(content)
    category = f"{category}".ljust(num_pad_chars)
    print2Terminal(f"{category}: {content}")
  ## print article information
  printDict2Terminal(dict_article_info)
  # _printLine("Title",         dict_article_info["title"])
  # _printLine("PDF URL",       dict_article_info["url_pdf"])
  # _printLine("Date Updated",  castDate2String(dict_article_info["date_updated"]))
  # _printLine("Author(s)",     dict_article_info["authors"])
  print2Terminal(" ")

def saveArticle(directory_output, dict_article_info, bool_verbose=False):
  filename = dict_article_info["arxiv_id"] + ".md"
  filepath_file = f"{directory_output}/{filename}"
  # Check if the file already exists
  if fileExists(filepath_file):
    _dict_article_info = readMarkdownFile2Dict(filepath_file)
    _task_status = _dict_article_info["task_status"]
    # If the article has already been assessed, don't overwrite it
    if _task_status in [ "D", "-" ]: return
    # Retain the task status
    dict_article_info["task_status"] = _task_status
    # Merge `config_tags`: only add unique tags from `_dict_article_info`
    if "config_tags" in _dict_article_info:
      dict_article_info["config_tags"] = list(
        set(dict_article_info.get("config_tags", [])) | set(_dict_article_info.get("config_tags", []))
      )
    # Retain `ai_rating` only if it is not None in `_dict_article_info`
    if _dict_article_info.get("ai_rating") is not None:
      dict_article_info["ai_rating"] = _dict_article_info.get("ai_rating")
    # Retain `ai_reason` only if it is not None in `_dict_article_info`
    if _dict_article_info.get("ai_reason") is not None:
      dict_article_info["ai_reason"] = _dict_article_info.get("ai_reason")
    # Merge `config_reason_*` keys from `_dict_article_info` if they don't already exist in `dict_article_info`
    for key, value in _dict_article_info.items():
      if key.startswith("config_reason_") and key not in dict_article_info:
        dict_article_info[key] = value
  # Overwrite the file if it exists, but retain the Obsidian task status and search category tags
  with open(filepath_file, "w") as filepointer:
    writeArticle2File(filepointer, dict_article_info)
  if bool_verbose: print2Terminal(f"Saved: {filename}\n")


def writeArticle2File(filepointer, dict_article_info):
  ## Helper functions
  def _format_list(content):
    if not content:
      return None
    return content
  def _write_task_status(task_status):
    filepointer.write(f" - [{task_status}] #task status\n")
  ## Prepare the YAML frontmatter
  yaml_content = {
    "title":            formatText(dict_article_info["title"]),
    "arxiv_id":         dict_article_info["arxiv_id"],
    "url_pdf":          dict_article_info["url_pdf"],
    "date_published":   castDate2String(dict_article_info["date_published"]),
    "date_updated":     castDate2String(dict_article_info["date_updated"]),
    "category_primary": dict_article_info["category_primary"],
    "category_others":  _format_list(dict_article_info.get("category_others")),
    "config_tags":      _format_list(dict_article_info.get("config_tags")),
    "authors":          dict_article_info.get("authors"),
    "abstract":         formatText(dict_article_info["abstract"]),
  }
  # Optional keys handling (these can be lists, booleans, or strings)
  list_optional_key_conditions = [
    "config_reason_",
    "ai_rating",
    "ai_reason",
  ]
  # Dynamically add optional keys to YAML content
  for key, value in dict_article_info.items():
    if any(
      key_condition in key
      for key_condition in list_optional_key_conditions
    ):
      yaml_content[key] = value
  ## Sort the YAML content alphabetically
  yaml_content_sorted = dict(sorted(yaml_content.items()))
  ## Dump the sorted YAML frontmatter to the file
  filepointer.write("---\n")
  yaml.dump(yaml_content_sorted, filepointer, default_flow_style=False, sort_keys=False)
  filepointer.write("---\n")
  ## Write the task status
  task_status = dict_article_info.get("task_status", "u")
  _write_task_status(task_status)


## END OF LIBRARY