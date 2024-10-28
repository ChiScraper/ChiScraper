#!/usr/bin/env python3


## ###############################################################
## LOAD MODULES
## ###############################################################
import os, sys, unidecode
import numpy as np

from collections import Counter


## ###############################################################
## PREPARE WORKSPACE
## ###############################################################
os.system("clear")


## ###############################################################
## HELPER FUNCTIONS
## ###############################################################
def loopOverAllArticles():
  return

def getAuthorNamesFromFile(filepath_input_file):
  ## helper function
  def getName(author):
    name = ""
    for elem in author.split(" ")[:-1]:
      if len(elem) == 0: continue
      if elem == "-": continue
      elem_uni = unidecode.unidecode(elem.replace("-", ""))
      if ("a" < elem_uni[0]) and (elem_uni[0] < "z"):
        name += f"{elem_uni} "
      else: name += f"{elem_uni[0]}. "
    name += unidecode.unidecode(author.split(" ")[-1]).capitalize()
    return name
  ## create list of author names
  list_author_names = []
  with open(filepath_input_file, "r") as txt_file:
    for line in txt_file:
      if len(line) > 0 and line.split(":")[0] == "Author(s)":
        list_author_names += [
          getName(author.replace("\n", ""))
          for author in line.split(":")[1].split(", ")
        ]
  return list_author_names

def getArticleTitles(filepath_input_file):
  list_words_exclude = [
    "of", "the", "in", "a", "and", "by", "on", "to", "from", "with", "for"
  ]
  list_titles = [ ]
  with open(filepath_input_file, "r") as txt_file:
    for line in txt_file:
      if len(line) > 0 and line.split(":")[0] == "Title":
        list_title_words = [
          word.replace("\n", "").replace(",", "").lower()
          for word in line.split(":")[1].split(" ")
          if len(word) > 0
        ]
        list_titles.extend(
          word
          for word in list_title_words
          if (word not in list_words_exclude) and ("\\" not in word)
        )
  return list_titles

def getArticleCategories(filepath_input_file):
  list_categories = [ ]
  with open(filepath_input_file, "r") as txt_file:
    for line in txt_file:
      if (len(line) > 0) and (":" in line):
        if "categor" in line.split(":")[0]:
          list_categories.extend(
            word.replace("\n", "").replace(" ", "")
            for word in line.split(":")[1].split(", ")
            if len(word.replace("\n", "").replace(" ", "")) > 0
          )
  return list_categories

def printWordFreq(list_words, min_count=0, str_type="word", bar_num_chars=50):
  counts = Counter(list_words)
  print(" ")
  print("The popular {} is '{}'. It occured {} times.\n".format(
    str_type,
    counts.most_common(1)[0][0],
    counts.most_common(1)[0][1]
  ))
  max_count = counts.most_common(1)[0][1]
  scale = bar_num_chars / float(max_count)
  max_count_length = int(np.log10(max_count))
  max_name_length = max(len(word) for word in list_words)
  for name, count in sorted(
      counts.items(),
      ## reorder sort: (1) frequency, (2) alphabetical
      key = lambda item: (-item[1], item[0])
    ):
    if count >= min_count:
      bar = int(count * scale) * "*"
      print(
        f"({str(count)})".ljust(max_count_length+3),
        f"{name.ljust(max_name_length+1)}",
        f"{bar}"
      )
  ## create trailing empty space
  print(" ")


## ###############################################################
## MAIN PROGRAM
## ###############################################################
BOOL_AUTHOR     = 1
BOOL_TITLE      = 1
BOOL_CATEGORIES = 1

def main():
  filename = "arxiv 2024-07-08 to 2024-07-01 (mhd) [1 1 0].txt"
  ## define path to file
  filepath_program    = os.path.dirname(os.path.realpath(__file__))
  filepath_input_file = f"{filepath_program}/Output/{filename}"
  ## extract information about articles
  list_author_names   = getAuthorNamesFromFile(filepath_input_file)
  list_titles         = getArticleTitles(filepath_input_file)
  print("Started analysis.")
  if BOOL_AUTHOR:
    printWordFreq(
      list_words = list_author_names,
      str_type   = "author name",
      min_count  = 2
    )
  if BOOL_TITLE:
    printWordFreq(
      list_words = list_titles,
      str_type   = "word in the titles",
      min_count  = 2
    )
  print(" ")
  print("Finished analysis.")


## ###############################################################
## PROGRAM ENTRY POINT
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit()


## END OF PROGRAM