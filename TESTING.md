# Testing Guide

This document explains how to test the Reddit Stock Tracker Bot locally.

## Pre-Installation Tests

Run these tests to verify the project structure before installing dependencies:

```bash
# Check file structure
ls -la

# Verify Python version
python --version  # Should be 3.8.5 or higher
```

## Installation Testing

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Automated Tests

```bash
python test_bot.py
```

This will test:
- ✓ File structure
- ✓ Package imports
- ✓ Stock price fetching (uses Yahoo Finance)
- ✓ Ticker extraction logic
- ✓ Environment configuration

Expected output with dependencies installed:
```
============================================================
Reddit Stock Tracker Bot - Test Suite
============================================================

Testing file structure...
✓ main.py exists
✓ requirements.txt exists
✓ Requirement.txt exists
✓ Procfile exists
✓ Runtime.txt exists
✓ .env.example exists
✓ .gitignore exists
✓ README.md exists

Testing imports...
✓ praw imported successfully
✓ yahoo_fin imported successfully
✓ python-dotenv imported successfully
✓ heapq imported successfully

Testing stock price fetching...
Fetching price for AAPL...
✓ Successfully fetched price for AAPL: $XXX.XX

Testing ticker extraction logic...
✓ 'I bought $TSLA today' -> $TSLA
✓ '$AAPL is going up!' -> $AAPL
✓ 'Check out $GME and $AMC' -> $GME
✓ 'Price is $100.50' -> None
✓ '$TOOLONGticker' -> None

Testing environment configuration...
✓ .env.example file exists
⚠ .env file not found (create it from .env.example)

============================================================
Test Summary
============================================================
✓ PASS: File Structure
✓ PASS: Package Imports
✓ PASS: Stock Price Fetching
✓ PASS: Ticker Extraction
✓ PASS: Environment Configuration

Total: 5/5 tests passed

🎉 All tests passed! The bot is ready to use.
```

## Manual Testing

### 1. Environment Setup Test

```bash
# Copy and configure .env
cp .env.example .env
nano .env  # Edit with your credentials

# Verify environment variables load
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Client ID:', os.getenv('REDDIT_CLIENT_ID')[:5] + '...' if os.getenv('REDDIT_CLIENT_ID') else 'Not set')"
```

### 2. Reddit Authentication Test

Create a test file `test_auth.py`:

```python
import os
from dotenv import load_dotenv
import praw

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    password=os.getenv('REDDIT_PASSWORD'),
    user_agent=os.getenv('REDDIT_USER_AGENT'),
    username=os.getenv('REDDIT_USERNAME'),
    check_for_async=False
)

print(f"Authenticated as: {reddit.user.me().name}")
print("✓ Reddit authentication successful!")
```

Run it:
```bash
python test_auth.py
```

### 3. Stock Price Fetch Test

```python
from yahoo_fin import stock_info as si

tickers = ['AAPL', 'TSLA', 'GME', 'MSFT']

for ticker in tickers:
    try:
        price = si.get_live_price(ticker)
        print(f"{ticker}: ${price:.2f}")
    except Exception as e:
        print(f"{ticker}: Error - {e}")
```

### 4. Bot Integration Test (Short Run)

Run the bot for a few minutes to verify it works:

```bash
# Run the bot
python main.py

# Let it run for 2-3 minutes
# Press Ctrl+C to stop

# Check the log file
cat reddit_bot.log
```

Expected log output:
```
2025-11-22 12:00:00 - INFO - Successfully authenticated as: your_username
2025-11-22 12:00:01 - INFO - Starting Reddit bot monitoring: wallstreetbets+stocks+personalfinance
2025-11-22 12:00:01 - INFO - Tracking top 5 stocks
2025-11-22 12:00:15 - INFO - New stock ticker found: $TSLA
...
```

## Testing Individual Features

### Feature 1: Ticker Extraction

```python
# Test the ticker extraction logic
test_comments = [
    "I love $AAPL stock!",
    "Buy $TSLA and $GME",
    "The price is $100.50",  # Should be ignored
    "$X is going up",
    "$TOOLONGNAME should be ignored"
]

# Run main.py and check if tickers are extracted correctly
```

### Feature 2: Ranking System

Monitor the rankings output as the bot runs:
```
Rankings: {'$TSLA': 5, '$AAPL': 3, '$GME': 2}
Top 5: ['$TSLA', '$AAPL', '$GME']
```

### Feature 3: Live Price Fetching

Verify prices are fetched and displayed:
```
Prices: {'$TSLA': 242.84, '$AAPL': 189.25, '$GME': 25.67}
```

### Feature 4: Multi-Subreddit Monitoring

Change SUBREDDITS in .env and verify bot monitors all:
```bash
SUBREDDITS=wallstreetbets+stocks
```

### Feature 5: Logging

Check both outputs work:
```bash
# Console output (real-time)
python main.py

# File output
tail -f reddit_bot.log
```

## Common Test Scenarios

### Scenario 1: Invalid Credentials
```bash
# Set wrong credentials in .env
REDDIT_CLIENT_ID=wrong_id

# Run bot
python main.py

# Expected: Error message about authentication failure
```

### Scenario 2: Network Failure
```bash
# Disconnect internet
# Run bot

# Expected: Graceful error handling
```

### Scenario 3: Invalid Ticker
The bot should skip invalid tickers:
- `$123` (starts with number)
- `$TOOLONGNAME` (more than 6 characters)

### Scenario 4: High Volume
Monitor performance during high activity:
```bash
# Use very active subreddit
SUBREDDITS=wallstreetbets

# Monitor CPU and memory usage
top
```

## Performance Testing

### Memory Usage
```bash
# Run bot
python main.py &

# Monitor memory
ps aux | grep python
```

### Response Time
Check how quickly new comments are processed:
```bash
# Look for time between comment and processing in logs
grep "New stock ticker" reddit_bot.log
```

## Troubleshooting Tests

If tests fail, run diagnostics:

```bash
# 1. Check Python version
python --version

# 2. Check installed packages
pip list | grep -E "(praw|yahoo|dotenv)"

# 3. Verify file permissions
ls -l main.py test_bot.py

# 4. Check .env file
cat .env  # (Be careful not to share output!)

# 5. Test Reddit API directly
python -c "import praw; print(praw.__version__)"

# 6. Test Yahoo Finance API
python -c "from yahoo_fin import stock_info as si; print(si.get_live_price('AAPL'))"
```

## CI/CD Testing (Optional)

Create `.github/workflows/test.yml` for automated testing:

```yaml
name: Test Bot

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python test_bot.py
```

## Test Checklist

Before deploying, verify:

- [ ] All dependencies install correctly
- [ ] `test_bot.py` passes all tests
- [ ] Reddit authentication works
- [ ] Stock prices can be fetched
- [ ] Ticker extraction works correctly
- [ ] Rankings update properly
- [ ] Logs are created and written to
- [ ] Environment variables load correctly
- [ ] Bot can be stopped gracefully (Ctrl+C)
- [ ] Error handling works for invalid tickers
- [ ] Multiple subreddits can be monitored
- [ ] .gitignore prevents .env from being committed

## Production Testing

Before running in production:

1. **Test with low-volume subreddit first**
2. **Monitor for 24 hours**
3. **Check log file size growth**
4. **Verify no memory leaks**
5. **Test error recovery**
6. **Verify all features work as expected**

## Automated Testing Schedule

Recommended testing frequency:
- **Before each deployment**: Full test suite
- **Weekly**: Integration tests
- **Monthly**: Performance tests
- **After dependency updates**: Full test suite

## Success Criteria

The bot is ready for use when:
- ✅ All automated tests pass
- ✅ Authentication works
- ✅ Stock prices are fetched successfully
- ✅ Rankings update correctly
- ✅ Logs are written properly
- ✅ No memory leaks after 1 hour of running
- ✅ Graceful shutdown works
- ✅ Error handling catches all exceptions
