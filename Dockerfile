# Stage 1: Build stage using a lightweight Python slim image
FROM python:3.12-slim as build

# Set the working directory
WORKDIR /app

# Install gcc and other dependencies for building Python packages
RUN apt-get update && apt-get install -y && rm -rf /var/lib/apt/lists/*

# Copy the main requirements file
COPY requirements.txt .

# Install the required Python dependencies for production
RUN pip3 install --no-cache-dir -r requirements.txt

# Stage 2: Tests stage using alpine, with dev dependencies
FROM python:3.12-slim as tests

# Set the working directory
WORKDIR /app

# Copy installed production packages from the build stage
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy requirements-dev.txt for additional test dependencies
COPY requirements-dev.txt .

# Install additional test dependencies
RUN pip3 install --no-cache-dir -r requirements-dev.txt

# Copy the application code and test files
COPY . .

# Run the tests
CMD ["pytest"]

# Stage 3: Runtime stage based on alpine, with only necessary runtime libraries
FROM python:3.12-slim as runtime

# Set the working directory
WORKDIR /app

# Copy installed production packages from the build stage
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy the application code (without dev dependencies)
COPY . .

# Expose the port on which the Flask app will run
EXPOSE 5000

# Command to run the Flask app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "nif_calculator.app:app"]
