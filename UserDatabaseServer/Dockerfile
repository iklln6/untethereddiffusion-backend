# Use official Python base image
#FROM python:3.10-slim
FROM python:3.11.12-slim
#FROM ubuntu/python:3.10-22.04_stable


# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y postgresql postgresql-contrib libpq-dev python3-dev
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Install Python, git and other necessary tools
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    libgl1 \
    && ln -sf /usr/bin/python3.10 /usr/bin/python \
    && ln -sf /usr/bin/pip3 /usr/bin/pip




# Copy the app source code
COPY ./app ./app


# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port FastAPI runs on
EXPOSE 8000

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]



