## ###############################################################
## LOAD MODULES
## ###############################################################
import os, sys, re, time, openai

from src.headers import Directories
from src.headers import FileNames
from src.headers import IO
from src.headers import WWArticles


## ###############################################################
## GLOBAL PARAMETERS
## ###############################################################
openai.OpenAI.api_key = os.getenv("OPENAI_API_KEY")


## ###############################################################
## REQUEST GPT TO SCORE ARTICLE
## ###############################################################
def getAIResponse(dict_article, prompt_rules, prompt_criteria):
  article_title    = dict_article.get("title", "")
  article_abstract = dict_article.get("abstract", "")
  if (article_title == ""):
     return {
      "status"    : "Missing article title",
      "ai_rating" : None,
      "ai_reason" : None
    }
  if (article_abstract == ""):
    return {
      "status"    : "Missing article abstract",
      "ai_rating" : None,
      "ai_reason" : None
    }
  prompt_input = f"{prompt_criteria} \n\nTITLE: {article_title}\n\nABSTRACT: {article_abstract}"
  try:
    client = openai.OpenAI()
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
    re_pattern = r"(?i)JUSTIFICATION:\s*(.*)\s*RATING:\s*([\d.]+)"
    match = re.search(re_pattern, response_text)
    if match:
      ai_reason = match.group(1).strip()
      ai_rating = float(match.group(2).strip())
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
## FUNCTION TO INTERPRET AI RESPONSE
## ###############################################################
def getAIScore(dict_article, prompt_rules, prompt_criteria, bool_score_all=False):
  if not(bool_score_all) and not(dict_article.get("ai_rating") is None):
    print("Skipping because the article has already been scored.")
    return False
  time_start = time.time()
  dict_ai_score = getAIResponse(
    dict_article    = dict_article,
    prompt_rules    = prompt_rules,
    prompt_criteria = prompt_criteria,
  )
  time_elapsed = time.time() - time_start
  if not("success" == dict_ai_score["status"].lower()):
    print("Error:", dict_ai_score["status"])
    if "ai_message" in dict_ai_score.keys():
      print("LLM response:")
      print(dict_ai_score["ai_message"])
    print("Error: something went wrong with resquesting a LLM score.")
    return False
  print("arXiv-id:", dict_article["arxiv_id"])
  print("Title:", dict_article["title"])
  print("Rating:", dict_ai_score['ai_rating'])
  dict_article["ai_rating"] = dict_ai_score["ai_rating"]
  dict_article["ai_reason"] = dict_ai_score["ai_reason"]
  print(f"Elapsed time: {time_elapsed:.2f} seconds.")
  return True


## ###############################################################
## MAIN PROGRAM
## ###############################################################
def main():
  list_article_dicts = WWArticles.readAllMarkdownFiles()
  prompt_rules       = IO.readTextFile(f"{Directories.directory_config}/{FileNames.filename_ai_rules}")
  prompt_criteria    = IO.readTextFile(f"{Directories.directory_config}/{FileNames.filename_ai_criteria}")
  num_articles       = len(list_article_dicts)
  for article_index, dict_article in enumerate(list_article_dicts):
    print(f"({article_index+1}/{num_articles})")
    bool_scored = getAIScore(
      dict_article    = dict_article,
      prompt_rules    = prompt_rules,
      prompt_criteria = prompt_criteria,
      bool_score_all  = True,
    )
    if bool_scored: WWArticles.saveArticle2Markdown(dict_article)
    print(" ")


## ###############################################################
## PROGRAM ENTRY POINT
## ###############################################################
if __name__ == "__main__":
  main()
  sys.exit(0)


## END OF PROGRAM