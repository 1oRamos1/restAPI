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

echo "=== Copying files ==="
cp -r frontend/build/static/* staticfiles/
cp frontend/build/*.ico staticfiles/ 2>/dev/null || echo "No ico files"
cp frontend/build/*.json staticfiles/ 2>/dev/null || echo "No json files"
cp frontend/build/*.png staticfiles/ 2>/dev/null || echo "No png files"

cp frontend/build/index.html templates/

echo "=== Files in staticfiles ==="
ls -la staticfiles/

echo "=== Installing Python deps ==="
pip install -r requirements.txt

echo "=== Running collectstatic ==="
python manage.py collectstatic --no-input --clear -v 2

echo "=== Final static files check ==="
python manage.py findstatic main.b6adf3a0.css || echo "CSS not found"
python manage.py findstatic main.4aec7e67.js || echo "JS not found"

python manage.py migrate