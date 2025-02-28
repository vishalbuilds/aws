# Use the official slim Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

LABEL application="remove_pii-s3"

# Copy the requirements file before installing dependencies
COPY src/requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY src/ .

# Default command
CMD ["python"]
