## Abstract Translator

## Description

This program was devised to cover the need for translating academic abstract conserving the number of words of the 
original abstract. It translates abstracts from English to Spanish conserving the number of words established by the 
user (up to 500 words)

It uses `smolagents` library with `gemma3:4b-it-qat` as brain. Given the limitations of the model run locally, 
ToolCallingAgent is applied instead of CodeAgent. The agent uses two tools, one for translating and another for word count. 
Translation uses `Helsinki-NLP/opus-mt-en-mul` for Spanish translation and `es_core_news_sm` for Spanish NLP model. 

The program uses gradio interface.

## Docker

## Requirements
1. Docker & Docker Compose: Installed and running (Docker Desktop for Windows/macOS or Docker Engine on Linux). Compose is included by default with Docker Desktop, or available via docker-compose-plugin.
2. NVIDIA GPU (recommended): An NVIDIA graphics card with up-to-date drivers, used by Ollama to run gemma3:4b-it-qat and by PyTorch for the translation model. Without a GPU the project still runs on CPU, but responses will be much slower.
3. NVIDIA Container Toolkit: Required on Linux/WSL2 so Docker can pass GPU access to the containers. Docker Desktop on Windows handles this automatically with the WSL2 backend and current drivers.
4. Hardware: Minimum 8 GB RAM (16 GB recommended), 4 GB+ VRAM on your NVIDIA GPU, and at least 15 GB free disk space for the Python/PyTorch image, the Ollama image, the Helsinki-NLP/opus-mt-en-mul translation model (~300 MB), and the gemma3:4b-it-qat model (~4 GB).
5. Internet access: Needed on the first run to build the image, pull ollama/ollama, and download the gemma3:4b-it-qat model. After that, everything runs offline.
6. Network / Ports: Port 7860 must be free on your machine, since the Gradio interface is exposed there (http://localhost:7860).
7. Storage / Permissions: Ollama models are stored in a Docker named volume (ollama:/root/.ollama), so they persist between restarts. Deleting volumes (docker compose down -v) removes the downloaded model and requires pulling it again.

## How it works 
1. Multi-Stage Build:
Builder (python:3.12-slim): Creates the Python virtual environment and installs all dependencies (gradio, transformers, smolagents, spacy, litellm, torch) plus the Spanish spaCy model. It also pre-downloads the Helsinki-NLP/opus-mt-en-mul translation model.
Runtime (python:3.12-slim): Copies only the finished virtual environment and the cached translation model, leaving behind pip caches and build tooling to keep the final image as lean as possible.
2. Two Services: Docker Compose runs the app (built from the Dockerfile) and Ollama (pulled from ollama/ollama). The app reaches Ollama over the internal Docker network at http://ollama:11434, so no ports need to be opened for it.
3. Security: The app runs as a non-root user (appuser with UID 1001).
4. Hugging Face Cache: The translation model is baked into the image at /home/appuser/.cache/huggingface (HF_HOME) during the build, with HF_HUB_OFFLINE=1 so the container never downloads anything at runtime.
5. Ollama Model Storage: The gemma3:4b-it-qat model is stored in a named Docker volume (ollama). It is downloaded only once and reused on subsequent runs, until you delete the volume with docker compose down -v.
6. Gradio Web Interface: Listens on port 7860 bound to 0.0.0.0, exposed to your machine at http://localhost:7860.
7. Step-by-step: build and start both services (`docker compose up -d --build`), download the language model once (`docker compose exec ollama ollama pull gemma3:4b-it-qat`), then open `http://localhost:7860`. To stop everything, run `docker compose down`.
8. See How it works section in Local section below for specifics on how the program and output details

## Local

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

## File structure
- `AbstractTranslator.py` - main program, run this to launch the app
- `tools.py` - file containing agent tools
- `requirements.txt` — Python dependencies
- `README.md` — this file

## License & Attributions

### Repository License
This project is licensed under the [MIT License](LICENSE) — see the LICENSE file for details.

### Model & Software Attributions
* **Agent Framework:** Built using [`smolagents`](https://github.com/huggingface/smolagents) (Apache 2.0 License).
* **Reasoning Model:** Powered by [Google Gemma 3](https://ai.google.dev/gemma) (`gemma3:4b-it-qat`). Usage of Gemma model weights is subject to the [Google Gemma Terms of Use](https://ai.google.dev/gemma/terms) and [Prohibited Use Policy](https://ai.google.dev/gemma/prohibited_use_policy).
* **Translation Model:** [`Helsinki-NLP/opus-mt-en-mul`](https://huggingface.co/Helsinki-NLP/opus-mt-en-mul) hosted on Hugging Face ([CC-BY-4.0 License](https://creativecommons.org/licenses/by/4.0/)).
* **NLP & Tokenization:** Uses [spaCy](https://spacy.io/) and its `es_core_news_sm` pipeline ([MIT License](https://github.com/explosion/spaCy/blob/master/LICENSE)).
* **Inference Engine & Interface:** Powered by [Ollama](https://ollama.com) (MIT License) and [Gradio](https://github.com/gradio-app/gradio) (Apache 2.0 License).

