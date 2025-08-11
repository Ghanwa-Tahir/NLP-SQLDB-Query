# Use a minimal Python image based on Alpine
FROM python:3.10-alpine

# Set environment variables to reduce size and suppress warnings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory     
WORKDIR /app

# Install system dependencies needed for Streamlit and scientific packages
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    py3-pip \
    build-base \
    unixodbc-dev\
    && pip install --upgrade pip

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the default Streamlit port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app.py"]