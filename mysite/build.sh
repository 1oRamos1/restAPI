#!/usr/bin/env bash
set -o errexit

# ----------------------------------------
# 1. Build React with relative paths
# ----------------------------------------
cd frontend
export CI=false
export PUBLIC_URL=/static  # ensures static paths are relative
npm install
npm run build
cd ..

# ----------------------------------------
# 2. Setup directories for Django
# ----------------------------------------
mkdir -p staticfiles templates

# Copy all React build files to staticfiles
cp -r frontend/build/* staticfiles/

# Move index.html to templates for TemplateView (React catch-all)
cp staticfiles/index.html templates/

# ----------------------------------------
# 3. Install Python dependencies
# ----------------------------------------
pip install -r requirements.txt

# ----------------------------------------
# 4. Collect static files for Django
# ----------------------------------------
# Copies JS/CSS/images from apps/static and frontend build into STATIC_ROOT
python manage.py collectstatic --no-input

# Optional: check some files exist
echo "=== Final check: staticfiles ==="
ls -la staticfiles/ | head -10
echo "Looking for CSS/JS files:"
find staticfiles -name "*.css" -o -name "*.js" | head -5

# ----------------------------------------
# 5. Django migrations for database
# ----------------------------------------
# Create new migrations if models changed
python manage.py makemigrations

# Apply all migrations to Internal Postgres (creates tables)
python manage.py migrate
python mange.py flush

# 6. Create superuser
python manage.py create_render_superuser

# 7. Populate database with categories + tracks
python manage.py create_sample_tracks
# Optional: load fixtures if you have existing data
# python manage.py loaddata data.json

echo "=== Build complete ==="
