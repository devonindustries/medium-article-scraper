# Use Playwright base image
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set working directory inside container
WORKDIR /app

# Copy application files from backend folder
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose Flask port
EXPOSE 5001

# Start Flask app
CMD ["python", "app.py"]