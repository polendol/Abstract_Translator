#imports
import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import spacy
from smolagents import tool, CodeAgent, LiteLLMModel
import gradio as gr

# SpaCy model for Spanish NLP nad Helsinki-NLP for Translation
nlp = spacy.load("es_core_news_sm")
tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-mul")
translator = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-mul")

# define tools for the agents
@tool
def translate(text: str) -> str:
    """
    Translate English text to Spanish
    """
    translated_abstract= translator(text)[0]['translation_text']
    return translated_abstract

@tool
def count_words(text: str) -> int:
    """
    Counts words in translation
    """
    abstract = nlp(text)
    word_n = len([token for token in abstract if token.isalpha])
    return word_n

# LiteLLModel for agent
hf_token = os.getenv("HF_TOKEN")
model_agent = LiteLLMModel(model_id="gpt-4", token=hf_token)

#define the agent and the task
editor_agent = CodeAgent(
    tools=[translate, count_words],
    model=model_agent,
    additional_authorized_imports=["spacy"]
)

task = """
Translate the following abstract to Spanish. 
Target word count: 200 words. 
If the translation is too long or short, rewrite it to fit the limit.
Abstract: 
"""

#Define the task function
def translate_abstract(abstract, n):
    prompt = f"""
    Translate this academic paper abstract into Spanish: '{abstract}'. 
    The Spanish version MUST be exactly {n} words. 
    Use your tools to check the count and edit until perfect.
    """
    return editor_agent.run(prompt)

# Gradio dashboard
demo = gr.Interface(
    fn=run_translation_task, # The function to run when the button is clicked
    inputs=[
        gr.Textbox(label="Input English Abstract", lines=5),
        gr.Slider(minimum=50, maximum=500, step=10, label="Target Word Count")
    ],
    outputs=gr.Textbox(label="Final Spanish Translation"),
    title="Agentic Abstract Editor"
)

# launch
if __name__ == "__main__":
    demo.launch()