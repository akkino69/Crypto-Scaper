# Crypto Conference Scraper

A Python program that automatically scrapes web information for 2026 crypto conferences using OpenAI's ChatGPT API. The program takes a CSV file of 2025 conferences, creates a 2026 template, and regularly searches the web to fill in missing information like dates, venues, and speakers.

## Features

- 🤖 **Automated Web Scraping**: Uses ChatGPT API with web search capabilities
- 📊 **CSV Processing**: Splits 2025/2026 data and manages conference information
- ⏰ **Scheduled Execution**: Runs every 12 hours automatically
- 🔍 **Smart Search**: Searches for missing dates, venues, speakers, and attendance info
- 📝 **Comprehensive Logging**: Detailed logs for monitoring and debugging
- 🎯 **Targeted Updates**: Only scrapes conferences with missing information
- 💾 **JSON Export**: Export results to JSON format
- 🖥️ **Command Line Interface**: Easy-to-use CLI for all operations

## Installation

1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   Get your OpenAI API key from: https://platform.openai.com/account/api-keys

4. **Initialize the system**:
   ```bash
   python main.py init
   ```

## Usage

### Commands

- **Initialize the system**:
  ```bash
  python main.py init
  ```
  Creates the 2025 and 2026 CSV files from your original data.

- **Start the scheduler** (runs every 12 hours):
  ```bash
  python main.py start
  ```
  Starts the automatic scraping process. Press Ctrl+C to stop.

- **Run a single scraping job**:
  ```bash
  python main.py scrape
  ```
  Manually trigger one scraping session for testing.

- **Check system status**:
  ```bash
  python main.py status
  ```
  Shows completion statistics and next conferences to scrape.

- **Preview next batch**:
  ```bash
  python main.py preview
  ```
  See which conferences will be scraped next.

- **Export results**:
  ```bash
  python main.py export
  ```
  Export current results to a JSON file.

### Quick Start

1. Run `python main.py init` to set up the system
2. Run `python main.py status` to check what needs scraping
3. Run `python main.py scrape` to test a single scraping job
4. Run `python main.py start` to begin automatic scraping

## How It Works

1. **Data Separation**: The program reads your original CSV file and separates 2025 and 2026 data
2. **Template Creation**: Creates a 2026 template with empty fields for missing information
3. **Web Scraping**: Uses ChatGPT API to search for missing conference details:
   - Start and end dates
   - Venue locations
   - Key speakers
   - Expected attendance
   - Conference status
4. **Data Updates**: Validates and updates the CSV with found information
5. **Scheduling**: Repeats the process every 12 hours

## File Structure

```
crypto-scraper/
├── main.py                 # Main program entry point
├── config.py               # Configuration settings
├── csv_processor.py        # CSV handling and data processing
├── web_scraper.py          # OpenAI API integration for web scraping
├── scheduler.py            # Scheduling and automation
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── conferences_2025.csv    # Generated 2025 data
├── conferences_2026.csv    # Generated 2026 data (updated by scraper)
└── scraper.log            # Log file
```

## Configuration

You can customize the scraper by modifying `config.py` or setting environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: gpt-4o-mini)
- `SCRAPING_INTERVAL_HOURS`: How often to run (default: 12)
- `LOG_LEVEL`: Logging level (default: INFO)

## API Usage and Costs

The scraper uses OpenAI's API with web search capabilities. Costs depend on:
- Number of conferences with missing information
- API calls made (roughly 1 call per conference)
- Current OpenAI pricing

**Cost Estimation**: 
- ~100 conferences = ~$1-2 per scraping session
- Running every 12 hours = ~$60-120 per month (decreases as data is filled)

## Logging

The program creates detailed logs in `scraper.log` including:
- Scraping progress and results
- API calls and responses
- Errors and debugging information
- System status updates

## Error Handling

The scraper includes robust error handling:
- API rate limiting and retries
- JSON parsing validation
- Network timeout handling
- Graceful failure recovery

## Troubleshooting

**Common Issues**:

1. **API Key Error**: Make sure your OpenAI API key is set correctly in `.env`
2. **No Data Found**: Check that your original CSV file is in the correct format
3. **Rate Limiting**: The scraper includes delays between API calls
4. **Parsing Errors**: Check logs for JSON parsing issues

**Debug Steps**:
1. Run `python main.py status` to check system state
2. Check `scraper.log` for detailed error messages
3. Run `python main.py scrape` to test a single job
4. Verify your `.env` file is properly configured

## Data Format

The scraper looks for these fields in your CSV:
- Conference Name (required)
- Category, Region (used for search context)
- Start Date, End Date (MM/DD format)
- Location (venue and city)
- Speaker (key speakers)
- Attendees (expected attendance)
- Status (confirmed, tentative, etc.)

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions:
1. Check the logs in `scraper.log`
2. Run `python main.py status` to diagnose
3. Ensure your OpenAI API key is valid and has credits

---

**Note**: This scraper uses OpenAI's API which may have usage costs. Monitor your API usage and costs through the OpenAI dashboard. 