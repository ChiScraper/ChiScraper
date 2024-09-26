#!/usr/bin/env python3


## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, os, requests
from MyLibrary import HelperFuncs


## ###############################################################
## SEARCH PARAMETERS
## ###############################################################
DIRECTORY_MD  = "/Users/necoturb/Library/CloudStorage/OneDrive-Personal/Obsidian/arXiv-articles"
DIRECTORY_PDF = "/Users/necoturb/Library/CloudStorage/OneDrive-Personal/Obsidian/arXiv-articles"


## ###############################################################
## HELPER FUNCTIONS
## ###############################################################
def downloadPDF(url_pdf, directory, filename):
  HelperFuncs.createFolder(directory)
  filepath_file = os.path.join(directory, filename)
  try:
    response = requests.get(url_pdf, stream=True)
    response.raise_for_status()
    with open(filepath_file, 'wb') as file:
      for chunk in response.iter_content(chunk_size=8192):
        file.write(chunk)
    print(f"Downloaded: {filepath_file}")
  except requests.RequestException as e: print(f"Error downloading file: {e}")


## ###############################################################
## MAIN PROGRAM
## ###############################################################
def main():
  list_filenames_in_directory = os.listdir(DIRECTORY_MD)
  list_filenames = [
    filename
    for filename in list_filenames_in_directory
    if filename.endswith(".md")
  ]
  num_articles = len(list_filenames)
  for article_index, filename in enumerate(list_filenames):
    filepath_file = f"{DIRECTORY_MD}/{filename}"
    HelperFuncs.print2Terminal(f"({article_index+1}/{num_articles})")
    HelperFuncs.print2Terminal(f"Looking at: {filepath_file}")
    dict_article_info = HelperFuncs.readMarkdownFile2Dict(filepath_file)
    task_status = dict_article_info.get("task_status", None)
    if task_status == "d":
      HelperFuncs.printDict2Terminal(dict_article_info)
      url_pdf = dict_article_info["url_pdf"]
      arxiv_id = dict_article_info["arxiv_id"]
      filename_pdf = f"{arxiv_id}.pdf"
      downloadPDF(url_pdf, DIRECTORY_PDF, filename_pdf)
      dict_article_info["task_status"] = "D"
      with open(filepath_file, "w") as filepointer:
        HelperFuncs.writeArticle2File(filepointer, dict_article_info)
      HelperFuncs.print2Terminal(f"Downloaded: {filename}\n")


## ###############################################################
## PROGRAM ENTRY POINT
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit(0)


## END OF PROGRAM