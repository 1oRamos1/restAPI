#!/usr/bin/env bash
set -o errexit

echo "=== Building React ==="
cd frontend
export CI=false
npm install
npm run build
cd ..

echo "=== Setting up directories ==="
mkdir -p staticfiles templates

echo "=== Copying static files ==="
cp -r frontend/build/static/* staticfiles/
cp frontend/build/*.ico staticfiles/ 2>/dev/null || :
cp frontend/build/*.json staticfiles/ 2>/dev/null || :
cp frontend/build/*.png staticfiles/ 2>/dev/null || :

echo "=== Processing index.html for Django templates ==="
# Copy index.html and modify it to work with Django
cp frontend/build/index.html templates/

# Replace static file references with Django template tags
sed -i 's|/static/css/\([^"]*\)|{% static "css/\1" %}|g' templates/index.html
sed -i 's|/static/js/\([^"]*\)|{% static "js/\1" %}|g' templates/index.html
sed -i 's|/favicon.ico|{% static "favicon.ico" %}|g' templates/index.html
sed -i 's|/logo192.png|{% static "logo192.png" %}|g' templates/index.html
sed -i 's|/manifest.json|{% static "manifest.json" %}|g' templates/index.html

# Add Django load static tag at the top
sed -i '1i{% load static %}' templates/index.html

echo "=== Processed index.html content ==="
head -10 templates/index.html

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Running collectstatic ==="
python manage.py collectstatic --no-input --clear

echo "=== Checking what files actually exist ==="
echo "CSS files found:"
find staticfiles -name "*.css" | head -5
echo "JS files found:"
find staticfiles -name "*.js" | head -5

python manage.py migrate