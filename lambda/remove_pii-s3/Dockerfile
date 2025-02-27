# Use the official Python image from the Docker Hub
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY src/requirements.txt .

# Install the dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY src/ .

# Run the tests
CMD ["python", "-m", "unittest", "discover", "-s", "test"]