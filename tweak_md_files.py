#!/usr/bin/env python3


## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, os
from MyLibrary import HelperFuncs


## ###############################################################
## SEARCH PARAMETERS
## ###############################################################
OUTPUT_DIRECTORY = "/Users/necoturb/Library/CloudStorage/OneDrive-Personal/Obsidian/arXiv-articles"


## ###############################################################
## HELPER FUNCTION
## ###############################################################
def removeBadConfigTags(dict_article_info):
  for key in dict_article_info.keys():
    if "config_tags" in key:
      list_tags = dict_article_info[key]
      if list_tags is None:
        dict_article_info[key] = [ "#plasma"]
      else:
        dict_article_info[key] = [
          tag
          for tag in list_tags
          if ('"#' not in tag) and ("'#" not in tag)
        ]


## ###############################################################
## MAIN PROGRAM
## ###############################################################
def main():
  list_filenames_in_directory = os.listdir(OUTPUT_DIRECTORY)
  list_filenames = [
    filename
    for filename in list_filenames_in_directory
    if filename.endswith(".md")
  ]
  num_articles = len(list_filenames)
  for article_index, filename in enumerate(list_filenames):
    filepath_file = f"{OUTPUT_DIRECTORY}/{filename}"
    HelperFuncs.print2Terminal(f"({article_index+1}/{num_articles})")
    HelperFuncs.print2Terminal(f"Looking at: {filepath_file}")
    dict_article_info = HelperFuncs.readMarkdownFile2Dict(filepath_file)
    removeBadConfigTags(dict_article_info)
    with open(filepath_file, "w") as filepointer:
      HelperFuncs.writeArticle2File(filepointer, dict_article_info)
    HelperFuncs.print2Terminal(f"Updated: {filename}\n")


## ###############################################################
## PROGRAM ENTRY POINT
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit(0)


## END OF PROGRAM