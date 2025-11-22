# Reddit Stock Tracker Bot v2.0 - Features

This document details all the features and improvements added in version 2.0 based on research of best practices and successful Reddit stock tracking bots.

## 🎯 Core Features

### 1. Real-Time Stock Mention Tracking
- Monitors multiple subreddits simultaneously
- Extracts stock tickers from Reddit comments ($SYMBOL format)
- Tracks frequency of mentions
- Ranks stocks by popularity
- Configurable number of top stocks to track

### 2. Sentiment Analysis (NEW v2.0)
**Based on research**: Most successful WSB bots include sentiment analysis

- **VADER Sentiment Analysis** - Specifically designed for social media
- Analyzes each comment containing stock mentions
- Calculates sentiment scores:
  - **Compound**: Overall sentiment (-1 to +1)
  - **Positive**: Positive sentiment ratio
  - **Negative**: Negative sentiment ratio
  - **Neutral**: Neutral sentiment ratio
- Classifies stocks as:
  - **Bullish** (compound > 0.05)
  - **Bearish** (compound < -0.05)
  - **Neutral** (-0.05 to 0.05)
- Aggregates sentiment across all mentions
- Can be enabled/disabled via configuration

### 3. Comment Score Weighting (NEW v2.0)
**Based on research**: Successful bots weight mentions by upvotes

- Highly upvoted comments count more
- Prevents manipulation from low-quality spam
- Configurable minimum score threshold
- Can be enabled/disabled
- Formula: `weight = max(1, comment_score)`

### 4. Spam Prevention (NEW v2.0)
**Best practice**: Prevent manipulation from single users

- Tracks mentions per author
- Configurable maximum mentions per author
- Prevents pump-and-dump spam
- Respects user privacy (no data retention beyond session)
- Author tracking isolated per stock

### 5. Live Stock Prices
- **Upgraded to yfinance** (v2.0) - More reliable than yahoo_fin
- Fetches real-time stock prices
- Validates ticker symbols
- Caches prices to reduce API calls
- Graceful error handling for invalid tickers

### 6. Advanced Statistics (NEW v2.0)

#### Mention Velocity
- Tracks mentions per hour
- Identifies trending stocks
- Shows momentum and interest spikes

#### Unique Author Tracking
- Counts unique users mentioning each stock
- Differentiates between viral mentions and spam

#### Time-Based Analysis
- Timestamp tracking for all mentions
- Enables time-series analysis
- Identifies peak discussion times

### 7. Data Persistence and Export (NEW v2.0)
**Based on research**: Essential for historical analysis

#### JSON Export
```json
{
  "timestamp": "2025-11-22T12:00:00",
  "session_start": "2025-11-22T10:00:00",
  "comments_processed": 1500,
  "total_stocks_tracked": 45,
  "stocks": [
    {
      "ticker": "$TSLA",
      "mentions": 127,
      "price": 242.84,
      "velocity": 15,
      "unique_authors": 42,
      "sentiment": {
        "compound": 0.456,
        "pos": 0.312,
        "neg": 0.089,
        "neu": 0.599
      }
    }
  ]
}
```

#### CSV Export
- Flat file format for spreadsheet analysis
- Includes all metrics
- Timestamp-based filenames

#### Features:
- Automatic periodic exports (configurable interval)
- Manual export on graceful shutdown
- Both JSON and CSV formats supported
- Timestamped files prevent overwrites

### 8. Enhanced Ticker Extraction
- Improved character exclusion
- Multiple tickers per comment support
- Configurable ticker length validation
- Handles edge cases and malformed text

### 9. Comprehensive Logging
- Dual output: console + file
- Timestamped entries
- Multiple log levels (INFO, DEBUG, ERROR)
- Session statistics
- Performance metrics

### 10. Configurable Parameters
All major features can be customized via `.env` file:

```ini
# Core Settings
TOP_STOCKS_COUNT=5
SUBREDDITS=wallstreetbets+stocks+personalfinance

# Sentiment Analysis
ENABLE_SENTIMENT=True

# Score Weighting
ENABLE_SCORE_WEIGHTING=True
MIN_COMMENT_SCORE=0

# Spam Prevention
MAX_MENTIONS_PER_AUTHOR=10

# Data Export
ENABLE_DATA_EXPORT=True
EXPORT_INTERVAL_MINUTES=60
EXPORT_FORMAT=json

# Display
STATS_UPDATE_INTERVAL=10

# Ticker Validation
MIN_TICKER_LENGTH=1
MAX_TICKER_LENGTH=5
```

## 📊 Output Examples

### Console Display
```
======================================================================
STOCK TRACKER STATISTICS (Comments Processed: 150)
Session Duration: 2:15:30
======================================================================

Top 5 Most Mentioned Stocks:
  1. $TSLA
     Mentions: 127 | Price: $242.84 | Velocity: 15/hr | Authors: 42
     Sentiment: Bullish (compound: 0.456)

  2. $AAPL
     Mentions: 98 | Price: $189.25 | Velocity: 12/hr | Authors: 35
     Sentiment: Neutral (compound: 0.023)

  3. $GME
     Mentions: 76 | Price: $25.67 | Velocity: 8/hr | Authors: 28
     Sentiment: Bearish (compound: -0.156)

All Tracked Stocks: $TSLA, $AAPL, $GME, $NVDA, $AMD, ...
======================================================================
```

## 🆕 What's New in v2.0

### Replaced Technologies
- ❌ `yahoo_fin` → ✅ `yfinance` (more reliable, widely used)

### New Dependencies
- ✅ `vaderSentiment` - Sentiment analysis
- ✅ `pandas` - Data handling and CSV export
- ✅ `numpy` - Numerical operations

### New Capabilities
1. **Sentiment Analysis** - Understand market sentiment
2. **Score Weighting** - Quality over quantity
3. **Spam Prevention** - Prevent manipulation
4. **Data Export** - Historical tracking
5. **Velocity Tracking** - Identify trending stocks
6. **Author Tracking** - Unique user counts
7. **Enhanced Statistics** - Deeper insights
8. **Better Validation** - Improved ticker detection

## 🔧 Technical Improvements

### Object-Oriented Design
- Introduced `StockTracker` class
- Better code organization
- Easier to extend and maintain
- Encapsulated state management

### Performance Optimizations
- Price caching (fetch once per ticker)
- Efficient data structures (defaultdict)
- Optimized ticker extraction algorithm
- Skip existing comments on startup

### Error Handling
- Comprehensive try-catch blocks
- Graceful degradation
- Detailed error logging
- Safe shutdown mechanisms

### Best Practices Implementation
Based on research from:
- PRAW official documentation
- Successful WSB tracking projects (wsbtickerbot, Swaggystocks, Apewisdom)
- Reddit bot best practices guides
- Financial API recommendations

## 🎓 Features Inspired By Research

### From Swaggystocks
- Sentiment analysis integration
- Score weighting for quality
- Periodic data exports

### From ApeWisdom
- Multi-subreddit tracking
- Velocity metrics
- API-ready data export

### From wsbtickerbot
- Comment context analysis
- Author tracking
- 24-hour analysis windows

### From PRAW Best Practices
- Rate limiting respect
- Error isolation
- Graceful shutdown
- Privacy considerations

## 📈 Use Cases

### 1. Market Sentiment Analysis
Track what retail investors are discussing and how they feel about it.

### 2. Trend Identification
Identify stocks gaining momentum before they go viral.

### 3. Research and Analysis
Export data for academic or personal research projects.

### 4. Bot Development
Use as a foundation for more advanced trading bots (paper trading only).

### 5. Community Monitoring
Understand what your investment community is focused on.

## ⚙️ Configuration Strategies

### Conservative (Avoid Spam)
```ini
MIN_COMMENT_SCORE=5
ENABLE_SCORE_WEIGHTING=True
MAX_MENTIONS_PER_AUTHOR=5
```

### Aggressive (Catch Everything)
```ini
MIN_COMMENT_SCORE=0
ENABLE_SCORE_WEIGHTING=False
MAX_MENTIONS_PER_AUTHOR=0
```

### Research Mode (Maximum Data)
```ini
ENABLE_SENTIMENT=True
ENABLE_DATA_EXPORT=True
EXPORT_INTERVAL_MINUTES=30
EXPORT_FORMAT=json
STATS_UPDATE_INTERVAL=5
```

### Production Mode (Efficient)
```ini
ENABLE_SENTIMENT=True
EXPORT_INTERVAL_MINUTES=120
STATS_UPDATE_INTERVAL=20
MIN_COMMENT_SCORE=2
```

## 🔮 Future Enhancement Possibilities

Based on research, these features could be added:

1. **Database Integration** - PostgreSQL/MongoDB for long-term storage
2. **Web Dashboard** - Real-time visualization
3. **API Endpoint** - Expose data via REST API
4. **Alert System** - Notifications for specific conditions
5. **Multiple Timeframes** - Track 1hr, 24hr, 7day trends
6. **Portfolio Simulation** - Paper trading based on sentiment
7. **Correlation Analysis** - Compare mentions with price movements
8. **Discord/Slack Integration** - Push notifications
9. **Options Tracking** - Track options plays separately
10. **Crypto Support** - Extend to cryptocurrency

## 📚 References

Research sources that influenced v2.0:

- [PRAW Documentation](https://praw.readthedocs.io/)
- [VADER Sentiment Analysis](https://github.com/cjhutto/vaderSentiment)
- [yfinance Library](https://github.com/ranaroussi/yfinance)
- [Swaggystocks](https://swaggystocks.com/)
- [ApeWisdom](https://apewisdom.io/)
- Reddit bot best practices guides
- Financial data API comparisons
- WSB tracking bot repositories on GitHub

## 🎯 Version Comparison

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Basic Tracking | ✅ | ✅ |
| Price Fetching | ✅ | ✅ (yfinance) |
| Sentiment Analysis | ❌ | ✅ |
| Score Weighting | ❌ | ✅ |
| Spam Prevention | ❌ | ✅ |
| Data Export | ❌ | ✅ |
| Velocity Tracking | ❌ | ✅ |
| Author Tracking | ❌ | ✅ |
| Advanced Stats | ❌ | ✅ |
| OOP Design | ❌ | ✅ |
| Configurable | Basic | Extensive |

---

**v2.0 is production-ready with enterprise-grade features based on industry best practices and successful implementations.**
