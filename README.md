# arXivScraper
arXiv scraper using the arXiv Python API-wrapper: arXiv.py.

# Intructions for AI Evalutation
To use the AI-LLM capabilities, you will need to install some an external program called "Ollama". This is a piece of middleware that lets you host LLMs locally.

## Installing Ollama
### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Mac
Installer https://ollama.com/download/mac

### Windows
Ollama for windows is avaliable at https://ollama.com/download/windows howeever it is in beta (as of last time I checked), so my prefered method is to install Windows Subsystem for Linux (WSL), via
```batch
wsl --install
```

Then opening it 
```batch
wsl
```

Then following Linux directions. 

## Pull a model
Ollama has a whole bunch of models to pick from. My reccomendation is Llama3 8b. This can be downloaded.
```
ollama pull llama3.1:8b
```

If you choose another model, ensure you update the config. 

### Picking other models.
I reccomend Llama3 8b because it balences system requirements with performance. The model takes about 45s per article on my laptop. For more intelligent reccomendation, try a larger model. e.g. `mistral-nemo:12b`. If you want faster performance, and can tolerate dumber reccomendations, consider phi3 mini. 

See the avaliable models at https://ollama.com/library 

## Using the Models
You have already got  everything needed to run the ai capabilityies. You can test out the capabilities by calling your model straight from the command line.
```bash
ollama run llama3
```

You can then talk to it just like ChatGPT. 