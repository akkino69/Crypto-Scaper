import pandas as pd
import logging
from typing import Tuple, List, Dict, Any
from config import Config

class CSVProcessor:
    """Handles CSV file operations for the crypto conference scraper"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def load_and_split_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load the main CSV file and split into 2025 and 2026 data
        Returns: (df_2025, df_2026)
        """
        try:
            # Read the CSV file
            df = pd.read_csv(Config.INPUT_CSV)
            
            # Find the row where 2026 data starts (look for "2026" in any column)
            year_2026_row = None
            for idx, row in df.iterrows():
                if '2026' in str(row.values):
                    year_2026_row = idx
                    break
            
            if year_2026_row is None:
                self.logger.warning("No 2026 data found in CSV")
                return df, pd.DataFrame()
            
            # Split the data
            df_2025 = df.iloc[:year_2026_row].copy()
            df_2026 = df.iloc[year_2026_row+1:].copy()  # Skip the "2026" row
            
            # Clean the data - remove empty rows
            df_2025 = df_2025.dropna(subset=['Conference Name'])
            df_2026 = df_2026.dropna(subset=['Conference Name'])
            
            self.logger.info(f"Loaded {len(df_2025)} conferences for 2025")
            self.logger.info(f"Loaded {len(df_2026)} conferences for 2026")
            
            return df_2025, df_2026
            
        except Exception as e:
            self.logger.error(f"Error loading CSV data: {str(e)}")
            raise
    
    def create_2026_template(self, df_2025: pd.DataFrame) -> pd.DataFrame:
        """
        Create a 2026 template based on 2025 conferences with empty fields
        """
        try:
            # Create a copy of 2025 data
            df_2026_template = df_2025.copy()
            
            # Clear the fields we want to scrape
            fields_to_clear = Config.FIELDS_TO_SCRAPE
            
            for field in fields_to_clear:
                if field in df_2026_template.columns:
                    df_2026_template[field] = ""
            
            # Update quarter information to match 2026 dates
            # This is a simple mapping - you may want to adjust based on actual 2026 calendar
            df_2026_template['Quarter'] = df_2026_template['Quarter']
            
            self.logger.info(f"Created 2026 template with {len(df_2026_template)} conferences")
            
            return df_2026_template
            
        except Exception as e:
            self.logger.error(f"Error creating 2026 template: {str(e)}")
            raise
    
    def save_csv(self, df: pd.DataFrame, filename: str) -> None:
        """Save dataframe to CSV file"""
        try:
            df.to_csv(filename, index=False)
            self.logger.info(f"Saved {len(df)} records to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving CSV {filename}: {str(e)}")
            raise
    
    def load_2026_data(self) -> pd.DataFrame:
        """Load the 2026 CSV file for updating"""
        try:
            if not pd.io.common.file_exists(Config.OUTPUT_2026_CSV):
                self.logger.warning(f"2026 CSV file not found: {Config.OUTPUT_2026_CSV}")
                return pd.DataFrame()
            
            df = pd.read_csv(Config.OUTPUT_2026_CSV)
            self.logger.info(f"Loaded {len(df)} records from 2026 CSV")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading 2026 CSV: {str(e)}")
            raise
    
    def get_incomplete_conferences(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Get conferences that have missing information in the specified fields
        """
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
        """
        Update specific fields for a conference at the given index
        """
        try:
            for field, value in field_updates.items():
                if field in df.columns:
                    df.at[index, field] = value
                    self.logger.info(f"Updated {field} for conference at index {index}")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error updating conference data: {str(e)}")
            raise
    
    def initialize_csv_files(self) -> None:
        """Initialize the 2025 and 2026 CSV files"""
        try:
            # Load and split the original data
            df_2025, df_2026_existing = self.load_and_split_data()
            
            # Save 2025 data
            self.save_csv(df_2025, Config.OUTPUT_2025_CSV)
            
            # Create 2026 template if no existing 2026 data
            if df_2026_existing.empty:
                df_2026_template = self.create_2026_template(df_2025)
                self.save_csv(df_2026_template, Config.OUTPUT_2026_CSV)
            else:
                # Merge existing 2026 data with template
                df_2026_template = self.create_2026_template(df_2025)
                
                # Update template with existing data
                for idx, row in df_2026_existing.iterrows():
                    conference_name = row['Conference Name']
                    matching_rows = df_2026_template[df_2026_template['Conference Name'] == conference_name]
                    
                    if not matching_rows.empty:
                        template_idx = matching_rows.index[0]
                        # Update fields that have data in the existing dataset
                        for col in df_2026_existing.columns:
                            if col in df_2026_template.columns and pd.notna(row[col]) and str(row[col]).strip():
                                df_2026_template.at[template_idx, col] = row[col]
                
                self.save_csv(df_2026_template, Config.OUTPUT_2026_CSV)
            
            self.logger.info("CSV files initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing CSV files: {str(e)}")
            raise 