FROM python:3.10-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    build-essential \
    make \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the script
COPY vscode-json.py .

# Optional: make executable (still good practice)
RUN chmod +x vscode-json.py

# Use python3 explicitly as entrypoint
ENTRYPOINT ["python3", "./vscode-json.py"]

