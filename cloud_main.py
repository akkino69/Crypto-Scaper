#!/usr/bin/env python3
"""
Cloud-optimized Crypto Conference Scraper
Runs as a background service with web server for health checks and monitoring
"""

import os
import logging
import sys
import json
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, request
from typing import Dict, Any

# Set up logging for cloud environment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/logs/scraper.log')
    ]
)

from config import Config
from scheduler import ConferenceScheduler
from sheets_processor import GoogleSheetsProcessor

# Initialize Flask app
app = Flask(__name__)

# Global variables
scheduler = None
scraper_thread = None
last_status = {}

def initialize_scraper():
    """Initialize the scraper in cloud environment"""
    global scheduler, last_status
    
    try:
        # Validate configuration
        Config.validate_config()
        
        # Initialize scheduler
        scheduler = ConferenceScheduler()
        
        # Update status
        last_status = {
            'status': 'initialized',
            'timestamp': datetime.now().isoformat(),
            'message': 'Scraper initialized successfully'
        }
        
        logging.info("Cloud scraper initialized successfully")
        return True
        
    except Exception as e:
        last_status = {
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'message': f'Initialization failed: {str(e)}'
        }
        logging.error(f"Failed to initialize scraper: {str(e)}")
        return False

def run_scraper_continuously():
    """Run the scraper continuously in a background thread"""
    global scheduler, last_status
    
    if not scheduler:
        logging.error("Scheduler not initialized")
        return
    
    try:
        logging.info("Starting continuous scraper...")
        
        # Update status
        last_status = {
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'message': 'Scraper running continuously'
        }
        
        # Run the scheduler (this will run indefinitely)
        scheduler.run_scheduler()
        
    except Exception as e:
        last_status = {
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'message': f'Scraper error: {str(e)}'
        }
        logging.error(f"Error in continuous scraper: {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Cloud Run"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'crypto-conference-scraper'
    }), 200

@app.route('/status', methods=['GET'])
def get_status():
    """Get current status of the scraper"""
    global scheduler, last_status
    
    try:
        if scheduler:
            # Get detailed status from scheduler
            scheduler_status = scheduler.get_status()
            
            # Get incomplete conferences count
            incomplete_count = scheduler.get_incomplete_conferences_count()
            
            # Get Google Sheets URL if using Google Sheets
            sheets_url = ""
            if Config.USE_GOOGLE_SHEETS:
                try:
                    if hasattr(scheduler.data_processor, 'get_spreadsheet_url') and scheduler._sheets_initialized:
                        sheets_url = scheduler.data_processor.get_spreadsheet_url()
                    else:
                        sheets_url = "Not initialized yet"
                except Exception as e:
                    logging.warning(f"Failed to get sheets URL: {str(e)}")
                    sheets_url = f"Error: {str(e)}"
            
            return jsonify({
                'scraper_status': last_status,
                'scheduler_status': scheduler_status,
                'incomplete_conferences': incomplete_count,
                'google_sheets_url': sheets_url,
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'scraper_status': last_status,
                'scheduler_status': 'not_initialized',
                'timestamp': datetime.now().isoformat()
            }), 200
            
    except Exception as e:
        logging.error(f"Error getting status: {str(e)}")
        return jsonify({
            'error': f'Status check failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/trigger-scrape', methods=['POST', 'GET'])
def trigger_scrape():
    """Manually trigger a scraping job"""
    global scheduler
    
    try:
        if not scheduler:
            return jsonify({'error': 'Scheduler not initialized'}), 500
        
        # Run a single scraping job
        result = scheduler.run_single_scraping_job()
        
        return jsonify({
            'message': 'Scraping job triggered',
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"Error triggering scrape: {str(e)}")
        return jsonify({
            'error': f'Failed to trigger scrape: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/preview', methods=['GET'])
def preview_next_batch():
    """Preview the next batch of conferences to be scraped"""
    global scheduler
    
    try:
        if not scheduler:
            return jsonify({'error': 'Scheduler not initialized'}), 500
        
        limit = request.args.get('limit', 10, type=int)
        next_batch = scheduler.preview_next_scraping_batch(limit)
        
        return jsonify({
            'next_batch': next_batch,
            'count': len(next_batch),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"Error previewing batch: {str(e)}")
        return jsonify({
            'error': f'Failed to preview batch: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/sheets-url', methods=['GET'])
def get_sheets_url():
    """Get the Google Sheets URL"""
    if not Config.USE_GOOGLE_SHEETS:
        return jsonify({'error': 'Google Sheets not enabled'}), 400
    
    global scheduler
    
    try:
        if not scheduler:
            return jsonify({'error': 'Scheduler not initialized'}), 500
        
        # Initialize sheets if needed
        scheduler._ensure_sheets_initialized()
        url = scheduler.data_processor.get_spreadsheet_url()
        
        return jsonify({
            'google_sheets_url': url,
            'spreadsheet_name': Config.GOOGLE_SPREADSHEET_NAME,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting sheets URL: {str(e)}")
        return jsonify({
            'error': f'Failed to get sheets URL: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/', methods=['GET'])
def home():
    """Home page with service information"""
    return jsonify({
        'service': 'Crypto Conference Scraper',
        'version': '1.0.0',
        'description': 'Automatically scrapes 2026 crypto conference information',
        'endpoints': {
            '/health': 'Health check',
            '/status': 'Get scraper status',
            '/trigger-scrape': 'Trigger manual scrape (POST)',
            '/preview': 'Preview next batch',
            '/sheets-url': 'Get Google Sheets URL'
        },
        'timestamp': datetime.now().isoformat()
    }), 200

def main():
    """Main entry point for cloud deployment"""
    global scraper_thread
    
    logging.info("Starting Crypto Conference Scraper (Cloud Version)")
    
    # Initialize scraper
    if not initialize_scraper():
        logging.error("Failed to initialize scraper, exiting")
        sys.exit(1)
    
    # Start scraper in background thread
    scraper_thread = threading.Thread(target=run_scraper_continuously, daemon=True)
    scraper_thread.start()
    
    # Get port from environment
    port = int(os.environ.get('PORT', 8080))
    
    # Start Flask web server
    logging.info(f"Starting web server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

if __name__ == "__main__":
    main() 