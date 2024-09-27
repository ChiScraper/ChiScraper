#!/usr/bin/env python3


## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, time, re, os
import yaml
from MyLibrary import HelperFuncs


## ###############################################################
## SEARCH PARAMETERS
## ###############################################################
# Load configuration from config.yaml
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

OUTPUT_DIRECTORY = config['output_directory']
CONFIG_DIRECTORY = config['config_directory']
CONFIG_MODELNAME = config['ai_model']
HOST = config['host']

## ###############################################################
## HELPER FUNCTIONS
## ###############################################################
def readTextFile(filepath):
  return HelperFuncs.readFile(filepath, expected_file_extension=".txt")


## ###############################################################
## OPERATOR FUNCTION
## ###############################################################

if HOST == "OpenAI":
  from openai import OpenAI
  OpenAI.api_key = os.getenv("OPENAI_API_KEY")
  from ai_eval import evaluateArticle_OpenAI as evaluateArticle
elif HOST == "Ollama":
  import ollama
  from ai_eval import evaluateArticle_Ollama as evaluateArticle
else:
  raise ValueError(f"Host {HOST} not supported")

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
  prompt_rules    = readTextFile(f"{CONFIG_DIRECTORY}/ai_rules.txt")
  prompt_criteria = readTextFile(f"{CONFIG_DIRECTORY}/ai_criteria.txt")
  for article_index, filename in enumerate(list_filenames):
    filepath_file = f"{OUTPUT_DIRECTORY}/{filename}"
    HelperFuncs.print2Terminal(f"({article_index+1}/{num_articles})")
    HelperFuncs.print2Terminal(f"Looking at: {filepath_file}")
    dict_article_info = HelperFuncs.readMarkdownFile2Dict(filepath_file)
    if dict_article_info.get("ai_rating") is not None:
      HelperFuncs.print2Terminal("Skipping because the article has already been rated.\n")
      continue
    time_start = time.time()
    dict_ai_result = evaluateArticle(
      dict_article_info = dict_article_info,
      prompt_rules      = prompt_rules,
      prompt_criteria   = prompt_criteria,
      model=CONFIG_MODELNAME
    )
    time_elapsed = time.time() - time_start
    if not("success" == dict_ai_result["status"].lower()):
      HelperFuncs.print2Terminal("Error: {}".format(dict_ai_result["status"]))
      if "ai_message" in dict_ai_result.keys():
        HelperFuncs.print2Terminal("LLM response:\n{}".format(dict_ai_result["ai_message"]))
    else:
      HelperFuncs.print2Terminal("Rating: {}".format(dict_ai_result['ai_rating']))
      dict_article_info["ai_rating"] = dict_ai_result["ai_rating"]
      dict_article_info["ai_reason"] = dict_ai_result["ai_reason"]
      HelperFuncs.saveArticle(OUTPUT_DIRECTORY, dict_article_info)
    HelperFuncs.print2Terminal(f"Elapsed time: {time_elapsed:.2f} seconds.\n")


## ###############################################################
## PROGRAM ENTRY POINT
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit(0)


## END OF PROGRAM