FROM python:3.12-slim

# Work inside /app in the container
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

COPY data/chroma/ ./data/chroma/


EXPOSE 8000


# How the container starts the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]