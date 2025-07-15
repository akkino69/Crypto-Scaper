import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from config import Config
from csv_processor import CSVProcessor
from sheets_processor import GoogleSheetsProcessor
from web_scraper import ConferenceScraper

class ConferenceScheduler:
    """Scheduler that runs the conference scraper every 12 hours"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize data processor (CSV or Google Sheets)
        if Config.USE_GOOGLE_SHEETS:
            self.data_processor = GoogleSheetsProcessor()
            self.logger.info("Using Google Sheets for data storage (lazy initialization)")
        else:
            self.data_processor = CSVProcessor()
            self.logger.info("Using CSV files for data storage")
        
        self._sheets_initialized = False
        
        self.scraper = ConferenceScraper()
        self.last_run = None
        self.total_conferences_processed = 0
        self.total_updates_made = 0
    
    def _ensure_sheets_initialized(self):
        """Ensure Google Sheets is initialized when needed"""
        if Config.USE_GOOGLE_SHEETS and not self._sheets_initialized:
            try:
                self.data_processor.create_or_open_spreadsheet(Config.GOOGLE_SPREADSHEET_NAME)
                self._sheets_initialized = True
                self.logger.info("Google Sheets initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Google Sheets: {str(e)}")
                raise
        
    def run_scraping_job(self) -> None:
        """
        Main scraping job that gets executed on schedule
        """
        self.logger.info("Starting scheduled scraping job...")
        start_time = datetime.now()
        
        try:
            # Ensure Google Sheets is initialized if needed
            self._ensure_sheets_initialized()
            
            # Test API connection first
            if not self.scraper.test_api_connection():
                self.logger.error("API connection test failed. Skipping scraping job.")
                return
            
            # Load 2026 data
            df_2026 = self.data_processor.load_2026_data()
            
            if df_2026.empty:
                self.logger.error("No 2026 data found. Please initialize data storage first.")
                return
            
            # Get conferences with missing information
            incomplete_conferences = self.data_processor.get_incomplete_conferences(df_2026)
            
            if not incomplete_conferences:
                self.logger.info("No conferences with missing information found.")
                return
            
            self.logger.info(f"Found {len(incomplete_conferences)} conferences with missing information")
            
            # Scrape information for incomplete conferences
            scraping_results = self.scraper.scrape_batch(incomplete_conferences, batch_size=3)
            
            # Process results and update CSV
            updates_made = 0
            for result in scraping_results:
                if result['scraped_data'] and result['scraped_data'] is not False:
                    # Validate the scraped data
                    validated_data = self.scraper.validate_scraped_data(result['scraped_data'])
                    
                    if validated_data:
                        # Update the dataframe
                        conference_index = result['conference_info']['index']
                        df_2026 = self.data_processor.update_conference_data(
                            df_2026, conference_index, validated_data
                        )
                        updates_made += 1
                        
                        self.logger.info(f"Updated {result['conference_info']['conference_name']} with {len(validated_data)} fields")
            
            # Save updated data
            if updates_made > 0:
                if Config.USE_GOOGLE_SHEETS:
                    self.data_processor.update_dashboard_timestamp()
                    self.data_processor.update_system_status("✅ Running", "✅ Connected", "None")
                else:
                    self.data_processor.save_csv(df_2026, Config.OUTPUT_2026_CSV)
                self.logger.info(f"Saved {updates_made} updates to data storage")
            
            # Update statistics
            self.total_conferences_processed += len(incomplete_conferences)
            self.total_updates_made += updates_made
            self.last_run = datetime.now()
            
            # Log summary
            duration = datetime.now() - start_time
            self.logger.info(f"Scraping job completed in {duration.total_seconds():.2f} seconds")
            self.logger.info(f"Processed: {len(incomplete_conferences)} conferences, Updated: {updates_made} conferences")
            
        except Exception as e:
            self.logger.error(f"Error in scraping job: {str(e)}")
            raise
    
    def schedule_jobs(self) -> None:
        """
        Schedule the scraping job to run every 12 hours
        """
        # Schedule job every 12 hours
        schedule.every(Config.SCRAPING_INTERVAL_HOURS).hours.do(self.run_scraping_job)
        
        # You can also schedule specific times
        # schedule.every().day.at("09:00").do(self.run_scraping_job)
        # schedule.every().day.at("21:00").do(self.run_scraping_job)
        
        self.logger.info(f"Scheduled scraping job to run every {Config.SCRAPING_INTERVAL_HOURS} hours")
    
    def run_scheduler(self) -> None:
        """
        Run the scheduler indefinitely
        """
        self.logger.info("Starting conference scraper scheduler...")
        
        # Schedule jobs
        self.schedule_jobs()
        
        # Run once immediately
        self.logger.info("Running initial scraping job...")
        self.run_scraping_job()
        
        # Keep the scheduler running
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                self.logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in scheduler: {str(e)}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def get_next_run_time(self) -> datetime:
        """
        Get the next scheduled run time
        """
        next_run = schedule.next_run()
        return next_run if next_run else datetime.now()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the scheduler
        """
        return {
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.get_next_run_time().isoformat(),
            'total_conferences_processed': self.total_conferences_processed,
            'total_updates_made': self.total_updates_made,
            'scheduled_jobs': len(schedule.jobs),
            'interval_hours': Config.SCRAPING_INTERVAL_HOURS
        }
    
    def run_single_scraping_job(self) -> Dict[str, Any]:
        """
        Run a single scraping job manually (for testing)
        """
        self.logger.info("Running single scraping job manually...")
        
        start_time = datetime.now()
        
        try:
            self.run_scraping_job()
            
            duration = datetime.now() - start_time
            
            return {
                'success': True,
                'duration_seconds': duration.total_seconds(),
                'timestamp': start_time.isoformat(),
                'message': 'Scraping job completed successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': start_time.isoformat(),
                'message': 'Scraping job failed'
            }
    
    def stop_scheduler(self) -> None:
        """
        Stop the scheduler and clear all jobs
        """
        schedule.clear()
        self.logger.info("Scheduler stopped and all jobs cleared")
    
    def set_custom_schedule(self, hours: int = None, specific_times: List[str] = None) -> None:
        """
        Set a custom schedule for the scraping job
        
        Args:
            hours: Run every N hours
            specific_times: List of specific times to run (e.g., ["09:00", "21:00"])
        """
        # Clear existing jobs
        schedule.clear()
        
        if hours:
            schedule.every(hours).hours.do(self.run_scraping_job)
            self.logger.info(f"Set custom schedule: every {hours} hours")
        
        if specific_times:
            for time_str in specific_times:
                schedule.every().day.at(time_str).do(self.run_scraping_job)
                self.logger.info(f"Set custom schedule: daily at {time_str}")
        
        if not hours and not specific_times:
            # Default to 12 hours if no custom schedule provided
            self.schedule_jobs()
    
    def get_incomplete_conferences_count(self) -> int:
        """
        Get the current number of conferences with missing information
        """
        try:
            self._ensure_sheets_initialized()
            df_2026 = self.data_processor.load_2026_data()
            if df_2026.empty:
                return 0
            
            incomplete_conferences = self.data_processor.get_incomplete_conferences(df_2026)
            return len(incomplete_conferences)
            
        except Exception as e:
            self.logger.error(f"Error getting incomplete conferences count: {str(e)}")
            return 0
    
    def preview_next_scraping_batch(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Preview the next batch of conferences that will be scraped
        """
        try:
            self._ensure_sheets_initialized()
            df_2026 = self.data_processor.load_2026_data()
            if df_2026.empty:
                return []
            
            incomplete_conferences = self.data_processor.get_incomplete_conferences(df_2026)
            
            # Return preview of next batch
            return incomplete_conferences[:limit]
            
        except Exception as e:
            self.logger.error(f"Error previewing next scraping batch: {str(e)}")
            return [] 