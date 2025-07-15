import gspread
import pandas as pd
import logging
from datetime import datetime
from typing import Tuple, List, Dict, Any, Optional
from google.auth.exceptions import RefreshError
from config import Config
import json
import os

class GoogleSheetsProcessor:
    """Handles Google Sheets operations for the crypto conference scraper"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.gc = None
        self.spreadsheet = None
        self.sheet_2025 = None
        self.sheet_2026 = None
        self.dashboard_sheet = None
        
        # Initialize Google Sheets client
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize Google Sheets client with the best available credentials"""
        try:
            # Try personal credentials first (for cloud deployment)
            if os.path.exists('personal_credentials.json'):
                import google.oauth2.credentials
                from google.auth.transport.requests import Request
                
                # Load personal OAuth2 credentials
                with open('personal_credentials.json', 'r') as f:
                    creds_data = json.load(f)
                
                creds = google.oauth2.credentials.Credentials(
                    token=None,
                    refresh_token=creds_data.get('refresh_token'),
                    id_token=None,
                    token_uri='https://oauth2.googleapis.com/token',
                    client_id=creds_data.get('client_id'),
                    client_secret=creds_data.get('client_secret'),
                    scopes=[
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive'
                    ]
                )
                
                # Refresh the token
                creds.refresh(Request())
                
                self.gc = gspread.authorize(creds)
                self.logger.info("Using personal OAuth2 credentials")
                
            # Try service account credentials
            elif hasattr(Config, 'GOOGLE_SERVICE_ACCOUNT_FILE') and Config.GOOGLE_SERVICE_ACCOUNT_FILE and os.path.exists(Config.GOOGLE_SERVICE_ACCOUNT_FILE):
                self.gc = gspread.service_account(filename=Config.GOOGLE_SERVICE_ACCOUNT_FILE)
                self.logger.info("Using service account credentials")
                
            else:
                # Use application default credentials (local development)
                import google.auth
                from google.auth.transport.requests import Request
                
                # Get application default credentials
                creds, project = google.auth.default(scopes=[
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ])
                
                # Refresh credentials if needed
                if hasattr(creds, 'refresh') and hasattr(creds, 'expired') and creds.expired:
                    creds.refresh(Request())
                
                self.gc = gspread.authorize(creds)
                self.logger.info("Using application default credentials (personal Google account)")
            
            self.logger.info("Google Sheets client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Sheets client: {str(e)}")
            raise
    
    def create_or_open_spreadsheet(self, spreadsheet_name: str = "Crypto Conferences 2026") -> None:
        """Create or open the main spreadsheet"""
        try:
            # Try to open existing spreadsheet
            try:
                self.spreadsheet = self.gc.open(spreadsheet_name)
                self.logger.info(f"Opened existing spreadsheet: {spreadsheet_name}")
            except gspread.SpreadsheetNotFound:
                # Create new spreadsheet
                self.spreadsheet = self.gc.create(spreadsheet_name)
                self.logger.info(f"Created new spreadsheet: {spreadsheet_name}")
            
            # Get or create worksheets
            self._setup_worksheets()
            
        except Exception as e:
            self.logger.error(f"Failed to create/open spreadsheet: {str(e)}")
            raise
    
    def _setup_worksheets(self):
        """Set up the required worksheets"""
        try:
            # Set up 2025 worksheet
            try:
                self.sheet_2025 = self.spreadsheet.worksheet("Conferences 2025")
            except gspread.WorksheetNotFound:
                self.sheet_2025 = self.spreadsheet.add_worksheet("Conferences 2025", rows=200, cols=15)
            
            # Set up 2026 worksheet
            try:
                self.sheet_2026 = self.spreadsheet.worksheet("Conferences 2026")
            except gspread.WorksheetNotFound:
                self.sheet_2026 = self.spreadsheet.add_worksheet("Conferences 2026", rows=200, cols=15)
            
            # Set up dashboard worksheet
            try:
                self.dashboard_sheet = self.spreadsheet.worksheet("Dashboard")
            except gspread.WorksheetNotFound:
                self.dashboard_sheet = self.spreadsheet.add_worksheet("Dashboard", rows=50, cols=10)
                self._setup_dashboard()
            
            self.logger.info("Worksheets set up successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to set up worksheets: {str(e)}")
            raise
    
    def _setup_dashboard(self):
        """Set up the dashboard worksheet with progress tracking"""
        try:
            # Dashboard header
            dashboard_data = [
                ["🚀 Crypto Conference Scraper Dashboard", "", "", "", ""],
                ["", "", "", "", ""],
                ["📊 Progress Overview", "", "", "", ""],
                ["Total Conferences:", "=COUNTA('Conferences 2026'!D:D)-1", "", "", ""],
                ["Completed Conferences:", "=COUNTIF('Conferences 2026'!I:I,\">\"&\"\")", "", "", ""],
                ["Completion Rate:", "=IF(B4>0,B5/B4,0)", "", "", ""],
                ["", "", "", "", ""],
                ["⏱️ Last Updated:", str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), "", "", ""],
                ["🔄 Next Scraping Run:", "Auto-updating every 12 hours", "", "", ""],
                ["", "", "", "", ""],
                ["📋 Field Completion Status", "", "", "", ""],
                ["Dates Complete:", "=COUNTIF('Conferences 2026'!B:B,\">\"&\"\")", "", "", ""],
                ["Locations Complete:", "=COUNTIF('Conferences 2026'!G:G,\">\"&\"\")", "", "", ""],
                ["Speakers Complete:", "=COUNTIF('Conferences 2026'!K:K,\">\"&\"\")", "", "", ""],
                ["Status Complete:", "=COUNTIF('Conferences 2026'!I:I,\">\"&\"\")", "", "", ""],
                ["", "", "", "", ""],
                ["🔗 Quick Links", "", "", "", ""],
                ["Conferences 2026", "👉 View main conference data", "", "", ""],
                ["Conferences 2025", "👉 View 2025 reference data", "", "", ""],
                ["", "", "", "", ""],
                ["🎯 Key Metrics", "", "", "", ""],
                ["Missing Dates:", "=COUNTIF('Conferences 2026'!B:B,\"\")", "", "", ""],
                ["Missing Locations:", "=COUNTIF('Conferences 2026'!G:G,\"\")", "", "", ""],
                ["Missing Speakers:", "=COUNTIF('Conferences 2026'!K:K,\"\")", "", "", ""],
                ["Missing Status:", "=COUNTIF('Conferences 2026'!I:I,\"\")", "", "", ""],
                ["", "", "", "", ""],
                ["📈 Progress Chart", "", "", "", ""],
                ["Field", "Completed", "Missing", "", ""],
                ["Dates", "=B12", "=B22", "", ""],
                ["Locations", "=B13", "=B23", "", ""],
                ["Speakers", "=B14", "=B24", "", ""],
                ["Status", "=B15", "=B25", "", ""],
                ["", "", "", "", ""],
                ["🔧 System Status", "", "", "", ""],
                ["System Status:", "✅ Running", "", "", ""],
                ["API Status:", "✅ Connected", "", "", ""],
                ["Last Error:", "None", "", "", ""],
                ["", "", "", "", ""],
                ["📝 Instructions", "", "", "", ""],
                ["1. Check progress in the metrics above", "", "", "", ""],
                ["2. View detailed data in 'Conferences 2026' tab", "", "", "", ""],
                ["3. System updates automatically every 12 hours", "", "", "", ""],
                ["4. Contact admin if system status shows errors", "", "", "", ""],
            ]
            
            # Update dashboard
            self.dashboard_sheet.update('A1', dashboard_data)
            
            # Format dashboard
            self._format_dashboard()
            
            self.logger.info("Dashboard set up successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to set up dashboard: {str(e)}")
            raise
    
    def _format_dashboard(self):
        """Format the dashboard for better readability"""
        try:
            # Format headers
            self.dashboard_sheet.format('A1:E1', {
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                'textFormat': {'bold': True, 'fontSize': 14},
                'horizontalAlignment': 'CENTER'
            })
            
            # Format section headers
            for row in [3, 11, 17, 21, 27, 33, 39]:
                self.dashboard_sheet.format(f'A{row}:E{row}', {
                    'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9},
                    'textFormat': {'bold': True}
                })
            
            # Format percentage cells
            self.dashboard_sheet.format('B6', {'numberFormat': {'type': 'PERCENT', 'pattern': '0.0%'}})
            
            self.logger.info("Dashboard formatted successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to format dashboard: {str(e)}")
    
    def upload_initial_data(self, df_2025: pd.DataFrame, df_2026: pd.DataFrame):
        """Upload initial data from CSV files to Google Sheets"""
        try:
            # Clean data by replacing NaN values with empty strings
            df_2025_clean = df_2025.fillna('')
            df_2026_clean = df_2026.fillna('')
            
            # Upload 2025 data
            self.logger.info("Uploading 2025 data to Google Sheets...")
            self.sheet_2025.clear()
            self.sheet_2025.update('A1', [df_2025_clean.columns.tolist()] + df_2025_clean.values.tolist())
            
            # Upload 2026 data
            self.logger.info("Uploading 2026 data to Google Sheets...")
            self.sheet_2026.clear()
            self.sheet_2026.update('A1', [df_2026_clean.columns.tolist()] + df_2026_clean.values.tolist())
            
            # Update dashboard timestamp
            self.update_dashboard_timestamp()
            
            self.logger.info("Initial data uploaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to upload initial data: {str(e)}")
            raise
    
    def load_2026_data(self) -> pd.DataFrame:
        """Load the 2026 conference data from Google Sheets"""
        try:
            # Get all values from 2026 sheet
            values = self.sheet_2026.get_all_values()
            
            if not values:
                self.logger.warning("No data found in 2026 sheet")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(values[1:], columns=values[0])
            
            # Clean empty rows
            df = df.dropna(subset=['Conference Name'], how='all')
            df = df[df['Conference Name'].str.strip() != '']
            
            self.logger.info(f"Loaded {len(df)} records from Google Sheets")
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to load 2026 data: {str(e)}")
            raise
    
    def get_incomplete_conferences(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Get conferences that have missing information"""
        incomplete_conferences = []
        
        for idx, row in df.iterrows():
            missing_fields = []
            
            for field in Config.FIELDS_TO_SCRAPE:
                if field in df.columns:
                    if pd.isna(row[field]) or str(row[field]).strip() == "":
                        missing_fields.append(field)
            
            if missing_fields:
                conference_info = {
                    'index': idx,
                    'conference_name': row['Conference Name'],
                    'category': row.get('Category', ''),
                    'region': row.get('Region', ''),
                    'missing_fields': missing_fields,
                    'existing_data': row.to_dict()
                }
                incomplete_conferences.append(conference_info)
        
        self.logger.info(f"Found {len(incomplete_conferences)} conferences with missing information")
        return incomplete_conferences
    
    def update_conference_data(self, df: pd.DataFrame, index: int, field_updates: Dict[str, Any]) -> pd.DataFrame:
        """Update specific fields for a conference and sync to Google Sheets"""
        try:
            # Update DataFrame
            for field, value in field_updates.items():
                if field in df.columns:
                    df.at[index, field] = str(value)
                    self.logger.info(f"Updated {field} for conference at index {index}")
            
            # Update Google Sheets
            self._sync_row_to_sheets(df, index)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error updating conference data: {str(e)}")
            raise
    
    def _sync_row_to_sheets(self, df: pd.DataFrame, index: int):
        """Sync a specific row to Google Sheets"""
        try:
            # Get the row data
            row_data = df.iloc[index].tolist()
            
            # Update the row in Google Sheets (index+2 because of header row and 1-based indexing)
            sheet_row = index + 2
            self.sheet_2026.update(f'A{sheet_row}', [row_data])
            
            self.logger.info(f"Synced row {index} to Google Sheets")
            
        except Exception as e:
            self.logger.error(f"Failed to sync row to Google Sheets: {str(e)}")
            raise
    
    def update_dashboard_timestamp(self):
        """Update the dashboard with current timestamp"""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.dashboard_sheet.update('B8', current_time)
            self.logger.info("Dashboard timestamp updated")
            
        except Exception as e:
            self.logger.warning(f"Failed to update dashboard timestamp: {str(e)}")
    
    def update_system_status(self, status: str, api_status: str = "✅ Connected", last_error: str = "None"):
        """Update system status in dashboard"""
        try:
            self.dashboard_sheet.update('B34', status)
            self.dashboard_sheet.update('B35', api_status)
            self.dashboard_sheet.update('B36', last_error)
            self.logger.info("System status updated")
            
        except Exception as e:
            self.logger.warning(f"Failed to update system status: {str(e)}")
    
    def get_spreadsheet_url(self) -> str:
        """Get the URL of the spreadsheet"""
        if self.spreadsheet:
            return self.spreadsheet.url
        return ""
    
    def share_spreadsheet(self, email: str, role: str = 'reader'):
        """Share the spreadsheet with an email address"""
        try:
            self.spreadsheet.share(email, perm_type='user', role=role)
            self.logger.info(f"Shared spreadsheet with {email} as {role}")
            
        except Exception as e:
            self.logger.error(f"Failed to share spreadsheet: {str(e)}")
            raise
    
    def initialize_from_csv(self, csv_2025_path: str, csv_2026_path: str):
        """Initialize Google Sheets from existing CSV files"""
        try:
            # Load CSV files
            df_2025 = pd.read_csv(csv_2025_path)
            df_2026 = pd.read_csv(csv_2026_path)
            
            # Upload to Google Sheets
            self.upload_initial_data(df_2025, df_2026)
            
            self.logger.info("Successfully initialized Google Sheets from CSV files")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize from CSV: {str(e)}")
            raise 