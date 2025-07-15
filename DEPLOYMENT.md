# 🚀 Google Cloud Deployment Guide

This guide will help you deploy the Crypto Conference Scraper to Google Cloud Platform, where it will run continuously and update a Google Sheets document automatically.

## 📋 Prerequisites

1. **Google Cloud Account** - [Create one here](https://cloud.google.com/)
2. **Google Cloud Project** - Create a new project or use an existing one
3. **gcloud CLI** - [Install the Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
4. **OpenAI API Key** - Get from [OpenAI Platform](https://platform.openai.com/account/api-keys)

## 🏗️ Architecture Overview

The cloud deployment includes:
- **Cloud Run** - Containerized service running the scraper
- **Google Sheets** - Live dashboard and data storage
- **Secret Manager** - Secure storage of API keys
- **Cloud Build** - Automated deployment pipeline
- **Service Account** - Secure access to Google APIs

## 🚀 Quick Deployment

### 1. Prepare Your Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd crypto-conference-scraper

# Set your OpenAI API key
export OPENAI_API_KEY="your-openai-api-key-here"

# Set your Google Cloud project (optional - script will detect current project)
export PROJECT_ID="your-project-id"
```

### 2. Run the Deployment Script

```bash
# Make the script executable
chmod +x deploy.sh

# Run the deployment
./deploy.sh
```

The script will:
- ✅ Enable required Google Cloud APIs
- ✅ Create service accounts and permissions
- ✅ Store your OpenAI API key securely
- ✅ Build and deploy the Docker container
- ✅ Deploy to Cloud Run
- ✅ Set up automatic Google Sheets integration

### 3. Access Your Service

After deployment, you'll receive URLs for:
- **Service URL**: Main application endpoint
- **Status Dashboard**: Real-time scraper status
- **Health Check**: Service health monitoring
- **Google Sheets**: Live data dashboard

## 📊 Google Sheets Integration

### Automatic Setup

The scraper automatically creates a Google Sheets document with:
- **Dashboard Tab**: Progress overview and metrics
- **Conferences 2026**: Main data with real-time updates
- **Conferences 2025**: Reference data from original CSV

### Dashboard Features

The dashboard includes:
- 📈 **Progress Metrics**: Completion rates and field status
- 🔄 **Last Updated**: Real-time timestamps
- 📊 **Field Completion**: Detailed breakdown by field type
- 🔗 **Quick Links**: Easy navigation between sheets
- 🎯 **Key Metrics**: Missing data counts
- 🔧 **System Status**: Health monitoring

### Manual Initialization

If you have existing CSV data:

```bash
# Upload your CSV data to Google Sheets
curl -X POST "https://your-service-url/trigger-scrape"
```

## 🔧 Configuration Options

### Environment Variables

The deployment automatically sets these environment variables:

```bash
USE_GOOGLE_SHEETS=true
GOOGLE_SPREADSHEET_NAME="Crypto Conferences 2026"
OPENAI_API_KEY="(from Secret Manager)"
GOOGLE_SERVICE_ACCOUNT_FILE="/app/service-account.json"
```

### Custom Configuration

To modify the configuration:

1. Edit `cloudbuild.yaml` for deployment settings
2. Update environment variables in the deployment script
3. Modify `config.py` for application settings

## 📡 API Endpoints

Your deployed service provides these endpoints:

### Status and Monitoring
- `GET /` - Service information
- `GET /health` - Health check
- `GET /status` - Detailed scraper status
- `GET /sheets-url` - Get Google Sheets URL

### Manual Controls
- `POST /trigger-scrape` - Manually trigger scraping
- `GET /preview?limit=10` - Preview next conferences to scrape

### Example Usage

```bash
# Check service status
curl https://your-service-url/status

# Trigger a manual scrape
curl -X POST https://your-service-url/trigger-scrape

# Get Google Sheets URL
curl https://your-service-url/sheets-url
```

## 🔄 Automatic Scheduling

The scraper runs automatically every 12 hours:
- Searches for missing conference information
- Updates Google Sheets in real-time
- Maintains detailed logs
- Updates dashboard metrics

## 🔍 Monitoring and Logs

### Cloud Logging

View logs in Google Cloud Console:
```bash
# View recent logs
gcloud logs read crypto-conference-scraper --project=your-project-id --limit=50

# Follow logs in real-time
gcloud logs tail crypto-conference-scraper --project=your-project-id
```

### Status Monitoring

Check service health:
```bash
# Service health
curl https://your-service-url/health

# Detailed status
curl https://your-service-url/status
```

## 🔐 Security and Permissions

### Service Account

The deployment creates a service account with minimal required permissions:
- Google Sheets API access
- Secret Manager access
- Cloud Logging write access

### API Key Security

Your OpenAI API key is:
- Stored securely in Google Secret Manager
- Never exposed in logs or code
- Accessible only to the service account

## 🛠️ Manual Deployment Steps

If you prefer manual deployment:

### 1. Enable APIs

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    secretmanager.googleapis.com \
    sheets.googleapis.com
```

### 2. Create Secrets

```bash
# Store OpenAI API key
echo -n "your-openai-key" | gcloud secrets create OPENAI_API_KEY --data-file=-
```

### 3. Build and Deploy

```bash
# Build with Cloud Build
gcloud builds submit --config=cloudbuild.yaml

# Or build and deploy manually
docker build -t gcr.io/your-project-id/crypto-scraper .
docker push gcr.io/your-project-id/crypto-scraper

gcloud run deploy crypto-conference-scraper \
    --image=gcr.io/your-project-id/crypto-scraper \
    --region=us-central1 \
    --platform=managed \
    --set-env-vars=USE_GOOGLE_SHEETS=true
```

## 🔧 Troubleshooting

### Common Issues

1. **Permission Errors**
   - Ensure all required APIs are enabled
   - Check service account permissions
   - Verify project ID is correct

2. **Google Sheets Access**
   - Verify service account has Sheets API access
   - Check if spreadsheet exists and is accessible

3. **OpenAI API Issues**
   - Verify API key is valid and has credits
   - Check Secret Manager access

### Debug Commands

```bash
# Check service logs
gcloud logs read crypto-conference-scraper --project=your-project-id

# Test API endpoints
curl https://your-service-url/health
curl https://your-service-url/status

# Check deployment status
gcloud run services describe crypto-conference-scraper --region=us-central1
```

## 💰 Cost Estimation

### Google Cloud Costs
- **Cloud Run**: ~$5-15/month (depends on usage)
- **Secret Manager**: ~$0.10/month
- **Cloud Build**: ~$0.10/build
- **Google Sheets API**: Free (up to 100 requests/100 seconds)

### OpenAI API Costs
- ~$1-2 per 100 conferences scraped
- Monthly cost decreases as data is filled in
- Estimated $50-100/month initially, reducing over time

## 📞 Support

If you encounter issues:
1. Check the logs using `gcloud logs read`
2. Verify your configuration in Google Cloud Console
3. Test API endpoints manually
4. Check Google Sheets permissions

## 🎯 Next Steps

After successful deployment:
1. 📊 **Monitor Progress**: Check the Google Sheets dashboard
2. 🔍 **Review Data**: Validate scraped conference information
3. 📈 **Track Metrics**: Monitor completion rates
4. 🔄 **Automatic Updates**: Let the system run continuously

Your crypto conference scraper is now running in the cloud! 🎉

---

**Note**: The scraper will automatically start working after deployment and will update the Google Sheets every 12 hours with new conference information. 