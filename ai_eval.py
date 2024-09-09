import re
import ollama
import json


# This is the LLM model to use. Make sure it is installed on your system
model = "llama3:latest"
# model = "phi3.5:latest"    
# model = "mistral-nemo"

configPath = "./Configs/FSOC.json" # This will need to change
maxAttempts = 2



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


def evaluateArticle(markdownArticle,systemPrompt,userPrompt,model="llama3:latest"):
    """
    This function will read the title and abstract from a markdown file
    pass them to the LLM and return the values ai_justification, ai_rating 
    and ai_tags (optional).
    NOTE: This function CAN fail if the LLM does not return the expected output.
    In that case, the function will return None,None
    Usually retrying the function will work.
    """
    with open(markdownArticle, 'r') as f:
        article = f.read()
    # Within article, search for title, by looking for everything in between `title: ` and `\n`
    title = re.search(r'title: (.*)\n', article).group(1)
    # and now the abstract
    abstract = re.search(r'abstract: (.*)\n', article).group(1)

    # Now lets construct the user prompt from the use input and the title and abstract
    userInput = f"{userPrompt} \n TITLE: {title} \n  ABSTRACT: {abstract}"
    # userInput = f"{userPrompt} \n TITLE: {title} "

    # Construct the prompt to feed to the LLM
    messages = [
        {"role": "system", "content": systemPrompt},
        {"role": "user",   "content": userInput }
    ]
    # Call the LLM
    response = ollama.chat(model=model,messages=messages)
    try:
        # Do some regex to extract the rating and justification from the response
        pattern = r'(?i)justification:\s*((?:(?!\nrating:).)*)\s*\nrating:\s*([\d.]+)' 
        match = re.search(pattern,response['message']['content'])
        justification = match.group(1)
        rating = match.group(2)
    except:
        # If for any reason the regex fails,try again 
        print("Failed to extract rating and justification from response")
        print("Printing response...")
        print(response['message']['content'])
        return None,None
    return rating,justification


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
    