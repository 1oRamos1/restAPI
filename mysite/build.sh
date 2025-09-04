#!/usr/bin/env bash
set -o errexit  # Exit on error

# Build React
cd frontend
npm install
npm run build
cd ..

# Setup Django directories
mkdir -p staticfiles mysite/templates

# Copy React build files
cp -r frontend/build/static/* staticfiles/ 2>/dev/null || :
cp frontend/build/index.html mysite/templates/

# Install Python dependencies and setup Django
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate