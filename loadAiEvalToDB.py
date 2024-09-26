import yaml
import os
from MyLibrary import HelperFuncs
from articleDB import ArticleDatabase

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

print(f"HOST: {HOST}")
print(f"CONFIG_DIRECTORY: {CONFIG_DIRECTORY}")
print(f"OUTPUT_DIRECTORY: {OUTPUT_DIRECTORY}")
print(f"CONFIG_MODELNAME: {CONFIG_MODELNAME}")

# Setup LLM Client
if HOST == "OpenAI":
  from openai import OpenAI
  OpenAI.api_key = os.getenv("OPENAI_API_KEY")

  from ai_eval import evaluateArticle_OpenAI as evaluateArticle
  print(f"OpenAI client initialized") 
elif HOST == "Ollama":
  import ollama
  from ai_eval import evaluateArticle_Ollama as evaluateArticle
  print(f"Ollama client initialized") 
else:
  raise ValueError(f"Host {HOST} not supported")

## ###############################################################
## MAIN
## ###############################################################

def main():
    userPrompt   = HelperFuncs.readFile(f"{CONFIG_DIRECTORY}/ai_rules.txt",expected_file_extension=".txt")
    systemPrompt = HelperFuncs.readFile(f"{CONFIG_DIRECTORY}/ai_criteria.txt",expected_file_extension=".txt")
    articleDB = ArticleDatabase()

    list_filenames_in_directory = os.listdir(OUTPUT_DIRECTORY)
    list_filenames = [
        filename
        for filename in list_filenames_in_directory
        if filename.endswith(".md")
    ]
    num_articles    = len(list_filenames)


    # Get unranked articles from database
    # unranked_articles = articleDB.find_unranked_articles()
    # print(f"Number of unranked articles: {len(unranked_articles)}")

    print("-"*100)
    for i, filename in enumerate(list_filenames):
        print(f"Evaluating article {i+1} of {num_articles}")
        ArXivID = os.path.splitext(filename)[0]
        print(f"ArXivID: {ArXivID}")
        # Get title and abstract
        metadata = articleDB.get_article_metadata_by_arxiv_id(ArXivID)
        try:
            articleInfo = {
                "title": metadata['title'],
                "abstract": metadata['abstract']
            }
            print(f"Title: {articleInfo['title']}")
        except Exception as e:
            print(f"Error getting article info: {e}, \n for article {filename}")
            continue

        # Get AI evaluation
        try:    
            evaluation = evaluateArticle(articleInfo, userPrompt, systemPrompt,CONFIG_MODELNAME)
        except Exception as e:
            print(f"Evaluation failed: {e}")
            continue
        if evaluation["status"] == "success":
            # Add AI evaluation to article
            articleDB.add_article_rating(ArXivID,
                                         ai_rating=evaluation["ai_rating"],
                                         ai_reason=evaluation["ai_reason"])
            print("-"*100)
        else:
            print(f"Evaluation failed: {evaluation['status']}")

if __name__ == "__main__":
    main()




