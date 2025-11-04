#!/bin/bash
# Startup script for Next.js frontend

echo "Starting Runpod Text Models Frontend..."
echo "Make sure you have:"
echo "1. Installed dependencies: cd frontend && npm install"
echo "2. Backend is running on http://localhost:8000"
echo ""
echo "Starting frontend on http://localhost:3000"
echo ""

cd frontend
npm run dev

