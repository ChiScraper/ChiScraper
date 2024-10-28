# How to run the AI Ranking Algorithm
Currently, you have two choices:
1. Run off OpenAI
2. Run the AI locally. 

Running the reccomendation algorithm on OpenAIs servers and with their models is faster, but you will need to generate an API key and load your account with some credit. Running it locally is easy, but time consuming. 

# OpenAI Quickstart
1. Create an account with OpenAI and generate an API key
2. Save the API key as a Environment Variable `OPENAI_API_KEY` to your system
3. Verify the config
```yaml
host: OpenAI
ai_model: gpt-4o-mini
```

# Ollama Quickstart 
1. Install Ollama from `https://ollama.com/`
2. Pull Llama3.1 8b
```bash
ollama pull llama3.1:8b
```
3. Edit `host` and `ai_model` in the config
```yaml
host: local
ai_model: llama3.1:8b
```
