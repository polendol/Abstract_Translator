FROM python:3.12-slim AS builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    HF_HOME=/opt/hf

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir \
    https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.7.0/es_core_news_sm-3.7.0-py3-none-any.whl

# Optional: bake the translation model into the image (~300 MB)
# so containers never download it at runtime
RUN python -c "from transformers import pipeline; \
pipeline('translation', model='Helsinki-NLP/opus-mt-en-mul')"


FROM python:3.12-slim

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    HF_HOME=/home/appuser/.cache/huggingface \
    HF_HUB_OFFLINE=1

RUN useradd --create-home --uid 1001 appuser
COPY --from=builder --chown=appuser:appuser /opt/hf /home/appuser/.cache/huggingface

WORKDIR /app
COPY --chown=appuser:appuser AbstractTranslator.py tools.py ./
USER appuser

EXPOSE 7860
CMD ["python", "AbstractTranslator.py"]