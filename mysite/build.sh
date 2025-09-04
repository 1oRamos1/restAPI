#!/usr/bin/env bash
set -o errexit

# Build React
cd frontend
export CI=false
npm install
npm run build
cd ..

# Setup directories (they're already in the right place)
mkdir -p staticfiles templates

# Copy React build files
cp -r frontend/build/static/* staticfiles/
cp frontend/build/*.ico staticfiles/ 2>/dev/null || :
cp frontend/build/*.json staticfiles/ 2>/dev/null || :
cp frontend/build/*.png staticfiles/ 2>/dev/null || :

# Copy index.html to templates
cp frontend/build/index.html templates/

# Install Python dependencies and setup Django
pip install -r requirements.txt
python manage.py collectstatic --no-input --clear
python manage.py migrate