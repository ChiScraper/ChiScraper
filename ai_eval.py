import re
import ollama
import openai
from openai import OpenAI
import json


# This is the LLM model to use. Make sure it is installed on your system
model = "llama3:latest"
# model = "phi3.5:latest"    
# model = "mistral-nemo"

configPath = "./Configs/FSOC.json" # This will need to change



def load_prompts(json_path):
    """ 
    Grabs the user and system prompts from a json file
    """
    # Get the filepath for the directory containing the json file
    directory = json_path[:json_path.rfind('/')]
    # Step 1: Open the JSON file
    with open(json_path, 'r') as file:
        # Step 2: Load the JSON data
        data = json.load(file)
    # Step 3: Find the file paths for user_prompt and system_prompt
    user_prompt_path = f"{directory}/{data.get('user_prompt')}"
    system_prompt_path = f"{directory}/{data.get('system_prompt')}"


    # Step 4: Load the content of user_prompt and system_prompt files
    with open(user_prompt_path, 'r') as file:
        user_prompt = file.read()
    with open(system_prompt_path, 'r') as file:
        system_prompt = file.read()
    # Return the prompts as strings
    return user_prompt, system_prompt

## ###############################################################
## OPERATOR FUNCTION
## ###############################################################

def evaluateArticle_OpenAI(dict_article_info, prompt_rules, prompt_criteria,model):
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
      model    = model,
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
    pattern = r"(?i)JUSTIFICATION:\s*(.*)\s*RATING:\s*([\d.]+)"
    match = re.search(pattern, response_text)
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

def evaluateArticle_Ollama(dict_article_info, prompt_rules, prompt_criteria,model):
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
    response = ollama.chat(model, messages =[
      {"role": "system", "content": prompt_rules},
    {"role": "user", "content": prompt_input}
    ])
    response_text = response['message']['content']
  except Exception as e:
    return {
      "status"    : f"API call failed: {e}",
      "ai_rating" : None,
      "ai_reason" : None
    }
  try:
    pattern = r"(?i)JUSTIFICATION:\s*(.*)\s*RATING:\s*([\d.]+)"
    match = re.search(pattern, response_text)
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




def example():
    import time
    import os

    # Get all files in the articles directory
    articles = os.listdir("./articles")
    # Filter out anything NOT markdown files
    articles = [article for article in articles if article.endswith('.md')]

    # Load the user and system prompts
    userPrompt, systemPrompt = load_prompts(configPath)

    # Enter into main loop
    for i,article in enumerate(articles):
        articlePath = f"./articles/{article}"
        print(f"Processing article {i+1}/{len(articles)}")
        print(f"Article: {articlePath}")

        # Check if the article already has an ai_rating and ai_justification
        with open(articlePath, 'r') as f:
            article = f.read()


        # Since `evaluateArticle` can fail, we will retry a maximum of `maxAttempts` times
        attempts = 0
        # Use a while loop to retry if the evaluation fails.
        while attempts < maxAttempts:
            attempts += 1 # increment attempts
            # start timer
            start = time.time()
            # This is the bit which actually calls the LLM
            rating, justification = evaluateArticle(articlePath,systemPrompt,userPrompt)
            end = time.time()
            print(f"time taken: {round(end-start,3)}s")
            if rating and justification:
                print(f"Rating: {rating}")
                print(f"Justification: {justification}")
                ### INSERT INTO MARKDOWN HERE


                break
            elif attempts < maxAttempts:
                # If rating and justification are None, and we have not reached maxAttempts, retry
                print("Failed to evaluate article, retrying...")
            else:
                # If rating and justification are None, and we have reached maxAttempts, skip to next article
                print("Failed to evaluate article, skipping to next article")
                break
        
        
if __name__ == "__main__":
    example()
    