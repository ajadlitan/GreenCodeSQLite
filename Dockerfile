# Use the official Python image from Docker Hub
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Update and install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    maven \
    default-jdk \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# # Install NUnit (for .NET projects)
# RUN apt-get update && apt-get install -y \
#     mono-complete \
#     && rm -rf /var/lib/apt/lists/*

# Install Mono and NUnit
RUN apt-get update && \
apt-get install -y --no-install-recommends \
mono-complete \
nunit-console && \
rm -rf /var/lib/apt/lists/*

# Install Python dependencies and pytest
COPY requirements.txt .
# Install Python dependencies without hash checking
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --no-deps -r requirements.txt pytest

# Copy the application code
COPY . .

# Install Flask for web app
RUN pip install Flask python-dotenv

# Set up tool paths in .env
RUN echo "PYTEST_PATH=$(which pytest)" >> .env
RUN echo "MAVEN_PATH=$(which mvn)" >> .env
RUN echo "JAVAC_PATH=$(which javac)" >> .env
RUN echo "NUNIT_PATH=$(which nunit-console)" >> .env

# Set additional environment variables
ENV EXPECTED_PASSWORD=gcrtrial135#

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Expose port for Flask
EXPOSE 5000

# Set the entrypoint
ENTRYPOINT ["./entrypoint.sh"]
