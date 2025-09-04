#!/usr/bin/env bash
set -o errexit  # Exit on error

# Build React
cd frontend
export CI=false
export PUBLIC_URL=
npm install
npm run build
cd ..

# Setup Django directories
mkdir -p staticfiles mysite/templates

# Copy React build files (CSS, JS, etc.)
cp -r frontend/build/static/* staticfiles/ 2>/dev/null || :

# Copy other important files (favicon, manifest, etc.)
cp frontend/build/*.ico staticfiles/ 2>/dev/null || :
cp frontend/build/*.json staticfiles/ 2>/dev/null || :
cp frontend/build/*.png staticfiles/ 2>/dev/null || :
cp frontend/build/*.txt staticfiles/ 2>/dev/null || :

# Copy index.html to templates
cp frontend/build/index.html mysite/templates/

# DEBUG: Show what files were actually copied
echo "=== DEBUG: Files in staticfiles folder ==="
ls -la staticfiles/
echo "=== DEBUG: Files in templates folder ==="
ls -la mysite/templates/
echo "=== DEBUG: Contents of React build folder ==="
ls -la frontend/build/

# Install Python dependencies and setup Django
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# DEBUG: Show final static files
echo "=== DEBUG: Final static files after collectstatic ==="
python manage.py findstatic main.4aec7e67.js || echo "JS file not found"
python manage.py findstatic main.b6adf3a0.css || echo "CSS file not found"