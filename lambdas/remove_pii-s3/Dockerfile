# Use the official slim Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

LABEL application="remove_pii-s3"

# Copy the requirements file before installing dependencies
COPY src/requirements.txt .

# Upgrade pip and install dependencies (including pytest & pytest-cov)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire source code into the container
COPY src/ .
COPY test.sh .
ENV PYTHONPATH=/app/src
RUN chmod +x test.sh

# Set the entrypoint to run the test script
RUN ["./test.sh"]
ENTRYPOINT['sh']