#!/bin/bash
# Development environment setup script

set -e

echo "Setting up Credit Risk RAG System development environment..."

# Check Python version
echo "Checking Python version..."
python_version=$(python3.12 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3.12 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements-dev.txt

# Setup pre-commit hooks
echo "Setting up pre-commit hooks..."
pre-commit install

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env with your configuration"
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data/raw data/processed models/saved logs

# Create .gitkeep files
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch models/saved/.gitkeep
touch logs/.gitkeep

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Edit .env with your configuration (especially OPENAI_API_KEY)"
echo "3. Start Docker services: docker-compose up -d"
echo "4. Run the application: uvicorn api.main:app --reload"
echo ""
