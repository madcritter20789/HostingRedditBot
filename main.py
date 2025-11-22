import time
import os
import sys
import logging
from dotenv import load_dotenv
import praw
import random
from heapq import nlargest
from yahoo_fin import stock_info as si

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('reddit_bot.log')
    ]
)
logger = logging.getLogger(__name__)

# Validate required environment variables
required_env_vars = [
    'REDDIT_CLIENT_ID',
    'REDDIT_CLIENT_SECRET',
    'REDDIT_USERNAME',
    'REDDIT_PASSWORD'
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    logger.error("Please create a .env file based on .env.example")
    sys.exit(1)

# Initialize Reddit client
try:
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        password=os.getenv('REDDIT_PASSWORD'),
        user_agent=os.getenv('REDDIT_USER_AGENT', 'reddit_stock_tracker_bot'),
        username=os.getenv('REDDIT_USERNAME'),
        check_for_async=False
    )
    # Test the connection
    reddit.user.me()
    logger.info(f"Successfully authenticated as: {reddit.user.me().name}")
except Exception as e:
    logger.error(f"Failed to initialize Reddit client: {e}")
    sys.exit(1)

def get_price(stock_ticker):
    """
    Fetch live stock price for a given ticker.

    Args:
        stock_ticker (str): Stock ticker symbol

    Returns:
        float: Current stock price or None if error
    """
    try:
        price = si.get_live_price(stock_ticker)
        return round(price, 2)
    except Exception as e:
        logger.debug(f"Error fetching price for {stock_ticker}: {e}")
        return None

# Configuration
SUBREDDITS = os.getenv('SUBREDDITS', 'wallstreetbets+stocks+personalfinance')
TOP_STOCKS_COUNT = int(os.getenv('TOP_STOCKS_COUNT', '5'))

# Data structures
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, " ", ".", ";", ")", ",", "$", "?", ">", "<", "\"", "!", "+", "-", "*"]
phrase = "$"
all_stocks = []
rankings = {}
stock_prices = {}

logger.info(f"Starting Reddit bot monitoring: {SUBREDDITS}")
logger.info(f"Tracking top {TOP_STOCKS_COUNT} stocks")

# Main monitoring loop
try:
    for comment in reddit.subreddit(SUBREDDITS).stream.comments(skip_existing=True):
        try:
            if phrase in comment.body:
                index = comment.body.index(phrase)
                ticker = ""
                ticker += comment.body[index]
                x = 1

                # Skip if first character after $ is a number
                try:
                    if comment.body[index + x] in str(numbers):
                        continue
                except IndexError:
                    continue

                # Extract ticker symbol
                while True:
                    try:
                        if comment.body[index + x] not in numbers:
                            ticker += comment.body[index + x]
                            x += 1
                        else:
                            break
                    except IndexError:
                        break

                ticker = ticker.upper()

                # Skip if ticker is too long (max 6 chars including $)
                if len(ticker) > 6:
                    continue

                # Update rankings
                if ticker not in all_stocks:
                    all_stocks.append(ticker)
                    rankings[ticker] = 1
                    logger.info(f"New stock ticker found: {ticker}")
                elif ticker in all_stocks:
                    rankings[ticker] += 1

                # Get top stocks
                largest = nlargest(TOP_STOCKS_COUNT, rankings, key=rankings.get)

                # Fetch prices for top stocks (FIXED: was range(len(largest)-1))
                for i in range(len(largest)):
                    ticker_symbol = largest[i]
                    no_dollar = ticker_symbol[1:]  # Remove $ sign

                    # Only fetch price if we don't have it yet or it's been a while
                    if ticker_symbol not in stock_prices:
                        price = get_price(no_dollar)
                        if price is not None:
                            stock_prices[ticker_symbol] = price
                            logger.info(f"Fetched price for {ticker_symbol}: ${price}")

                # Display current rankings
                logger.info("\n" + "="*50)
                logger.info("CURRENT RANKINGS:")
                logger.info(f"Rankings: {rankings}")
                logger.info(f"Top {TOP_STOCKS_COUNT}: {largest}")
                logger.info(f"Prices: {stock_prices}")
                logger.info("="*50 + "\n")

        except Exception as e:
            logger.error(f"Error processing comment: {e}")
            continue

except KeyboardInterrupt:
    logger.info("Bot stopped by user")
except Exception as e:
    logger.error(f"Fatal error in main loop: {e}")
    raise
