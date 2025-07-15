# Deploy Crypto Conference Scraper to Render

## Quick Setup

1. **Push to GitHub**
   ```bash
   # If you haven't already, initialize git repo
   git init
   git add .
   git commit -m "Initial commit: Crypto Conference Scraper"
   
   # Push to GitHub (create a new repository on GitHub first)
   git remote add origin https://github.com/yourusername/crypto-conference-scraper.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy to Render**
   - Go to https://render.com and sign up/login
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Select the repository containing this code
   - Render will automatically detect the `render.yaml` file and deploy

3. **Environment Variables** (Already configured in render.yaml)
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `USE_GOOGLE_SHEETS`: true
   - `GOOGLE_SPREADSHEET_NAME`: Crypto Conferences 2026
   - `SCRAPING_INTERVAL_HOURS`: 12

## What Happens After Deployment

1. **Automatic Startup**: The scraper will start automatically
2. **Health Monitoring**: Render will monitor the service health
3. **Scheduled Scraping**: Runs every 12 hours automatically
4. **Google Sheets Updates**: Uses your personal credentials to update the sheet
5. **Web Interface**: Available at your Render URL for monitoring

## Monitoring

- **Service URL**: Will be provided by Render after deployment
- **Health Check**: Available at `https://your-app.onrender.com/health`
- **Status**: Available at `https://your-app.onrender.com/status`
- **Logs**: Available in Render dashboard

## Google Sheets Access

The deployed service will automatically update your Google Sheets:
**Sheet URL**: https://docs.google.com/spreadsheets/d/1Udeh1Ju_9gLjIXQgEnyW-V9yV53dQHPrzAdNhqjtYYA

## Manual Triggers

You can manually trigger scraping by visiting:
`https://your-app.onrender.com/trigger-scrape`

## Troubleshooting

1. **Authentication Issues**: Check that personal_credentials.json is included
2. **API Limits**: Monitor OpenAI API usage in your dashboard
3. **Logs**: Check Render service logs for detailed error information

## Cost

- **Render**: Free tier available (service sleeps after 15 minutes of inactivity)
- **OpenAI API**: ~$1-2 per scraping session (decreases as data gets filled)
- **Google Sheets**: Free 