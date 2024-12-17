## ###############################################################
## LOAD MODULES
## ###############################################################
import sys, time, datetime, re, os
import logging

from src.headers import Directories
from src.headers import FileNames
from src.headers import IO
from src.headers import WWFnFs
from src.headers import WWDates
from src.headers import WWArgParse
from src.headers import WWArticles
from src.headers import WWDatabase

from src.scripts import search_arxiv as SearchArxiv
from src.scripts import score_article as ScoreArticle
from src.scripts import fetch_from_arxiv as FetchFromArxiv
from src.scripts import download_articles as DownloadArticles
from src.scripts import launch_webapp as WebApp


import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer

## ###############################################################



# Define a function to preprocess the text
def preprocess_text(articleTuple):
    title = articleTuple[1]
    abstract = articleTuple[9]
    text = title + ' ' + abstract
    # Remove punctuation and convert to lowercase
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text.lower())
    return text

# Get the database
dbPath = 'articles.db'
db = WWDatabase.ArticleDatabase(dbPath)

filter_tag = None
show_processed = 'a'
sort_by = 'date'
published_after = None
published_before = None


articles = db.get_articles_list(
    show_processed=show_processed,
)


import spacy

# Load the spaCy English language model with NER capabilities
nlp = spacy.load("en_core_web_sm")



# Function to extract named entities from a given text
def extract_named_entities(text):
    """
    This function uses spaCy's natural language processing capabilities to extract named entities from a given text.

    Parameters:
    text (str): The input text from which named entities will be extracted.

    Returns:
    list: A list of named entities found in the input text, along with their labels.
    """
    doc = nlp(text)
    named_entities = []
    for ent in doc.ents:
        named_entities.append((ent.text, ent.label_))
    return named_entities

def getNounPhrases(text):
    """
    Extracts noun phrases from a given text using spaCy's natural language processing capabilities.

    Parameters:
    text (str): The input text from which noun phrases will be extracted.

    Returns:
    list: A list of noun phrases found in the input text.
    """
    doc = nlp(text)
    noun_phrases = []
    for chunk in doc.noun_chunks:
        noun_phrases.append(chunk.text)
    return noun_phrases

def getVerbs(text):
    """
    Extracts verbs from a given text using spaCy's natural language processing capabilities.

    Parameters:
    text (str): The input text from which verbs will be extracted.

    Returns:
    list: A list of verbs found in the input text.
    """
    doc = nlp(text)
    verbs = []
    for token in doc:
        if token.pos_ == "VERB":
            verbs.append(token.text)
    return verbs
def TallyVerbList(VerbList):
    Tally = {}
    for verb in VerbList:
        if verb in Tally:
            Tally[verb] += 1
        else:
            Tally[verb] = 1
    return Tally

def printTally(Tally, max=10):
    for key in sorted(Tally, key=lambda x: Tally[x], reverse=True)[:max]:
        print(key + ": " + str(Tally[key]))

def TallyNounPhraseList(NounPhraseList):
    Tally = {}
    for nounPhrase in NounPhraseList:
        if nounPhrase in Tally:
            Tally[nounPhrase] += 1
        else:
            Tally[nounPhrase] = 1
    return Tally

# Function to extract named entities from a given text
def extract_named_entities(text):
    doc = nlp(text)
    named_entities = []
    for ent in doc.ents:
        named_entities.append((ent.text, ent.label_))
    return named_entities

NounPhraseList = []
VerbList = []
namedEntries = []

# # Iterate over the list of articles
# for article in articles:
#     text = preprocess_text(article)
#     NounPhraseList.extend(getNounPhrases(text))
#     VerbList.extend(getVerbs(text))
#     namedEntries.extend(extract_named_entities(text))

keywords = []


for article in articles:
    text = preprocess_text(article)
    doc = nlp(text)
    # Extract named entities
    entities = [ent.text for ent in doc.ents]
    # Extract noun chunks
    noun_chunks = [chunk.text for chunk in doc.noun_chunks]
    # Combine entities and noun chunks
    keywords = entities + noun_chunks
    # Print or store the keywords as desired
    keywords.extend(keywords)
    # print(keywords)

# Tally the keywords
TallyKeywords = {}
for keyword in keywords:
    if keyword in TallyKeywords:
        TallyKeywords[keyword] += 1
    else:
        TallyKeywords[keyword] = 1

# Print the top 10 keywords
printTally(TallyKeywords)

# TallyNounPhrases = TallyNounPhraseList(NounPhraseList)
# TallyVerbs = TallyVerbList(VerbList)

# print("Noun Phrases:")
# printTally(TallyNounPhrases)
# # print(TallyNounPhrases)

# print("Verbs:")
# printTally(TallyVerbs)

# print("Named Entities:")    
# print(namedEntries)