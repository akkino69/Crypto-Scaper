import json
import logging
import time
from typing import Dict, Any, Union, List
from openai import OpenAI
from config import Config

class ConferenceScraper:
    """Web scraper that uses ChatGPT API to find missing conference information"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
    def create_search_prompt(self, conference_info: Dict[str, Any]) -> str:
        """
        Create a search prompt for the ChatGPT API
        """
        conference_name = conference_info['conference_name']
        category = conference_info.get('category', '')
        region = conference_info.get('region', '')
        missing_fields = conference_info['missing_fields']
        
        prompt = f"""You are tasked with finding information about the conference "{conference_name}" for 2026.

Conference Details:
- Name: {conference_name}
- Category: {category}
- Region: {region}

I need you to search the web and find the following missing information for this conference in 2026:
{', '.join(missing_fields)}

Please search for:
1. Start Date and End Date (in MM/DD format)
2. Venue/Location (specific venue name and city)
3. Key Speakers (notable speakers or keynote speakers)
4. Expected Attendees (approximate number if available)
5. Current Status (confirmed, tentative, cancelled, etc.)

Return ONLY a JSON object with the found information. Use these exact field names:
- "Start Date": "MM/DD" format
- "End Date": "MM/DD" format  
- "Location": "Venue Name, City"
- "Speaker": "Key speaker names"
- "Attendees": "Number or description"
- "Status": "Current status"

If you cannot find information for a specific field, use null for that field.
If you cannot find ANY information about this conference for 2026, return false.

Example response format:
{{
    "Start Date": "05/15",
    "End Date": "05/17",
    "Location": "Convention Center, Miami",
    "Speaker": "Vitalik Buterin, CZ",
    "Attendees": "5000+",
    "Status": "Confirmed"
}}

Search the web now and provide the information about "{conference_name}" for 2026."""
        
        return prompt
    
    def search_conference_info(self, conference_info: Dict[str, Any]) -> Union[Dict[str, Any], bool]:
        """
        Search for conference information using OpenAI Responses API with web search
        Returns: Dictionary with found information or False if nothing found
        """
        try:
            prompt = self.create_search_prompt(conference_info)
            
            self.logger.info(f"Searching for information about: {conference_info['conference_name']}")
            
            response = self.client.responses.create(
                model="o4-mini",  # Use the model that supports web search
                tools=[
                    {
                        "type": "web_search_preview",
                        "user_location": {
                            "type": "approximate",
                            "country": "US",
                            "city": "San Francisco",
                            "region": "California",
                        },
                        "search_context_size": "low",
                    }
                ],
                input=prompt
            )
            
            response_text = response.output_text.strip()
            
            # Try to parse the JSON response
            try:
                if response_text.lower() == 'false':
                    self.logger.info(f"No information found for: {conference_info['conference_name']}")
                    return False
                
                # Remove markdown formatting if present
                if response_text.startswith('```json'):
                    response_text = response_text.replace('```json', '').replace('```', '').strip()
                
                parsed_response = json.loads(response_text)
                
                # Filter out null values and empty strings
                filtered_response = {}
                for key, value in parsed_response.items():
                    if value is not None and str(value).strip() != '':
                        filtered_response[key] = value
                
                if filtered_response:
                    self.logger.info(f"Found information for {conference_info['conference_name']}: {list(filtered_response.keys())}")
                    return filtered_response
                else:
                    self.logger.info(f"No valid information found for: {conference_info['conference_name']}")
                    return False
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON response for {conference_info['conference_name']}: {e}")
                self.logger.debug(f"Response was: {response_text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error searching for {conference_info['conference_name']}: {str(e)}")
            return False
    
    def scrape_batch(self, conferences: List[Dict[str, Any]], batch_size: int = 5) -> List[Dict[str, Any]]:
        """
        Scrape information for a batch of conferences
        """
        results = []
        
        for i in range(0, len(conferences), batch_size):
            batch = conferences[i:i + batch_size]
            
            self.logger.info(f"Processing batch {i//batch_size + 1} of {len(conferences)//batch_size + 1}")
            
            for conference in batch:
                try:
                    result = self.search_conference_info(conference)
                    
                    results.append({
                        'conference_info': conference,
                        'scraped_data': result,
                        'timestamp': time.time()
                    })
                    
                    # Add delay between requests to avoid rate limiting
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"Error processing conference {conference['conference_name']}: {str(e)}")
                    results.append({
                        'conference_info': conference,
                        'scraped_data': False,
                        'timestamp': time.time(),
                        'error': str(e)
                    })
            
            # Add longer delay between batches
            if i + batch_size < len(conferences):
                self.logger.info("Waiting between batches...")
                time.sleep(10)
        
        return results
    
    def validate_scraped_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean scraped data
        """
        validated_data = {}
        
        # Validate date format
        for date_field in ['Start Date', 'End Date']:
            if date_field in data:
                date_value = str(data[date_field]).strip()
                # Basic date validation - should be MM/DD format
                if '/' in date_value and len(date_value) <= 5:
                    validated_data[date_field] = date_value
        
        # Validate location
        if 'Location' in data:
            location = str(data['Location']).strip()
            if len(location) > 0:
                validated_data['Location'] = location
        
        # Validate speaker
        if 'Speaker' in data:
            speaker = str(data['Speaker']).strip()
            if len(speaker) > 0:
                validated_data['Speaker'] = speaker
        
        # Validate attendees
        if 'Attendees' in data:
            attendees = str(data['Attendees']).strip()
            if len(attendees) > 0:
                validated_data['Attendees'] = attendees
        
        # Validate status
        if 'Status' in data:
            status = str(data['Status']).strip()
            if len(status) > 0:
                validated_data['Status'] = status
        
        return validated_data
    
    def get_rate_limit_delay(self) -> int:
        """
        Get the delay between API calls to avoid rate limiting
        """
        return 2  # 2 seconds between calls
    
    def test_api_connection(self) -> bool:
        """
        Test if the OpenAI API connection is working
        """
        try:
            response = self.client.responses.create(
                model="o4-mini",
                tools=[
                    {
                        "type": "web_search_preview",
                        "search_context_size": "low",
                    }
                ],
                input="Hello, please respond with 'API test successful'"
            )
            
            if "successful" in response.output_text.lower():
                self.logger.info("API connection test successful")
                return True
            else:
                self.logger.error("API connection test failed - unexpected response")
                return False
                
        except Exception as e:
            self.logger.error(f"API connection test failed: {str(e)}")
            return False 