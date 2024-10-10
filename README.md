# Chi_Scraper

This application is designed to search for academic articles from the ArXiv repository, rank them based on relevance, and display the results in a web browser. It leverages LLLMs running locally or on the cloud to enhance the search and ranking processes.

## Key Scripts

1. **`searchArxiv.py`**: This script pulls articles from ArXiv using a keyword matching algorithm. It reads configurations from `cofig.nyaml` to determine search criteria and output settings.

2. **`rank_articles.py`**: This script assigns relevance scores to the articles retrieved by `searchArxiv.py`. It uses AI models specified in the configuration to evaluate the relevance of each article.

3. **`app.py`**: This script displays the articles in a web browser, providing an interactive interface for users to explore the search results.

## Configuration

The application is configured using the `config.yaml` file. Key settings include:

- **`ai_model`**: Specifies the AI model to use for ranking.
- **`host`**: Indicates whether to use OpenAI's servers or run the AI locally.
- **`config_directory`**: Directory where configuration files are stored.
- **`output_directory`**: Directory where markdown files for each article are saved.
- **`config_modelname`**: Which keyword matching file should be used
- **lookback_date**: How many days backwards to search the ArXiv

## Getting Started

1. **Install Dependencies**: Ensure all necessary Python packages and external tools (like Ollama for local AI hosting) are installed.

## ChiScraper Dependancies
```bash
python -m venv .venv
# For Mac/Linux
source ./.venv/bin/actiivate
# For Windows
.venv/Scripts/Activate.ps1`

pip install -r ./requirements.txt
```
If you want to run the LLM locally, follow instructions on  `helpFiles\localAIEval.md`


2. **Configure the Application**: Edit `config.yaml` to set your preferences for search criteria, AI model, and output settings.

3. **Run the Scripts**:
   - Execute `searchArxiv.py` to fetch articles.
   - Run `rank_articles.py` to rank the articles based on relevance.
   - Launch `app.py` to view the articles in your web browser.

## Additional Resources

- **AI Ranking**: For more details on running the AI ranking algorithm, refer to `helpFiles/aiRanking.md`.
- **Local AI Evaluation**: Instructions for setting up local AI evaluation are available in `helpFiles/localAIEval.md`.
- **Search Configuration**: Learn about configuring search criteria in `helpFiles/searchConfig.md`.

By following these steps and utilizing the provided scripts, you can efficiently search, rank, and explore academic articles tailored to your research needs.