FROM python:3.11-slim

# Install system dependencies including pandoc
RUN apt-get update && \
    apt-get install -y --no-install-recommends pandoc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir streamlit pandas

# Create app directory
WORKDIR /app

# (Optional) Copy your app here
COPY . /app

# Expose Streamlit's default port
EXPOSE 8501

# Default command (customize as needed)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]