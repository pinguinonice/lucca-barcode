#!/bin/bash

# Exit on any error
set -e

# Exit on pipe failure (e.g., cmd1 | cmd2)
set -o pipefail

# Treat unset variables as errors
set -u

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to display error messages
error() {
    echo "ERROR: $1" >&2
    exit 1
}

# Function to display info messages
info() {
    echo "INFO: $1"
}

# Check if Docker is installed
if ! command_exists docker; then
    error "Docker is not installed. Please install Docker first."
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    error "Docker daemon is not running. Please start Docker first."
fi

# Check if docker-compose is installed
if ! command_exists docker-compose; then
    error "docker-compose is not installed. Please install docker-compose first."
fi

# Check if required files exist
for file in "Dockerfile" "docker-compose.yml" "requirements.txt"; do
    if [ ! -f "$file" ]; then
        error "Required file '$file' not found in current directory."
    fi
done

# Check if website directory exists
if [ ! -d "website" ]; then
    error "Required 'website' directory not found."
fi

# Create necessary directories if they don't exist
mkdir -p website/app/static/uploads
mkdir -p website/flask_session

# Set permissions for uploads and session directories
chmod 755 website/app/static/uploads
chmod 755 website/flask_session

# Function to cleanup on exit
cleanup() {
    info "Cleaning up..."
    docker-compose down --remove-orphans
}

# Register cleanup function
trap cleanup EXIT

# Build and run the application
info "Building and starting the application..."
docker-compose up --build --remove-orphans

# Note: The cleanup function will be called automatically on script exit 