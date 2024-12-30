# Use the official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install prerequisites
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unixodbc-dev

# Add the Microsoft repository for ODBC Driver 18
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . .

# Expose the port
EXPOSE 8000

# Start the application
CMD ["python", "main.py"]
