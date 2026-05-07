# imports
import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import spacy
from smolagents import tool, ToolCallingAgent, LiteLLMModel


# SpaCy model for Spanish NLP
try:
    import es_core_news_sm

    nlp = es_core_news_sm.load()
except ImportError:
    os.system("python -m spacy download es_core_news_sm")
    import es_core_news_sm

    nlp = es_core_news_sm.load()

# Helsinki-NLP for Translation
tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-mul")
translator = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-mul")


# define tools for the agents
@tool
def translate(text: str) -> str:
    """
    Translates English text to Spanish using a Seq2Seq model.

    Args:
        text: The English text string that needs to be translated.
    """
    source = f">>spa<< {text}"
    inputs = tokenizer(source, return_tensors="pt", padding = True, truncation = True, max_length = 512).to("cpu")
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
    words = [token.text for token in abstract if token.is_alpha and not token.is_punct]
    word_n = len(words)
    return word_n


# define model agent
model_agent = LiteLLMModel(model_id="ollama/llama3.2")

# define the agent and the task
editor_agent = ToolCallingAgent(
    tools=[translate, count_words],
    model=model_agent)


# Define the task function
def translate_abstract(abstract, n):
    if not abstract.strip():
        return "Please enter an abstract."
    prompt = f"""
    You are an expert Academic Translator. Your goal is to provide a Spanish translation of an abstract that is EXACTLY    
    {n} words long. Follow these steps:

    1. TRANSLATE: Translate the following English abstract into academic Spanish using the translate tool: '{abstract}'
    2. COUNT: Use the 'count_words' tool on your translation.
    3. ITERATE: If the count is not {n}, edit the Spanish text. 
       - If the count > {n}: Use more concise Spanish academic phrasing.
       - If too count < {n}: Expand descriptions using formal Spanish adjectives.
    4. FINAL VALIDATION: You must use the 'count_words' tool one last time before finishing.

    CONSTRAINTS:
    - The final output must be 100% in Spanish.
    - Do not summarize; maintain the original meaning while hitting the word count.
    - Final sentence must say how many words the final output has

    [Output Format]
    [Reasoning]: (Briefly describe your adjustments in English)
    [Final Spanish Abstract]: (The text)
    [Word Count]: El resumen tiene x palabras.
    """
    return editor_agent.run(prompt)


if __name__ == "__main__":



    print("=== Academic Abstract Translator ===")

    # Input test data
    eng_abstract = input("Enter the English abstract: ")
    try:
        target_count = int(input("Enter the target word count (e.g., 50): "))
    except ValueError:
        print("Invalid number. Defaulting to 200.")
        target_count = 200

    print("\n[The Agent is now thinking and iterating... this may take a minute]\n")

    # Execute and Print
    try:
        final_result = translate_abstract(eng_abstract, target_count)
        print("\n" + "=" * 30)
        print("FINAL AGENT RESPONSE:")
        print(final_result)
        print("=" * 30)
    except Exception as e:
        print(f"An error occurred: {e}")