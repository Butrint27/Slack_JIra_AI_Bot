FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

ENV PYTHONPATH=/app

# Default command just runs the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]