FROM python:3.11-slim

# Install system dependencies including pandoc
RUN apt-get update && \
    apt-get install -y --no-install-recommends pandoc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt /tmp/requirements.txt

# Install Python packages from requirements file
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Create app directory
WORKDIR /app

# Copy your app here
COPY . /app

# Expose Streamlit's default port
EXPOSE 8501

# Default command
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]