#!/usr/bin/env python3


## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, time, re, os
import openai
from MyLibrary import HelperFuncs

## ###############################################################
## SEARCH PARAMETERS
## ###############################################################
OUTPUT_DIRECTORY = "/Users/necoturb/Library/CloudStorage/OneDrive-Personal/Obsidian/arXiv-articles"
CONFIG_DIRECTORY = "./configs"
CONFIG_MODELNAME = "plasma"

openai.api_key = os.getenv('OPENAI_API_KEY')


# ## ###############################################################
# ## OPERATOR FUNCTION
# ## ###############################################################
# def evaluateArticle(markdownArticle, prompt_rules, prompt_criteria):
#   with open(markdownArticle, "r") as f:
#     article = f.read()
#   article_title = re.search(r"title: (.*)\n", article).group(1)
#   article_abstract = re.search(r"abstract: (.*)\n", article).group(1)
#   prompt_input = f"{prompt_criteria} \n TITLE: {article_title} \n ABSTRACT: {article_abstract}"
#   response = openai.OpenAI().chat.completions.create(
#     model    = "gpt-4o-mini",
#     messages = [
#       {
#         "role"    : "system",
#         "content" : prompt_rules
#       },
#       {
#         "role"    : "user",
#         "content" : prompt_input
#       }
#     ]
#   )
#   justification = None
#   rating = None
#   try:
#     pattern = r"(?i)justification:\s*((?:(?!\nrating:).)*)\s*\nrating:\s*([\d.]+)" 
#     match = re.search(pattern, response["message"]["content"])
#     justification = match.group(1)
#     rating = match.group(2)
#   except:
#     print("Failed to extract rating and justification from response")
#     print("Printing response...")
#     print(response["message"]["content"])
#   return rating, justification


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
  num_articles    = len(list_filenames)
  prompt_rules    = HelperFuncs.readFile(f"{CONFIG_DIRECTORY}/ai_rules.txt", file_extension=".txt")
  prompt_criteria = HelperFuncs.readFile(f"{CONFIG_DIRECTORY}/{CONFIG_MODELNAME}.txt", file_extension=".txt")
  HelperFuncs.print2Terminal("OpenAI API Key:")
  HelperFuncs.print2Terminal(openai.api_key)
  HelperFuncs.print2Terminal(" ")
  HelperFuncs.print2Terminal("AI Rules:")
  HelperFuncs.print2Terminal(prompt_rules)
  HelperFuncs.print2Terminal(" ")
  HelperFuncs.print2Terminal("Article Criteria:")
  HelperFuncs.print2Terminal(prompt_criteria)
  HelperFuncs.print2Terminal(" ")
  for article_index, filename in enumerate(list_filenames):
    filepath_file = f"{OUTPUT_DIRECTORY}/{filename}"
    HelperFuncs.print2Terminal(f"({article_index+1}/{num_articles})")
    HelperFuncs.print2Terminal(f"Article: {filepath_file}")
    dict_article = HelperFuncs.readArticleMarkdownFile2Dict(filepath_file)
    HelperFuncs.printDict2Terminal(dict_article)
    HelperFuncs.print2Terminal(" ")
    break
    # time_start = time.time()
    # rating, justification = evaluateArticle(
    #   filepath_file,
    #   system_prompt,
    #   user_prompt
    # )
    # time_elapsed = time.time() - time_start
    # HelperFuncs.print2Terminal(" ")
    # HelperFuncs.print2Terminal(f"Elapsed time: {time_elapsed:.2f} seconds.")
    # if rating and justification:
    #   HelperFuncs.print2Terminal(f"Article: {filename}")
    #   HelperFuncs.print2Terminal(f"Rating: {rating}")
    #   HelperFuncs.print2Terminal(f"Justification: {justification}")
    #   HelperFuncs.print2Terminal(" ")
    #   ### INSERT INTO MARKDOWN HERE
    #   break


## ###############################################################
## PROGRAM ENTRY POINT
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit(0)


## END OF PROGRAM