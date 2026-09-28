import os

from litellm import nlp_cloud_models

from tools import translate, count_words, nlp
from smolagents import ToolCallingAgent, LiteLLMModel
import gradio as gr

# the LLM brain, LiteLLModel imported to support Ollama models ("ollama/...")
model_agent = LiteLLMModel(model_id="ollama/gemma3:4b-it-qat")

# the agent using the brain, ToolCallingAgent calls tools directly without the need to write Python code
editor_agent = ToolCallingAgent(
    tools=[translate, count_words],
    model=model_agent,
)

#Translation task function
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
    result = editor_agent.run(prompt)

    if "[Final Spanish Abstract]" in result:
        spanish = result.split("[Final Spanish Abstract]")[1]
        spanish = spanish.split("[Word Count]")[0].strip()
        final_abstract = len([t for t in nlp(spanish) if t.is_alpha])

        result += f"\n\n Final count: {final_abstract} words"

    return result

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
    demo.launch(server_name="0.0.0.0", server_port=7860) #standard Gradio port