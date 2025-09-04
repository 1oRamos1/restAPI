#!/usr/bin/env bash
set -o errexit

# Build React with relative paths
cd frontend
export CI=false
export PUBLIC_URL=/static
npm install
npm run build
cd ..

# Setup directories
mkdir -p staticfiles templates

# Copy ALL build files to staticfiles (including index.html initially)
cp -r frontend/build/* staticfiles/

# Move index.html to templates but keep a copy in staticfiles
cp staticfiles/index.html templates/

# Install Python dependencies
pip install -r requirements.txt

# Don't run collectstatic with --clear, just add files
python manage.py collectstatic --no-input

echo "=== Final check ==="
echo "Files in staticfiles:"
ls -la staticfiles/ | head -10
echo "Looking for CSS/JS files:"
find staticfiles -name "*.css" -o -name "*.js" | head -5

python manage.py migrate