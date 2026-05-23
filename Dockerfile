FROM python:3.11-slim

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Set environment variables for production
ENV ENV=production
ENV PORT=8080

EXPOSE 8080

# Run the FastAPI server
CMD ["python", "app.py"]
