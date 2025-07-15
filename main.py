#!/usr/bin/env python3
"""
Crypto Conference Scraper
A program that automatically scrapes web information for 2026 crypto conferences
"""

import argparse
import logging
import sys
import json
import os
from datetime import datetime
from typing import Dict, Any

from config import Config
from csv_processor import CSVProcessor
from sheets_processor import GoogleSheetsProcessor
from web_scraper import ConferenceScraper
from scheduler import ConferenceScheduler

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )

def initialize_system():
    """Initialize the system and data storage (CSV or Google Sheets)"""
    logger = logging.getLogger(__name__)
    
    try:
        # Validate configuration
        Config.validate_config()
        logger.info("Configuration validation successful")
        
        if Config.USE_GOOGLE_SHEETS:
            # Initialize Google Sheets
            sheets_processor = GoogleSheetsProcessor()
            sheets_processor.create_or_open_spreadsheet(Config.GOOGLE_SPREADSHEET_NAME)
            
            # Initialize from existing CSV files if they exist
            if os.path.exists(Config.INPUT_CSV):
                csv_processor = CSVProcessor()
                df_2025, df_2026 = csv_processor.load_and_split_data()
                
                # If no existing 2026 data in CSV, create template
                if df_2026.empty:
                    df_2026 = csv_processor.create_2026_template(df_2025)
                
                sheets_processor.upload_initial_data(df_2025, df_2026)
                logger.info("Google Sheets initialized from CSV data")
            else:
                logger.info("Google Sheets initialized without CSV data")
                
            # Print spreadsheet URL
            spreadsheet_url = sheets_processor.get_spreadsheet_url()
            print(f"📊 Google Sheets URL: {spreadsheet_url}")
            
        else:
            # Initialize CSV processor and create files
            csv_processor = CSVProcessor()
            csv_processor.initialize_csv_files()
            logger.info("CSV files initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"System initialization failed: {str(e)}")
        return False

def run_scheduler():
    """Run the scheduler that executes scraping every 12 hours"""
    logger = logging.getLogger(__name__)
    
    try:
        scheduler = ConferenceScheduler()
        scheduler.run_scheduler()
        
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}")
        sys.exit(1)

def run_single_scrape():
    """Run a single scraping job manually"""
    logger = logging.getLogger(__name__)
    
    try:
        scheduler = ConferenceScheduler()
        result = scheduler.run_single_scraping_job()
        
        if result['success']:
            print(f"✅ Scraping completed successfully in {result['duration_seconds']:.2f} seconds")
        else:
            print(f"❌ Scraping failed: {result['error']}")
            
        return result['success']
        
    except Exception as e:
        logger.error(f"Single scrape error: {str(e)}")
        return False

def show_status():
    """Show current status of the system"""
    logger = logging.getLogger(__name__)
    
    try:
        scheduler = ConferenceScheduler()
        
        # Get 2026 data
        df_2026 = scheduler.data_processor.load_2026_data()
        
        if df_2026.empty:
            print("❌ No 2026 data found. Please initialize the system first.")
            return False
        
        # Get incomplete conferences
        incomplete_conferences = scheduler.data_processor.get_incomplete_conferences(df_2026)
        
        # Get scheduler status
        scheduler_status = scheduler.get_status()
        
        # Print status
        print("\n" + "="*50)
        print("📊 CRYPTO CONFERENCE SCRAPER STATUS")
        print("="*50)
        print(f"Total 2026 conferences: {len(df_2026)}")
        print(f"Conferences with missing info: {len(incomplete_conferences)}")
        print(f"Completion rate: {((len(df_2026) - len(incomplete_conferences)) / len(df_2026) * 100):.1f}%")
        print(f"Last run: {scheduler_status['last_run'] or 'Never'}")
        print(f"Next run: {scheduler_status['next_run']}")
        print(f"Total conferences processed: {scheduler_status['total_conferences_processed']}")
        print(f"Total updates made: {scheduler_status['total_updates_made']}")
        print(f"Scraping interval: {scheduler_status['interval_hours']} hours")
        
        if incomplete_conferences:
            print(f"\n🔍 Next {min(5, len(incomplete_conferences))} conferences to scrape:")
            for i, conf in enumerate(incomplete_conferences[:5]):
                print(f"  {i+1}. {conf['conference_name']} ({conf['category']}) - Missing: {', '.join(conf['missing_fields'])}")
        
        print("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return False

def preview_scraping():
    """Preview what will be scraped in the next batch"""
    logger = logging.getLogger(__name__)
    
    try:
        scheduler = ConferenceScheduler()
        next_batch = scheduler.preview_next_scraping_batch(limit=10)
        
        if not next_batch:
            print("✅ No conferences need scraping!")
            return True
        
        print(f"\n🔍 Next {len(next_batch)} conferences to be scraped:")
        print("-" * 80)
        
        for i, conf in enumerate(next_batch):
            print(f"{i+1:2d}. {conf['conference_name']}")
            print(f"    Category: {conf['category']}")
            print(f"    Region: {conf['region']}")
            print(f"    Missing: {', '.join(conf['missing_fields'])}")
            print()
        
        return True
        
    except Exception as e:
        logger.error(f"Preview error: {str(e)}")
        return False

def export_results():
    """Export current results to JSON"""
    logger = logging.getLogger(__name__)
    
    try:
        scheduler = ConferenceScheduler()
        df_2026 = scheduler.data_processor.load_2026_data()
        
        if df_2026.empty:
            print("❌ No 2026 data found.")
            return False
        
        # Convert to JSON
        result = {
            'export_timestamp': datetime.now().isoformat(),
            'total_conferences': len(df_2026),
            'conferences': df_2026.to_dict('records')
        }
        
        # Save to JSON file
        filename = f"conferences_2026_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ Results exported to {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Crypto Conference Scraper - Automatically scrape 2026 conference information"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Initialize command
    subparsers.add_parser('init', help='Initialize the system and create CSV files')
    
    # Scheduler command
    subparsers.add_parser('start', help='Start the scheduler (runs every 12 hours)')
    
    # Single scrape command
    subparsers.add_parser('scrape', help='Run a single scraping job')
    
    # Status command
    subparsers.add_parser('status', help='Show current system status')
    
    # Preview command
    subparsers.add_parser('preview', help='Preview next batch of conferences to scrape')
    
    # Export command
    subparsers.add_parser('export', help='Export current results to JSON')
    
    # Google Sheets commands
    if Config.USE_GOOGLE_SHEETS:
        share_parser = subparsers.add_parser('share', help='Share Google Sheets with an email address')
        share_parser.add_argument('email', help='Email address to share with')
        share_parser.add_argument('--role', default='reader', choices=['reader', 'writer', 'owner'], 
                                help='Permission level (default: reader)')
        
        subparsers.add_parser('url', help='Get Google Sheets URL')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Handle commands
    if args.command == 'init':
        print("🚀 Initializing Crypto Conference Scraper...")
        if initialize_system():
            print("✅ System initialized successfully!")
            print("📝 Next steps:")
            print("  1. Set your OpenAI API key in a .env file: OPENAI_API_KEY=your_key_here")
            print("  2. Run 'python main.py status' to check the system status")
            print("  3. Run 'python main.py scrape' to test a single scraping job")
            print("  4. Run 'python main.py start' to start the scheduler")
        else:
            print("❌ System initialization failed. Check logs for details.")
            sys.exit(1)
    
    elif args.command == 'start':
        print("🚀 Starting Crypto Conference Scraper scheduler...")
        print("📅 Will run every 12 hours. Press Ctrl+C to stop.")
        run_scheduler()
    
    elif args.command == 'scrape':
        print("🔍 Running single scraping job...")
        if run_single_scrape():
            print("✅ Single scraping job completed successfully!")
        else:
            print("❌ Single scraping job failed. Check logs for details.")
            sys.exit(1)
    
    elif args.command == 'status':
        show_status()
    
    elif args.command == 'preview':
        preview_scraping()
    
    elif args.command == 'export':
        export_results()
    
    elif args.command == 'share' and Config.USE_GOOGLE_SHEETS:
        try:
            sheets_processor = GoogleSheetsProcessor()
            sheets_processor.create_or_open_spreadsheet(Config.GOOGLE_SPREADSHEET_NAME)
            sheets_processor.share_spreadsheet(args.email, args.role)
            print(f"✅ Shared Google Sheets with {args.email} as {args.role}")
        except Exception as e:
            print(f"❌ Failed to share Google Sheets: {str(e)}")
    
    elif args.command == 'url' and Config.USE_GOOGLE_SHEETS:
        try:
            sheets_processor = GoogleSheetsProcessor()
            sheets_processor.create_or_open_spreadsheet(Config.GOOGLE_SPREADSHEET_NAME)
            url = sheets_processor.get_spreadsheet_url()
            print(f"📊 Google Sheets URL: {url}")
        except Exception as e:
            print(f"❌ Failed to get Google Sheets URL: {str(e)}")
    
    else:
        parser.print_help()
        storage_type = "Google Sheets" if Config.USE_GOOGLE_SHEETS else "CSV files"
        print(f"\n💡 Quick start (using {storage_type}):")
        print("  1. python main.py init")
        print("  2. python main.py status")
        print("  3. python main.py start")
        if Config.USE_GOOGLE_SHEETS:
            print("  4. python main.py url  # Get Google Sheets URL")
            print("  5. python main.py share user@email.com  # Share with someone")

if __name__ == "__main__":
    main() 