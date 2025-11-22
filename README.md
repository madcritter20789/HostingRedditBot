# Reddit Stock Tracker Bot

A Python bot that monitors Reddit comments for stock ticker mentions, tracks their frequency, and fetches live stock prices.

## Features

- 🔍 Real-time monitoring of Reddit comments across multiple subreddits
- 📊 Automatic extraction of stock tickers (symbols starting with $)
- 📈 Frequency tracking of mentioned stocks
- 💰 Live stock price fetching using Yahoo Finance
- 🏆 Top 5 most mentioned stocks ranking
- 📝 Comprehensive logging to file and console
- 🔒 Secure credential management with environment variables

## Requirements

- Python 3.8.5 or higher
- Reddit API credentials
- Internet connection

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd HostingRedditBot
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Reddit API Credentials

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in the form:
   - **name**: Your bot name (e.g., "Stock Tracker Bot")
   - **App type**: Select "script"
   - **description**: Optional description
   - **about url**: Leave blank
   - **redirect uri**: http://localhost:8080
4. Click "Create app"
5. Note down:
   - **client_id**: The string under "personal use script"
   - **client_secret**: The "secret" value

### 5. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your Reddit credentials:
   ```bash
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USERNAME=your_reddit_username
   REDDIT_PASSWORD=your_reddit_password
   REDDIT_USER_AGENT=reddit_stock_tracker_bot

   # Optional: Customize these
   SUBREDDITS=wallstreetbets+stocks+personalfinance
   TOP_STOCKS_COUNT=5
   ```

## Usage

### Run Locally

```bash
python main.py
```

The bot will:
1. Authenticate with Reddit
2. Start monitoring configured subreddits
3. Display stock mentions and rankings in real-time
4. Save logs to `reddit_bot.log`

### Stop the Bot

Press `Ctrl+C` to gracefully stop the bot.

## Configuration

You can customize the bot behavior by editing the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `REDDIT_CLIENT_ID` | Reddit app client ID | Required |
| `REDDIT_CLIENT_SECRET` | Reddit app secret | Required |
| `REDDIT_USERNAME` | Your Reddit username | Required |
| `REDDIT_PASSWORD` | Your Reddit password | Required |
| `REDDIT_USER_AGENT` | Bot identifier | `reddit_stock_tracker_bot` |
| `SUBREDDITS` | Subreddits to monitor (+ separated) | `wallstreetbets+stocks+personalfinance` |
| `TOP_STOCKS_COUNT` | Number of top stocks to track | `5` |

## How It Works

1. **Comment Streaming**: The bot continuously monitors new comments from specified subreddits
2. **Ticker Extraction**: When a comment contains "$", the bot extracts the potential stock ticker
3. **Validation**: Tickers are validated (max 6 characters, no numbers immediately after $)
4. **Ranking**: Each mention increments the ticker's count
5. **Price Fetching**: Top stocks get their live prices from Yahoo Finance
6. **Display**: Rankings and prices are logged to console and file

## Example Output

```
2025-11-22 12:00:00 - INFO - Successfully authenticated as: your_username
2025-11-22 12:00:01 - INFO - Starting Reddit bot monitoring: wallstreetbets+stocks+personalfinance
2025-11-22 12:00:01 - INFO - Tracking top 5 stocks
2025-11-22 12:00:15 - INFO - New stock ticker found: $TSLA
2025-11-22 12:00:15 - INFO - Fetched price for $TSLA: $242.84

==================================================
CURRENT RANKINGS:
Rankings: {'$TSLA': 1, '$AAPL': 3, '$GME': 2}
Top 5: ['$AAPL', '$GME', '$TSLA']
Prices: {'$AAPL': 189.25, '$GME': 25.67, '$TSLA': 242.84}
==================================================
```

## Deployment

### Heroku Deployment

This bot includes Heroku configuration files:
- `Procfile`: Defines worker and web processes
- `Runtime.txt`: Specifies Python version
- `requirements.txt`: Lists all dependencies

To deploy to Heroku:

```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-app-name

# Set environment variables
heroku config:set REDDIT_CLIENT_ID=your_client_id
heroku config:set REDDIT_CLIENT_SECRET=your_client_secret
heroku config:set REDDIT_USERNAME=your_username
heroku config:set REDDIT_PASSWORD=your_password

# Push to Heroku
git push heroku main

# Scale worker
heroku ps:scale worker=1
```

## Troubleshooting

### "Missing required environment variables"
- Ensure you've created a `.env` file with all required variables
- Check that variable names match exactly

### "Failed to initialize Reddit client"
- Verify your Reddit credentials are correct
- Check that your Reddit account is in good standing
- Ensure your app type is set to "script" on Reddit

### "Error fetching price for [ticker]"
- Some tickers may not be valid stock symbols
- Yahoo Finance API might be temporarily unavailable
- The ticker might be delisted or invalid

### No comments appearing
- The subreddits might have low activity
- Try adding more subreddits in the `SUBREDDITS` variable
- Check your Reddit app permissions

## Files Description

- `main.py`: Main bot script
- `requirements.txt`: Python dependencies (standard naming)
- `Requirement.txt`: Python dependencies (Heroku compatibility)
- `Procfile`: Heroku process configuration
- `Runtime.txt`: Python version specification
- `.env`: Your environment variables (not committed)
- `.env.example`: Template for environment variables
- `.gitignore`: Git ignore rules
- `README.md`: This file

## Security Notes

- ⚠️ Never commit your `.env` file to version control
- ⚠️ Keep your Reddit credentials secure
- ⚠️ Use environment variables for all sensitive data
- ⚠️ Regularly rotate your Reddit app credentials

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review Reddit API documentation: https://www.reddit.com/dev/api
3. Check PRAW documentation: https://praw.readthedocs.io/

## Changelog

### Version 2.0 (Latest)
- ✅ Added environment variable support
- ✅ Implemented comprehensive logging
- ✅ Fixed logic bug in stock price fetching
- ✅ Added error handling and validation
- ✅ Improved code documentation
- ✅ Added local development support
- ✅ Created setup documentation

### Version 1.0
- Initial release with basic functionality
