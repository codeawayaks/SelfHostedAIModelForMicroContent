#!/bin/bash
# Startup script for FastAPI backend

echo "Starting Runpod Text Models Backend..."
echo "Make sure you have:"
echo "1. Created a .env file with your Runpod.io credentials"
echo "2. Installed dependencies: pip install -r requirements.txt"
echo ""
echo "Starting server on http://0.0.0.0:8000"
echo "API docs available at http://localhost:8000/docs"
echo ""

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

