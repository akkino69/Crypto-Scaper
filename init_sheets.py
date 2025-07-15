#!/usr/bin/env python3
"""
Initialize Google Sheets from existing CSV data
This script uploads the CSV data to Google Sheets for the first time
"""

import sys
import logging
from config import Config
from csv_processor import CSVProcessor
from sheets_processor import GoogleSheetsProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Initialize Google Sheets from CSV data"""
    print("🚀 Initializing Google Sheets from CSV data...")
    
    try:
        # Load CSV data
        print("📊 Loading CSV data...")
        csv_processor = CSVProcessor()
        df_2025, df_2026 = csv_processor.load_and_split_data()
        
        # Create 2026 template if no existing data
        if df_2026.empty:
            print("📋 Creating 2026 template...")
            df_2026 = csv_processor.create_2026_template(df_2025)
        
        print(f"✅ Loaded {len(df_2025)} conferences for 2025")
        print(f"✅ Loaded {len(df_2026)} conferences for 2026")
        
        # Initialize Google Sheets
        print("🔗 Connecting to Google Sheets...")
        sheets_processor = GoogleSheetsProcessor()
        sheets_processor.create_or_open_spreadsheet(Config.GOOGLE_SPREADSHEET_NAME)
        
        # Upload data
        print("📤 Uploading data to Google Sheets...")
        sheets_processor.upload_initial_data(df_2025, df_2026)
        
        # Get spreadsheet URL
        url = sheets_processor.get_spreadsheet_url()
        
        print("✅ Successfully initialized Google Sheets!")
        print("=" * 50)
        print(f"📊 Google Sheets URL: {url}")
        print("=" * 50)
        
        # Show next steps
        print("\n🎯 Next steps:")
        print("1. Visit the Google Sheets URL to view your data")
        print("2. Check the Dashboard tab for progress overview")
        print("3. The scraper will automatically update data every 12 hours")
        print("4. You can share the spreadsheet with others using the URL")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing Google Sheets: {str(e)}")
        logging.error(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 