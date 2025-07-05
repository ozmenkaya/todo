#!/bin/bash

echo "=== DigitalOcean App Platform Troubleshooting ==="
echo

# 1. Dosya yapısını kontrol et
echo "1. Checking file structure:"
echo "Required files:"
echo "- app.py: $(if [ -f app.py ]; then echo "✓ EXISTS"; else echo "✗ MISSING"; fi)"
echo "- requirements.txt: $(if [ -f requirements.txt ]; then echo "✓ EXISTS"; else echo "✗ MISSING"; fi)"
echo "- runtime.txt: $(if [ -f runtime.txt ]; then echo "✓ EXISTS"; else echo "✗ MISSING"; fi)"
echo "- .do/app.yaml: $(if [ -f .do/app.yaml ]; then echo "✓ EXISTS"; else echo "✗ MISSING"; fi)"
echo "- Procfile: $(if [ -f Procfile ]; then echo "✓ EXISTS"; else echo "✗ MISSING"; fi)"
echo

# 2. requirements.txt içeriğini kontrol et
echo "2. Checking requirements.txt:"
if [ -f requirements.txt ]; then
    echo "Content:"
    cat requirements.txt
    echo
    echo "Flask version: $(grep -i flask requirements.txt | head -1)"
    echo "Gunicorn: $(if grep -q gunicorn requirements.txt; then echo "✓ INCLUDED"; else echo "✗ MISSING"; fi)"
else
    echo "✗ requirements.txt not found"
fi
echo

# 3. runtime.txt kontrol et
echo "3. Checking runtime.txt:"
if [ -f runtime.txt ]; then
    echo "Python version: $(cat runtime.txt)"
else
    echo "✗ runtime.txt not found"
fi
echo

# 4. app.py'da Flask app tanımını kontrol et
echo "4. Checking Flask app definition in app.py:"
if [ -f app.py ]; then
    echo "Flask import: $(if grep -q "from flask import Flask" app.py; then echo "✓ FOUND"; else echo "✗ NOT FOUND"; fi)"
    echo "App creation: $(if grep -q "app = Flask" app.py; then echo "✓ FOUND"; else echo "✗ NOT FOUND"; fi)"
    echo "Main block: $(if grep -q "if __name__ == '__main__'" app.py; then echo "✓ FOUND"; else echo "? NOT FOUND (optional)"; fi)"
else
    echo "✗ app.py not found"
fi
echo

# 5. .do/app.yaml yapılandırmasını kontrol et
echo "5. Checking .do/app.yaml configuration:"
if [ -f .do/app.yaml ]; then
    echo "YAML structure:"
    echo "- Name: $(grep "^name:" .do/app.yaml)"
    echo "- Services: $(if grep -q "^services:" .do/app.yaml; then echo "✓ DEFINED"; else echo "✗ MISSING"; fi)"
    echo "- GitHub repo: $(grep "repo:" .do/app.yaml | head -1)"
    echo "- Environment: $(grep "environment_slug:" .do/app.yaml)"
    echo "- Build command: $(grep "build_command:" .do/app.yaml)"
    echo "- Run command: $(grep "run_command:" .do/app.yaml)"
    echo "- HTTP port: $(grep "http_port:" .do/app.yaml)"
else
    echo "✗ .do/app.yaml not found"
fi
echo

# 6. Git durumunu kontrol et
echo "6. Checking Git status:"
if [ -d .git ]; then
    echo "Git repository: ✓ INITIALIZED"
    echo "Current branch: $(git branch --show-current 2>/dev/null || echo "Unable to determine")"
    echo "Remote origin: $(git remote get-url origin 2>/dev/null || echo "No remote set")"
    echo "Uncommitted changes: $(if [ -n "$(git status --porcelain)" ]; then echo "⚠ YES"; else echo "✓ NONE"; fi)"
else
    echo "Git repository: ✗ NOT INITIALIZED"
fi
echo

# 7. DigitalOcean'a deployment için öneri
echo "7. Deployment recommendations:"
echo "Before deploying to DigitalOcean:"
echo "- Ensure all files are committed to Git"
echo "- Push changes to GitHub"
echo "- Update .do/app.yaml with correct GitHub repo name"
echo "- Verify environment variables in app.yaml"
echo
echo "To test locally first:"
echo "pip install -r requirements.txt"
echo "export PORT=8080"
echo "gunicorn app:app --bind 0.0.0.0:8080"
echo
echo "Then visit: http://localhost:8080"
echo

# 8. DigitalOcean specific checks
echo "8. DigitalOcean App Platform specific checks:"
echo "- Source directory: $(grep "source_dir:" .do/app.yaml || echo "Not specified (will use root)")"
echo "- Python runtime: $(if [ -f runtime.txt ]; then echo "✓ Specified in runtime.txt"; else echo "⚠ Using default"; fi)"
echo "- Database: $(if grep -q "databases:" .do/app.yaml; then echo "✓ PostgreSQL configured"; else echo "Using SQLite (file-based)"; fi)"
echo

echo "=== Troubleshooting Complete ==="
echo
echo "If you're still getting 'no component detected' error:"
echo "1. Make sure your GitHub repo is public or DigitalOcean has access"
echo "2. Verify the repo name in .do/app.yaml matches your GitHub repo"
echo "3. Try using the minimal app.yaml configuration"
echo "4. Check DigitalOcean build logs for specific error messages"
