
# Quickstart

1. Install Ollama from `https://ollama.com/`
2. Pull Llama3.1 8b
```bash
ollama pull llama3.18b
```
3. Edit `host` and `ai_model` in the config

```yaml
host: local
ai_model: llama3.1:8b
```

**Detailed instructions and configuration below**

# Intructions for AI Evalutation
To use the AI-LLM capabilities, you will need to install some an external program called "Ollama". This is a piece of middleware that lets you host LLMs locally.

## Installing Ollama
### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Mac
Install from https://ollama.com/download/mac and follow the setup instructions in the app.

### Windows
Ollama for windows is avaliable at https://ollama.com/download/windows. 

## Verify Ollama is running. 
Navigating to http://localhost:11434 in your web browser will tell you if it is running correctly. 

## Pull a model
Ollama has a whole bunch of models to pick from. My reccomendation is Llama3 8b. This can be downloaded.
```
ollama pull llama3.1:8b
```

If you choose another model, ensure you update the config. 

### Picking other models.
I reccomend Llama3 8b because it balences system requirements with performance. The model takes about 45s per article on my laptop. For more intelligent reccomendation, try a larger model. e.g. `mistral-nemo:12b`. If you want faster performance, and can tolerate dumber reccomendations, consider phi3 mini. 

See the avaliable models at https://ollama.com/library 

# Configuring Chi-Scraper
Within `config.yaml` set the host to `local` and the `ai_model` to whichever model you have downloaded and plan on using. 

```yaml
host: local
ai_model: llama3.1:8b
```