## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, requests

from src.headers import Directories
from src.headers import WWFnFs
from src.headers import WWArticles


## ###############################################################
## DOWNLOAD ARXIV PDF
## ###############################################################
def downloadPDF(dict_article):
  arxiv_id     = dict_article["arxiv_id"]
  filepath_pdf = f"{Directories.directory_pdfs}/{arxiv_id}.pdf"
  filepath_md  = f"{Directories.directory_mdfiles}/{arxiv_id}.md"
  ## download arxiv-pdf
  try:
    response = requests.get(dict_article["url_pdf"], stream=True)
    response.raise_for_status()
    with open(filepath_pdf, 'wb') as file:
      for chunk in response.iter_content(chunk_size=8192):
        file.write(chunk)
    print(f"Downloaded: {filepath_pdf}")
  except requests.RequestException as e: print(f"Error downloading file: {e}")
  ## update task status stored in the markdown file
  dict_article["task_status"] = "D"
  with open(filepath_md, "w") as filepointer:
    WWArticles.writeArticleContent2File(filepointer, dict_article)


## ###############################################################
## DOWNLOAD MARKDOWN FILES WITH DOWNLOAD STATUS
## ###############################################################
def downloadPDFs(list_article_dicts):
  num_articles = len(list_article_dicts)
  for article_index, dict_article in enumerate(list_article_dicts):
    print(f"({article_index+1}/{num_articles})")
    print("arXiv-id:", dict_article["arxiv_id"])
    print("Title:", dict_article["title"])
    if dict_article.get("task_status", None) == "d": downloadPDF(dict_article)
    else: print("Article does not need to be downloaded.")
    print(" ")


## ###############################################################
## MAIN PROGRAM
## ###############################################################
def main():
  WWFnFs.createDirectory(Directories.directory_pdfs, bool_add_space=True)
  list_article_dicts = WWArticles.readAllMarkdownFiles()
  downloadPDFs(list_article_dicts)


## ###############################################################
## PROGRAM ENTRY POINT
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit(0)


## END OF PROGRAM