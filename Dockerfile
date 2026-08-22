FROM python:3.12-slim

WORKDIR /app

# Copy requirements first
# This helps Docker cache dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .

# Copy HTML templates
COPY templates ./templates

# Application port
EXPOSE 5000

# Start Flask application
CMD ["python", "app.py"]
