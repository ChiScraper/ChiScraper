#!/usr/bin/env python3


## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, time, re, os
from openai import OpenAI
from MyLibrary import HelperFuncs


## ###############################################################
## SEARCH PARAMETERS
## ###############################################################
OUTPUT_DIRECTORY = "/Users/necoturb/Library/CloudStorage/OneDrive-Personal/Obsidian/arXiv-articles"
CONFIG_DIRECTORY = "./configs"
CONFIG_MODELNAME = "plasma"


## ###############################################################
## HELPER FUNCTIONS
## ###############################################################
def readTextFile(filepath):
  return HelperFuncs.readFile(filepath, expected_file_extension=".txt")


## ###############################################################
## OPERATOR FUNCTION
## ###############################################################
def evaluateArticle(dict_article_info, prompt_rules, prompt_criteria):
  article_title    = dict_article_info.get("title", "")
  article_abstract = dict_article_info.get("abstract", "")
  if not article_title or not article_abstract:
    return {
      "status"    : "Missing title or abstract",
      "ai_rating" : None,
      "ai_reason" : None
    }
  prompt_input = f"{prompt_criteria} \n\nTITLE: {article_title}\n\nABSTRACT: {article_abstract}"
  try:
    client = OpenAI()
    response = client.chat.completions.create(
      model    = "gpt-4o-mini",
      messages = [
        { "role": "system", "content": prompt_rules },
        { "role": "user",   "content": prompt_input },
      ]
    )
  except Exception as e:
    return {
      "status"    : f"API call failed: {e}",
      "ai_rating" : None,
      "ai_reason" : None
    }
  try:
    response_text = response.choices[0].message.content
    pattern = r"(?i)RATING:\s*([\d.]+)\s*JUSTIFICATION:\s*(.*)"
    match = re.search(pattern, response_text)
    if match:
      ai_rating = float(match.group(1).strip())
      ai_reason = match.group(2).strip()
    else:
      return {
        "status"     : "Failed to extract rating and justification",
        "ai_message" : response_text,
        "ai_rating"  : None,
        "ai_reason"  : None
      }
  except Exception as e:
    return {
      "status"     : f"Parsing error occurred: {e}",
      "ai_message" : response_text,
      "ai_rating"  : None,
      "ai_reason"  : None
    }
  return {
    "status"    : "success",
    "ai_rating" : ai_rating,
    "ai_reason" : ai_reason
  }


## ###############################################################
## MAIN PROGRAM
## ###############################################################
def main():
  OpenAI.api_key = os.getenv("OPENAI_API_KEY")
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
    if "ai_rating" in dict_article_info.keys():
      HelperFuncs.print2Terminal("Skipping because the article has already been rated.\n")
      continue
    time_start = time.time()
    dict_ai_result = evaluateArticle(
      dict_article_info = dict_article_info,
      prompt_rules      = prompt_rules,
      prompt_criteria   = prompt_criteria,
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