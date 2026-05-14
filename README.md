## Abstract Translator

## Description

This program was devised to cover the need for translating academic abstract conserving the number of words of the 
original abstract. It translates abstracts from English to Spanish conserving the number of words established by the 
user (up to 500 words)

It uses `smolagents` library with `gemma3:4b-it-qat` as brain. Given the limitations of the model run locally, 
ToolCallingAgent is applied instead of CodeAgent. The agent uses two tools, one for translating and another for word count. 
Translation uses `Helsinki-NLP/opus-mt-en-mul` for Spanish translation and `es_core_news_sm` for Spanish NLP model. 

The program uses gradio interface.

## Requirements
- Python 3.8+
- gradio
- transformers
- smolagents
- spacy
- litellm
- torch
- sentencepiece

## Models
- `gemma3:4b-it-qat` (via Ollama) — agent reasoning model
- `Helsinki-NLP/opus-mt-en-mul` (via HuggingFace) — English to Spanish translation
- `es_core_news_sm` — Spanish NLP model for accurate word counting

## Installation
pip install -r requirements.txt

## Prerequisites
- [Ollama](https://ollama.com) installed and running
- Run: `ollama pull gemma3:4b-it-qat`

## Usage
python AbstractTranslator.py

Enter the abstract 
Enter the number of words of your translation

## How it works
1. User inputs an English abstract and a target word count via the Gradio interface
2. The agent translates the abstract to Spanish using the Helsinki-NLP translation tool
3. The agent counts the words in the translation using the spaCy-based word count tool
4. If the word count does not match the target, the agent iterates by expanding 
   or condensing the Spanish text using formal academic phrasing
5. The final validated translation is returned to the user
6. 
## File structure
- `AbstractTranslator.py` - main program, run this to launch the app
- `tools.py` - file containing agent tools
- `requirements.txt` — Python dependencies
- `README.md` — this file

