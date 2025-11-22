import time
import os
import sys
import logging
import json
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv
import praw
import yfinance as yf
from heapq import nlargest
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

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

# Configuration
SUBREDDITS = os.getenv('SUBREDDITS', 'wallstreetbets+stocks+personalfinance')
TOP_STOCKS_COUNT = int(os.getenv('TOP_STOCKS_COUNT', '5'))
ENABLE_SENTIMENT = os.getenv('ENABLE_SENTIMENT', 'True').lower() == 'true'
MIN_COMMENT_SCORE = int(os.getenv('MIN_COMMENT_SCORE', '0'))
ENABLE_SCORE_WEIGHTING = os.getenv('ENABLE_SCORE_WEIGHTING', 'True').lower() == 'true'
MAX_MENTIONS_PER_AUTHOR = int(os.getenv('MAX_MENTIONS_PER_AUTHOR', '10'))
ENABLE_DATA_EXPORT = os.getenv('ENABLE_DATA_EXPORT', 'True').lower() == 'true'
EXPORT_INTERVAL_MINUTES = int(os.getenv('EXPORT_INTERVAL_MINUTES', '60'))
EXPORT_FORMAT = os.getenv('EXPORT_FORMAT', 'json')
STATS_UPDATE_INTERVAL = int(os.getenv('STATS_UPDATE_INTERVAL', '10'))
MIN_TICKER_LENGTH = int(os.getenv('MIN_TICKER_LENGTH', '1'))
MAX_TICKER_LENGTH = int(os.getenv('MAX_TICKER_LENGTH', '5'))

# Initialize Reddit client
try:
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        password=os.getenv('REDDIT_PASSWORD'),
        user_agent=os.getenv('REDDIT_USER_AGENT', 'reddit_stock_tracker_bot_v2'),
        username=os.getenv('REDDIT_USERNAME'),
        check_for_async=False
    )
    # Test the connection
    reddit.user.me()
    logger.info(f"Successfully authenticated as: {reddit.user.me().name}")
except Exception as e:
    logger.error(f"Failed to initialize Reddit client: {e}")
    sys.exit(1)

# Initialize sentiment analyzer if enabled
if ENABLE_SENTIMENT:
    try:
        sentiment_analyzer = SentimentIntensityAnalyzer()
        logger.info("Sentiment analysis enabled")
    except Exception as e:
        logger.error(f"Failed to initialize sentiment analyzer: {e}")
        ENABLE_SENTIMENT = False


class StockTracker:
    """Advanced stock mention tracker with sentiment analysis and statistics."""

    def __init__(self):
        self.all_stocks = []
        self.rankings = {}
        self.stock_prices = {}
        self.sentiment_scores = defaultdict(list)
        self.author_mentions = defaultdict(lambda: defaultdict(int))
        self.mention_timestamps = defaultdict(list)
        self.comment_count = 0
        self.last_export_time = datetime.now()
        self.session_start = datetime.now()

        # Characters to exclude from tickers
        self.excluded_chars = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, " ", ".", ";", ")", ",", "$",
                               "?", ">", "<", "\"", "!", "+", "-", "*", "/", "\\", "|",
                               ":", "(", "[", "]", "{", "}", "@", "#", "%", "^", "&", "="]

    def get_price(self, stock_ticker):
        """
        Fetch live stock price using yfinance.

        Args:
            stock_ticker (str): Stock ticker symbol

        Returns:
            float: Current stock price or None if error
        """
        try:
            ticker = yf.Ticker(stock_ticker)
            data = ticker.history(period='1d', interval='1m')

            if data.empty:
                logger.debug(f"No data available for {stock_ticker}")
                return None

            price = data['Close'].iloc[-1]
            return round(price, 2)
        except Exception as e:
            logger.debug(f"Error fetching price for {stock_ticker}: {e}")
            return None

    def validate_ticker(self, ticker_symbol):
        """
        Validate if a ticker symbol exists using yfinance.

        Args:
            ticker_symbol (str): Ticker to validate

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info

            # Check if ticker has basic info
            if info and 'symbol' in info:
                return True
            return False
        except:
            return False

    def analyze_sentiment(self, text):
        """
        Analyze sentiment of text using VADER.

        Args:
            text (str): Text to analyze

        Returns:
            dict: Sentiment scores (neg, neu, pos, compound)
        """
        if not ENABLE_SENTIMENT:
            return None

        try:
            scores = sentiment_analyzer.polarity_scores(text)
            return scores
        except Exception as e:
            logger.debug(f"Error analyzing sentiment: {e}")
            return None

    def extract_tickers(self, comment_body):
        """
        Extract all ticker symbols from comment text.

        Args:
            comment_body (str): Comment text

        Returns:
            list: List of extracted ticker symbols
        """
        tickers = []
        phrase = "$"

        index = 0
        while index < len(comment_body):
            if comment_body[index] == phrase:
                ticker = "$"
                x = 1

                # Skip if first character after $ is a number or excluded character
                try:
                    if index + x >= len(comment_body):
                        index += 1
                        continue

                    if comment_body[index + x] in str(self.excluded_chars):
                        index += 1
                        continue
                except IndexError:
                    index += 1
                    continue

                # Extract ticker symbol
                while True:
                    try:
                        if index + x >= len(comment_body):
                            break

                        if comment_body[index + x] not in self.excluded_chars:
                            ticker += comment_body[index + x]
                            x += 1
                        else:
                            break
                    except IndexError:
                        break

                ticker = ticker.upper()
                ticker_without_dollar = ticker[1:]  # Remove $

                # Validate ticker length
                if MIN_TICKER_LENGTH <= len(ticker_without_dollar) <= MAX_TICKER_LENGTH:
                    tickers.append(ticker)

                index += x
            else:
                index += 1

        return tickers

    def process_comment(self, comment):
        """
        Process a single Reddit comment.

        Args:
            comment: PRAW comment object
        """
        try:
            # Check minimum score threshold
            if comment.score < MIN_COMMENT_SCORE:
                return

            # Extract all tickers from comment
            tickers = self.extract_tickers(comment.body)

            if not tickers:
                return

            # Analyze sentiment
            sentiment = self.analyze_sentiment(comment.body) if ENABLE_SENTIMENT else None

            # Calculate weight based on comment score
            weight = max(1, comment.score) if ENABLE_SCORE_WEIGHTING else 1

            for ticker in tickers:
                ticker_without_dollar = ticker[1:]
                author_name = str(comment.author) if comment.author else "deleted"

                # Check author mention limit
                if MAX_MENTIONS_PER_AUTHOR > 0:
                    if self.author_mentions[author_name][ticker] >= MAX_MENTIONS_PER_AUTHOR:
                        logger.debug(f"Skipping {ticker} from {author_name} - max mentions reached")
                        continue

                # Update author mention count
                self.author_mentions[author_name][ticker] += 1

                # Add to all_stocks if new
                if ticker not in self.all_stocks:
                    self.all_stocks.append(ticker)
                    self.rankings[ticker] = weight
                    logger.info(f"New stock ticker found: {ticker} (score: {comment.score}, weight: {weight})")
                else:
                    self.rankings[ticker] += weight

                # Store sentiment
                if sentiment:
                    self.sentiment_scores[ticker].append({
                        'compound': sentiment['compound'],
                        'pos': sentiment['pos'],
                        'neg': sentiment['neg'],
                        'neu': sentiment['neu'],
                        'timestamp': datetime.now().isoformat()
                    })

                # Store mention timestamp
                self.mention_timestamps[ticker].append(datetime.now())

            self.comment_count += 1

            # Display stats periodically
            if self.comment_count % STATS_UPDATE_INTERVAL == 0:
                self.display_stats()

            # Export data periodically
            if ENABLE_DATA_EXPORT:
                time_since_export = datetime.now() - self.last_export_time
                if time_since_export.total_seconds() >= EXPORT_INTERVAL_MINUTES * 60:
                    self.export_data()
                    self.last_export_time = datetime.now()

        except Exception as e:
            logger.error(f"Error processing comment: {e}")

    def calculate_statistics(self):
        """Calculate advanced statistics for tracked stocks."""
        stats = {}

        for ticker in self.all_stocks:
            ticker_without_dollar = ticker[1:]

            # Get price if not already fetched
            if ticker not in self.stock_prices:
                price = self.get_price(ticker_without_dollar)
                if price is not None:
                    self.stock_prices[ticker] = price

            # Calculate average sentiment
            avg_sentiment = None
            if ENABLE_SENTIMENT and ticker in self.sentiment_scores:
                sentiments = self.sentiment_scores[ticker]
                if sentiments:
                    avg_sentiment = {
                        'compound': sum(s['compound'] for s in sentiments) / len(sentiments),
                        'pos': sum(s['pos'] for s in sentiments) / len(sentiments),
                        'neg': sum(s['neg'] for s in sentiments) / len(sentiments),
                        'neu': sum(s['neu'] for s in sentiments) / len(sentiments),
                    }

            # Calculate mention velocity (mentions per hour)
            velocity = 0
            if ticker in self.mention_timestamps:
                recent_mentions = [
                    ts for ts in self.mention_timestamps[ticker]
                    if datetime.now() - ts <= timedelta(hours=1)
                ]
                velocity = len(recent_mentions)

            stats[ticker] = {
                'mentions': self.rankings.get(ticker, 0),
                'price': self.stock_prices.get(ticker),
                'sentiment': avg_sentiment,
                'velocity': velocity,
                'unique_authors': len([
                    author for author, mentions in self.author_mentions.items()
                    if ticker in mentions
                ])
            }

        return stats

    def display_stats(self):
        """Display current tracking statistics."""
        if not self.all_stocks:
            return

        largest = nlargest(TOP_STOCKS_COUNT, self.rankings, key=self.rankings.get)
        stats = self.calculate_statistics()

        logger.info("\n" + "="*70)
        logger.info(f"STOCK TRACKER STATISTICS (Comments Processed: {self.comment_count})")
        logger.info(f"Session Duration: {datetime.now() - self.session_start}")
        logger.info("="*70)

        logger.info(f"\nTop {TOP_STOCKS_COUNT} Most Mentioned Stocks:")
        for i, ticker in enumerate(largest, 1):
            stock_stats = stats.get(ticker, {})
            mentions = stock_stats.get('mentions', 0)
            price = stock_stats.get('price', 'N/A')
            velocity = stock_stats.get('velocity', 0)
            unique_authors = stock_stats.get('unique_authors', 0)

            price_str = f"${price}" if price != 'N/A' else price

            logger.info(f"  {i}. {ticker}")
            logger.info(f"     Mentions: {mentions:.0f} | Price: {price_str} | Velocity: {velocity}/hr | Authors: {unique_authors}")

            if ENABLE_SENTIMENT and stock_stats.get('sentiment'):
                sent = stock_stats['sentiment']
                sentiment_label = "Bullish" if sent['compound'] > 0.05 else "Bearish" if sent['compound'] < -0.05 else "Neutral"
                logger.info(f"     Sentiment: {sentiment_label} (compound: {sent['compound']:.3f})")

        logger.info("\nAll Tracked Stocks: " + ", ".join(largest[:20]))
        logger.info("="*70 + "\n")

    def export_data(self):
        """Export tracking data to file."""
        try:
            stats = self.calculate_statistics()

            export_data = {
                'timestamp': datetime.now().isoformat(),
                'session_start': self.session_start.isoformat(),
                'comments_processed': self.comment_count,
                'total_stocks_tracked': len(self.all_stocks),
                'stocks': []
            }

            # Sort by mentions
            sorted_tickers = sorted(
                self.all_stocks,
                key=lambda t: self.rankings.get(t, 0),
                reverse=True
            )

            for ticker in sorted_tickers:
                stock_data = {
                    'ticker': ticker,
                    'mentions': self.rankings.get(ticker, 0),
                    'price': self.stock_prices.get(ticker),
                    'velocity': stats[ticker].get('velocity', 0),
                    'unique_authors': stats[ticker].get('unique_authors', 0)
                }

                if ENABLE_SENTIMENT and stats[ticker].get('sentiment'):
                    stock_data['sentiment'] = stats[ticker]['sentiment']

                export_data['stocks'].append(stock_data)

            # Export based on format
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')

            if EXPORT_FORMAT == 'json':
                filename = f'stock_data_{timestamp_str}.json'
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                logger.info(f"Data exported to {filename}")

            elif EXPORT_FORMAT == 'csv':
                filename = f'stock_data_{timestamp_str}.csv'
                df = pd.DataFrame(export_data['stocks'])
                df.to_csv(filename, index=False)
                logger.info(f"Data exported to {filename}")

        except Exception as e:
            logger.error(f"Error exporting data: {e}")


def main():
    """Main function to run the stock tracker bot."""
    tracker = StockTracker()

    logger.info(f"Starting Reddit Stock Tracker Bot v2.0")
    logger.info(f"Monitoring subreddits: {SUBREDDITS}")
    logger.info(f"Tracking top {TOP_STOCKS_COUNT} stocks")
    logger.info(f"Sentiment analysis: {'Enabled' if ENABLE_SENTIMENT else 'Disabled'}")
    logger.info(f"Score weighting: {'Enabled' if ENABLE_SCORE_WEIGHTING else 'Disabled'}")
    logger.info(f"Data export: {'Enabled' if ENABLE_DATA_EXPORT else 'Disabled'}")

    if MAX_MENTIONS_PER_AUTHOR > 0:
        logger.info(f"Spam prevention: Max {MAX_MENTIONS_PER_AUTHOR} mentions per author")

    logger.info("Starting comment stream...\n")

    try:
        for comment in reddit.subreddit(SUBREDDITS).stream.comments(skip_existing=True):
            tracker.process_comment(comment)

    except KeyboardInterrupt:
        logger.info("\nBot stopped by user")
        logger.info("Generating final report...")
        tracker.display_stats()

        if ENABLE_DATA_EXPORT:
            logger.info("Exporting final data...")
            tracker.export_data()

    except Exception as e:
        logger.error(f"Fatal error in main loop: {e}")
        raise


if __name__ == "__main__":
    main()
