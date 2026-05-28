#!/usr/bin/env bash
set -o errexit

# ----------------------------------------
# 1. Install Python dependencies
# ----------------------------------------
pip install -r ../requirements.txt

# ----------------------------------------
# 2. Build React
# ----------------------------------------
cd frontend
export CI=false
npm install
npm run build
cd ..

# ----------------------------------------
# 3. Setup directories
# ----------------------------------------
mkdir -p staticfiles/static templates

# Copy index.html to templates for Django TemplateView
cp frontend/build/index.html templates/

# Copy React static files to staticfiles/static/
cp -r frontend/build/static/* staticfiles/static/

# Copy other public assets to staticfiles root
cp frontend/build/favicon.ico staticfiles/ 2>/dev/null || true
cp frontend/build/*.png staticfiles/ 2>/dev/null || true
cp frontend/build/*.gif staticfiles/ 2>/dev/null || true
cp frontend/build/manifest.json staticfiles/ 2>/dev/null || true
cp frontend/build/robots.txt staticfiles/ 2>/dev/null || true

# ----------------------------------------
# 4. Collect static files (Django admin, rest_framework etc.)
# ----------------------------------------
python manage.py collectstatic --no-input

echo "=== Static files check ==="
find staticfiles/static -name "*.css" -o -name "*.js" | head -5

# ----------------------------------------
# 5. Migrations
# ----------------------------------------
python manage.py makemigrations
python manage.py migrate

# ----------------------------------------
# 6. Setup initial data
# ----------------------------------------
python manage.py create_superuser
python manage.py create_sample_tracks

echo "=== Build complete ==="
