#!/bin/bash

echo "==================================="
echo "Forenstiq Evidence Analyzer"
echo "==================================="
echo

# Activate virtual environment
source venv/bin/activate

# Check if demo data exists
if [ ! -f "data/forenstiq_cases.db" ]; then
    echo "No database found. Generating demo data..."
    python scripts/generate_demo_data.py
    echo
fi

# Run application
echo "Starting application..."
python src/main.py