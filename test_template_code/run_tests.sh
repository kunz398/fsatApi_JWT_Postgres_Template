#!/bin/bash

echo "🚀 Starting FastAPI JWT Template Testing Application..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Check if requirements are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import requests" &> /dev/null; then
    echo "📥 Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Run the testing application
echo
echo "🎯 Starting test application..."
python3 test_api.py 