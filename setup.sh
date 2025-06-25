#!/bin/bash

echo "Setting up Fake News Detection System..."

# Create virtual environment (optional)
if command -v python3 -m venv &> /dev/null; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install basic dependencies
echo "Installing basic dependencies..."
pip install -r requirements.txt

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"

# Create logs directory
mkdir -p logs

echo "Setup complete! You can now run the application in one of the following modes:"
echo ""
echo "Basic mode (no AI models):"
echo "python run.py --safe-mode"
echo ""
echo "Minimal mode (just the API endpoints):"
echo "python run.py --minimal"
echo ""
echo "Full mode (requires additional AI dependencies):"
echo "python run.py"
echo ""
echo "For help and additional options:"
echo "python run.py --help" 