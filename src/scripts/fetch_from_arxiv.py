## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, arxiv

from src.headers import Directories
from src.headers import WWFnFs
from src.headers import WWArgParse
from src.headers import WWArticles


## ###############################################################
## FETCH ARTICLE FROM THE ARXIV
## ###############################################################
def fetchFromArxiv(arxiv_id):
  client = arxiv.Client()
  search = arxiv.Search(id_list=[arxiv_id])
  dict_arxiv = next(client.results(search), None)
  if dict_arxiv is None:
    print(f"Error: the arXiv article '{arxiv_id}' does not exist.")
    return None
  _dict_article = WWArticles.getArticleSummaryDict(dict_arxiv)
  print("The article you have requested:")
  WWArticles.printArticle(_dict_article)
  print(" ")
  input_right_article = input("Was this the article you intended to fetch? (y/n): ")
  print(" ")
  if input_right_article[0].lower() != "y": return None
  filepath_file = f"{Directories.directory_mdfiles}/{arxiv_id}.md"
  if WWFnFs.fileExists(filepath_file):
    print(f"Note: this arXiv article has already been saved: {filepath_file}")
    input_save_again = input("Would you like to save it again? (y/n): ")
    print(" ")
    if input_save_again[0].lower() != "y": return _dict_article
  input_tag = input("Enter a config tag: ")
  print(" ")
  if input_tag == "": raise Exception("Error: config tag cannot be empty.")
  if " " in input_tag: raise Exception("Error: config tag cannot contain spaces.")
  dict_config_results = { input_tag : [ 1, 0, 0 ] }
  dict_article = WWArticles.getArticleSummaryDict(
    dict_arxiv          = dict_arxiv,
    dict_config_results = dict_config_results
  )
  WWArticles.saveArticle2Markdown(dict_article)
  return dict_article


## ###############################################################
## MAIN PROGRAM
## ###############################################################
def main():
  obj_user_inputs = WWArgParse.GetUserInputs()
  arxiv_id = obj_user_inputs.getFetchInputs()
  WWFnFs.createDirectory(Directories.directory_mdfiles, bool_add_space=True)
  fetchFromArxiv(arxiv_id)


## ###############################################################
## PROGRAM ENTRY POINT
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit(0)


## END OF PROGRAM