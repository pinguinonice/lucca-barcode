# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Install system dependencies including poppler-utils and fonts
RUN apt-get update && apt-get install -y \
    poppler-utils \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Set working directory in container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Set working directory to website folder (where run.py is located)
WORKDIR /app/website

# Create directory for uploads if it doesn't exist
RUN mkdir -p app/static/uploads

# Expose the port the app runs on
EXPOSE 5099

# Set environment variables
ENV PYTHONPATH=/app/website
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PATH="/usr/local/bin:${PATH}"

# Run the application
CMD ["python", "run.py"] 