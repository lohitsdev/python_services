#!/bin/bash

echo "🐍 Starting PDF Extractor Service..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Start the service
echo "🚀 Starting PDF Extractor Service on port 5001..."
echo
echo "Service will be available at: http://localhost:5001"
echo "Press Ctrl+C to stop the service"
echo

python pdf_extractor.py
