#!/bin/bash

# Crypto Conference Scraper - Render Deployment Script

echo "🚀 Deploying Crypto Conference Scraper to Render..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: Crypto Conference Scraper for Render deployment"
else
    echo "📝 Adding changes to Git..."
    git add .
    git commit -m "Update: Crypto Conference Scraper deployment $(date)"
fi

# Check if we have a remote
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❓ Please enter your GitHub repository URL (e.g., https://github.com/username/repo.git):"
    read -r repo_url
    git remote add origin "$repo_url"
fi

echo "📤 Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ Code pushed to GitHub successfully!"
echo ""
echo "🌐 Next steps:"
echo "1. Go to https://render.com and sign up/login"
echo "2. Click 'New' → 'Blueprint'"
echo "3. Connect your GitHub repository"
echo "4. Select this repository"
echo "5. Render will automatically detect render.yaml and deploy"
echo ""
echo "📊 Your Google Sheets will be updated at:"
echo "https://docs.google.com/spreadsheets/d/1Udeh1Ju_9gLjIXQgEnyW-V9yV53dQHPrzAdNhqjtYYA"
echo ""
echo "⏰ The scraper will run automatically every 12 hours!"
echo ""
echo "🔧 After deployment, you can monitor at:"
echo "https://your-app.onrender.com/health"
echo "https://your-app.onrender.com/status"
echo "https://your-app.onrender.com/trigger-scrape" 