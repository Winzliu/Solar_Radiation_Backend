
# Use Python 3.13-slim as the base image
FROM python:3.13-slim

# Set timezone
ENV TZ=Asia/Jakarta
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install system dependencies if required (e.g., for building wheels)
# Since we use --only-binary :all: in run_api.bat for fallback, we might not need build tools, 
# but installing gcc/python3-dev is safer for some libraries like numpy/pandas if wheels are missing.
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc \
  python3-dev \
  && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app /app/app
COPY model /app/model
COPY data /app/data

# Expose port 8000
EXPOSE 8000

# Set environment variables
ENV ALLOWED_ORIGINS="http://localhost:3000,http://localhost:3001"

# Change working directory to /app/app to ensure relative paths (e.g. ../model) work
WORKDIR /app/app

# Run the application
# Using uvicorn directly to ensure it binds to 0.0.0.0
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
