FROM python:3.11-slim-buster

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy   
COPY . .

# Expose the port
EXPOSE 8080

# Command to run the application
CMD ["python", "app.py"]
