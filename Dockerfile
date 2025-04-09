# Use an official Python runtime
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port your app runs on
EXPOSE 10000

# Start the app with Gunicorn using gevent workers
CMD ["gunicorn", "--worker-class", "gevent", "-w", "1", "-b", "0.0.0.0:10000", "app:app"]
