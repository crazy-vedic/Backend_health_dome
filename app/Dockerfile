# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app to the working directory
COPY ./app /app

# Copy the initiate.py script to the working directory
COPY initiate.py /app/initiate.py

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run initiate.py script to setup database
CMD ["bash", "-c", "python /app/initiate.py && python /app/app.py"]
