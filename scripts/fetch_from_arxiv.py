#!/usr/bin/env python3


## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, arxiv

from header import Directories
from header import WWFnFs
from header import WWArgParse
from header import WWArticles


## ###############################################################
## GET USER INPUT
## ###############################################################
def getUserInput():
  parser = WWArgParse.MyParser(description="Calculate kinetic and magnetic energy spectra.")
  parse_args = parser.add_argument_group(description="Required processing arguments:")
  parse_args.add_argument("-id", type=str, required=True, help="type: %(type)s. arXiv-id in the format `2310.17036`.")
  args = vars(parser.parse_args())
  return args["id"]


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
  WWArticles.printArticle(_dict_article)
  print(" ")
  filepath_file = f"{Directories.directory_mdfiles}/{arxiv_id}.md"
  if WWFnFs.fileExists(filepath_file):
    print(f"Note: this arXiv article has already been saved: {filepath_file}\n")
  input_save = input("Do you want to save this article? (y/n): ")
  if input_save[0].lower() != "y": return None
  input_tag = input("Enter a config tag: ")
  if input_tag == "":
    print("Error: config tag cannot be empty.")
    return None
  if " " in input_tag:
    print("Error: config tag cannot contain spaces.")
    return None
  dict_config_results = { input_tag : [ 1, 0, 0 ] }
  dict_article = WWArticles.getArticleSummaryDict(
    dict_arxiv          = dict_arxiv,
    dict_config_results = dict_config_results
  )
  WWArticles.saveArticle2Markdown(
    directory_output = Directories.directory_mdfiles,
    dict_article     = dict_article,
    bool_verbose     = True,
  )
  return dict_article


## ###############################################################
## MAIN PROGRAM
## ###############################################################
def main():
  arxiv_id = getUserInput()
  WWFnFs.createDirectory(Directories.directory_mdfiles, bool_add_space=True)
  fetchFromArxiv(arxiv_id)


## ###############################################################
## PROGRAM ENTRY POINT
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit(0)


## END OF PROGRAM