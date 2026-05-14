from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from smolagents import tool
import os

# Helsinki-NLP for Translation
tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-mul")
translator = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-mul")

# SpaCy model for Spanish NLP
try:
    import es_core_news_sm
    nlp = es_core_news_sm.load()
except ImportError:
    os.system("python -m spacy download es_core_news_sm")
    import es_core_news_sm
    nlp = es_core_news_sm.load()


# define tools for the agents
@tool
def translate(text: str) -> str:
    """
    Translates English text to Spanish using a Seq2Seq model.

    Args:
        text: The English text string that needs to be translated.
    """

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to("cpu")
    output_tokens = translator.generate(**inputs)
    translation = tokenizer.decode(output_tokens[0], skip_special_tokens=True)
    return translation

@tool
def count_words(text: str) -> int:
    """
    Counts the number of alphabetic words in a given string.

    Args:
        text: The Spanish translation string to count words from.
     """
    abstract = nlp(text)
    # Note the fix: token.is_alpha (with underscore)
    word_n = len([token for token in abstract if token.is_alpha])
    return word_n