#imports
import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import spacy
from smolagents import tool, CodeAgent, InferenceClientModel
import gradio as gr


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
    inputs = tokenizer(text, return_tensors="pt").to("cpu")
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

# HfApiModel for agent
HF_token = os.getenv("HF_TOKEN")
model_agent = InferenceClientModel(model_id="meta-llama/Llama-3.3-70B-Instruct", token=HF_token)

#define the agent and the task
editor_agent = CodeAgent(
    tools=[translate, count_words],
    model=model_agent,
    additional_authorized_imports=["spacy"]
)



#Define the task function
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

# Gradio dashboard
demo = gr.Interface(
    fn = translate_abstract, # The function to run when the button is clicked
    inputs=[
        gr.Textbox(label="Input English Abstract", lines=5),
        gr.Slider(minimum=50, maximum=500, step=10, label="Target Word Count")
    ],
    outputs=gr.Textbox(label="Final Spanish Translation"),
    title="Abstract Translator"
)

# launch
if __name__ == "__main__":
    demo.launch()