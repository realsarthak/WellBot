FROM python:3.12-slim


WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


RUN python -m spacy download en_core_web_sm


COPY . .

EXPOSE 8501


CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
