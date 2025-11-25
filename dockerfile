FROM python:3.10-slim

# Install dependencies for PyAudio & others
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3-dev \
        build-essential \
        portaudio19-dev \
        ffmpeg \
        sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy dependency list first
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy full project structure
COPY app/ ./app/
COPY stt_module/ ./stt_module/
COPY tts_module/ ./tts_module/
COPY logs/ ./logs/
COPY decision_tree.json .
COPY main.py .

# Copy your SQLite database
COPY data/app.sqlite3 ./data/app.sqlite3

# If your app needs a data folder:
RUN mkdir -p ./data

# Expose a port if needed (Flask/FastAPI)
# EXPOSE 8000

CMD ["python", "main.py"]
