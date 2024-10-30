## ###############################################################
## LOAD MODULES
## ###############################################################
import os, re, yaml, unidecode

from src.headers import Directories
from src.headers import WWFnFs
from src.headers import WWLists
from src.headers import IO
from src.headers import WWDates


## ###############################################################
## HELPER FUNCTION
## ###############################################################
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


## ###############################################################
## PRINT ARTICLE CONTENTS
## ###############################################################
def printArticle(dict_article, num_pad_chars=13):
  ## helper function
  def _printLine(category, content):
    if isinstance(content, list): content = ", ".join(content)
    category = f"{category}".ljust(num_pad_chars)
    print(f"{category}: {content}")
  ## print article information
  ## debug: printDict(dict_article)
  _printLine("Title",        dict_article["title"])
  _printLine("PDF URL",      dict_article["url_pdf"])
  _printLine("Date Updated", WWDates.castDate2String(dict_article["date_updated"]))
  _printLine("Author(s)",    dict_article["authors"])
  return


## ###############################################################
## SAVE FILE TO MARKDOWN
## ###############################################################
def writeArticleContent2File(filepointer, dict_article):
  ## helper functions
  def _formatListIfDefined(content):
    if not content: return None
    return content
  ## prepare the YAML frontmatter
  yaml_content = {
    "title":            formatText(dict_article["title"]),
    "arxiv_id":         dict_article["arxiv_id"],
    "url_pdf":          dict_article["url_pdf"],
    "date_published":   WWDates.castDate2String(dict_article["date_published"]),
    "date_updated":     WWDates.castDate2String(dict_article["date_updated"]),
    "category_primary": dict_article["category_primary"],
    "category_others":  _formatListIfDefined(dict_article.get("category_others")),
    "config_tags":      _formatListIfDefined(dict_article.get("config_tags")),
    "authors":          dict_article.get("authors"),
    "abstract":         formatText(dict_article["abstract"]),
  }
  ## optional keys handling (these can be lists, booleans, or strings)
  list_optional_key_conditions = [
    "config_reason_",
    "ai_rating",
    "ai_reason",
  ]
  ## dynamically add optional keys to YAML content
  for key, value in dict_article.items():
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
  task_status = dict_article.get("task_status", "u")
  filepointer.write(f" - [{task_status}] #task status\n")
  return

def saveArticle2Markdown(dict_article, bool_verbose=True):
  filename = dict_article["arxiv_id"] + ".md"
  filepath_file = f"{Directories.directory_mdfiles}/{filename}"
  if WWFnFs.fileExists(filepath_file):
    _dict_article = readMarkdownFile2Dict(filepath_file)
    _task_status = _dict_article["task_status"]
    ## if the article has already been assessed, don't overwrite it
    if _task_status in [ "D", "-" ]:
      if _task_status == "D": print("The following article has already been downloaded:")
      if _task_status == "-": print("The following article has already been ignored:")
      printArticle(dict_article)
      input_save = input("Do you want to save it again? (y/n): ")
      print(" ")
      if input_save[0].lower() != "y": return
    ## retain the task status
    dict_article["task_status"] = _task_status
    ## merge `config_tags`: only add unique tags from `_dict_article`
    if "config_tags" in _dict_article:
      dict_article["config_tags"] = list(
        set(dict_article.get("config_tags", [])) | set(_dict_article.get("config_tags", []))
      )
    ## retain `ai_rating` only if it is not None
    if _dict_article.get("ai_rating") is not None:
      dict_article["ai_rating"] = _dict_article.get("ai_rating")
    ## retain `ai_reason` only if it is not None
    if _dict_article.get("ai_reason") is not None:
      dict_article["ai_reason"] = _dict_article.get("ai_reason")
    ## merge `config_reason_*` keys from `_dict_article` if they don't already exist in `dict_article`
    for key, value in _dict_article.items():
      if key.startswith("config_reason_") and key not in dict_article:
        dict_article[key] = value
  ## overwrite the file if it exists, but retain the Obsidian task status and search category tags
  with open(filepath_file, "w") as filepointer:
    writeArticleContent2File(filepointer, dict_article)
  if bool_verbose: print(f"Saved: {filepath_file}")
  return


## ###############################################################
## EXTRACT + COMBINE ARTICLE INFORMATION
## ###############################################################
def getArticleSummaryDict(dict_arxiv, dict_config_results={}, dict_ai_results={}, task_status="u"):
  list_authors = [
    unidecode.unidecode(str(author))
    for author in WWLists.shortenList(dict_arxiv.authors)
  ]
  list_other_categories = [
    formatText(elem)
    for elem in WWLists.shortenList(dict_arxiv.categories)
    if (elem != dict_arxiv.primary_category)
  ]
  list_config_tags = [
    f"#{key}" if ("#" not in key) else key
    for key in dict_config_results.keys()
  ]
  dict_article = {
    "title"               : formatText(dict_arxiv.title),
    "arxiv_id"            : dict_arxiv.pdf_url.split("/")[-1].split("v")[0],
    "url_pdf"             : dict_arxiv.pdf_url,
    "authors"             : list_authors,
    "abstract"            : formatText(dict_arxiv.summary),
    "date_published"      : dict_arxiv.published.date(),
    "date_updated"        : dict_arxiv.updated.date(),
    "category_primary"    : dict_arxiv.primary_category,
    "category_others"     : list_other_categories,
    "config_tags"         : list_config_tags,
    "task_status"         : task_status,
  }
  for config_tag, list_bool_reasons in dict_config_results.items():
    dict_article[f"config_reason_{config_tag}"] = list_bool_reasons
  for ai_key, ai_value in dict_ai_results.items():
    if   ai_key == "ai_rating": dict_article["ai_rating"] = ai_value
    elif ai_key == "ai_reason": dict_article["ai_reason"] = ai_value
  return dict_article


## ###############################################################
## READ MARKDOWN (ARTICLE) FILES
## ###############################################################
def readMarkdownFile2Dict(md_file):
  content = IO.readMarkdownFile(md_file)
  ## split the file into frontmatter (YAML) and body (markdown)
  match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
  if match:
    frontmatter_content = match.group(1)
    body = match.group(2)
  else: raise ValueError("Missing frontmatter section in the Markdown file.")
  ## parse the YAML frontmatter
  try:
    metadata = yaml.safe_load(frontmatter_content)
  except yaml.YAMLError as e: raise ValueError(f"Error parsing YAML frontmatter: {e}")
  ## ensure all required keys are present in the metadata
  missing_keys = [
    key
    for key in [
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
    if key not in metadata
  ]
  if missing_keys: raise ValueError("Missing required keys in frontmatter:", ", ".join(missing_keys))
  ## extract all config_reason_* keys
  config_reasons = {
    k: v
    for k, v in metadata.items()
    if k.startswith("config_reason_")
  }
  ## find the character inside the brackets [] on the same line as `#task`
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
    "date_published"   : WWDates.castString2Date(metadata.get("date_published")),
    "date_updated"     : WWDates.castString2Date(metadata.get("date_updated")),
    "category_primary" : metadata.get("category_primary"),
    "category_others"  : metadata.get("category_others", None),
    "config_tags"      : metadata.get("config_tags", []),
    "ai_rating"        : metadata.get("ai_rating", None),
    "ai_reason"        : metadata.get("ai_reason", None),
    "task_status"      : task_status,
    **config_reasons
  }
  return dict(sorted(properties.items()))

def readAllMarkdownFiles():
  list_filenames = [
    filename
    for filename in os.listdir(Directories.directory_mdfiles)
    if filename.endswith(".md")
  ]
  list_article_dicts = []
  for filename in list_filenames:
    filepath_file = f"{Directories.directory_mdfiles}/{filename}"
    dict_article = readMarkdownFile2Dict(filepath_file)
    list_article_dicts.append(dict_article)
  return list_article_dicts


## END OF HEADER FILE