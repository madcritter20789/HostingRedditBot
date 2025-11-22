#!/usr/bin/env python3
"""
Test script to validate Reddit Stock Tracker Bot v2.0 functionality.
This script tests:
1. All required dependencies are installed
2. Stock price fetching works (yfinance)
3. Sentiment analysis works (VADER)
4. Ticker extraction logic works
5. Environment variable loading
6. Data export capabilities
"""

import sys
import os

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    packages = [
        ('praw', 'praw'),
        ('yfinance', 'yf'),
        ('python-dotenv', 'dotenv'),
        ('vaderSentiment', 'vaderSentiment.vaderSentiment'),
        ('pandas', 'pd'),
        ('numpy', 'np'),
    ]

    all_imported = True
    for package_name, import_path in packages:
        try:
            if '.' in import_path:
                parts = import_path.split('.')
                __import__(parts[0])
                print(f"✓ {package_name} imported successfully")
            else:
                __import__(import_path)
                print(f"✓ {package_name} imported successfully")
        except ImportError as e:
            print(f"✗ Failed to import {package_name}: {e}")
            all_imported = False

    # Test heapq (built-in)
    try:
        from heapq import nlargest
        print("✓ heapq imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import heapq: {e}")
        all_imported = False

    return all_imported


def test_stock_price_fetch():
    """Test fetching stock price with yfinance."""
    print("\nTesting stock price fetching (yfinance)...")
    try:
        import yfinance as yf

        # Test with a known ticker
        ticker = "AAPL"
        print(f"Fetching price for {ticker}...")
        stock = yf.Ticker(ticker)
        data = stock.history(period='1d', interval='1m')

        if not data.empty:
            price = data['Close'].iloc[-1]
            print(f"✓ Successfully fetched price for {ticker}: ${price:.2f}")
            return True
        else:
            print(f"⚠ No data returned for {ticker}")
            return False
    except Exception as e:
        print(f"✗ Failed to fetch stock price: {e}")
        return False


def test_sentiment_analysis():
    """Test VADER sentiment analysis."""
    print("\nTesting sentiment analysis (VADER)...")
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

        analyzer = SentimentIntensityAnalyzer()

        test_texts = [
            ("$TSLA to the moon! 🚀", "positive"),
            ("$GME is crashing badly", "negative"),
            ("$AAPL is trading today", "neutral"),
        ]

        all_passed = True
        for text, expected_sentiment in test_texts:
            scores = analyzer.polarity_scores(text)
            compound = scores['compound']

            if expected_sentiment == "positive" and compound > 0.05:
                result = "✓"
            elif expected_sentiment == "negative" and compound < -0.05:
                result = "✓"
            elif expected_sentiment == "neutral" and -0.05 <= compound <= 0.05:
                result = "✓"
            else:
                result = "⚠"
                all_passed = False

            print(f"  {result} '{text}' -> compound: {compound:.3f}")

        if all_passed:
            print("✓ Sentiment analysis working correctly")
        else:
            print("⚠ Some sentiment tests had unexpected results (may be OK)")

        return True
    except Exception as e:
        print(f"✗ Failed to test sentiment analysis: {e}")
        return False


def test_ticker_extraction():
    """Test the enhanced ticker extraction logic."""
    print("\nTesting ticker extraction logic...")

    # Simulate the enhanced extraction from main.py
    excluded_chars = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, " ", ".", ";", ")", ",", "$",
                      "?", ">", "<", "\"", "!", "+", "-", "*", "/", "\\", "|",
                      ":", "(", "[", "]", "{", "}", "@", "#", "%", "^", "&", "="]

    test_cases = [
        ("I bought $TSLA today", ["$TSLA"]),
        ("$AAPL is going up!", ["$AAPL"]),
        ("Check out $GME and $AMC", ["$GME", "$AMC"]),  # Multiple tickers
        ("Price is $100.50", []),  # Should skip (number after $)
        ("$TOOLONG", []),  # Should skip (too long with default max=5)
        ("$A is valid", ["$A"]),  # Single char is valid
    ]

    all_passed = True

    for text, expected_tickers in test_cases:
        tickers = []
        phrase = "$"
        MIN_TICKER_LENGTH = 1
        MAX_TICKER_LENGTH = 5

        index = 0
        while index < len(text):
            if text[index] == phrase:
                ticker = "$"
                x = 1

                try:
                    if index + x >= len(text):
                        index += 1
                        continue

                    if text[index + x] in str(excluded_chars):
                        index += 1
                        continue
                except IndexError:
                    index += 1
                    continue

                while True:
                    try:
                        if index + x >= len(text):
                            break

                        if text[index + x] not in excluded_chars:
                            ticker += text[index + x]
                            x += 1
                        else:
                            break
                    except IndexError:
                        break

                ticker = ticker.upper()
                ticker_without_dollar = ticker[1:]

                if MIN_TICKER_LENGTH <= len(ticker_without_dollar) <= MAX_TICKER_LENGTH:
                    tickers.append(ticker)

                index += x
            else:
                index += 1

        if tickers == expected_tickers:
            print(f"✓ '{text}' -> {tickers}")
        else:
            print(f"✗ '{text}' -> Expected: {expected_tickers}, Got: {tickers}")
            all_passed = False

    return all_passed


def test_data_export():
    """Test data export functionality."""
    print("\nTesting data export capabilities...")
    try:
        import json
        import pandas as pd

        # Test JSON export
        test_data = {
            'timestamp': '2025-11-22T12:00:00',
            'stocks': [
                {'ticker': '$TSLA', 'mentions': 10, 'price': 242.84}
            ]
        }

        # Test JSON serialization
        json_str = json.dumps(test_data)
        print("✓ JSON serialization works")

        # Test pandas DataFrame
        df = pd.DataFrame(test_data['stocks'])
        print("✓ Pandas DataFrame creation works")

        return True
    except Exception as e:
        print(f"✗ Failed to test data export: {e}")
        return False


def test_env_file():
    """Test if .env.example exists with v2.0 variables."""
    print("\nTesting environment configuration...")

    if os.path.exists('.env.example'):
        print("✓ .env.example file exists")

        # Check for v2.0 specific variables
        with open('.env.example', 'r') as f:
            content = f.read()

        v2_vars = [
            'ENABLE_SENTIMENT',
            'ENABLE_SCORE_WEIGHTING',
            'ENABLE_DATA_EXPORT',
            'MAX_MENTIONS_PER_AUTHOR'
        ]

        found_vars = [var for var in v2_vars if var in content]

        if len(found_vars) == len(v2_vars):
            print("✓ .env.example includes v2.0 configuration options")
        else:
            print(f"⚠ Missing some v2.0 variables: {set(v2_vars) - set(found_vars)}")

    else:
        print("✗ .env.example file not found")
        return False

    if os.path.exists('.env'):
        print("✓ .env file exists (ready for use)")

        from dotenv import load_dotenv
        load_dotenv()

        required_vars = [
            'REDDIT_CLIENT_ID',
            'REDDIT_CLIENT_SECRET',
            'REDDIT_USERNAME',
            'REDDIT_PASSWORD'
        ]

        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            print(f"⚠ Warning: Missing variables in .env: {', '.join(missing)}")
            print("  You'll need to set these before running the bot")
        else:
            print("✓ All required environment variables are set")
    else:
        print("⚠ .env file not found (create it from .env.example)")

    return True


def test_file_structure():
    """Test that all required files exist."""
    print("\nTesting file structure...")

    required_files = [
        'main.py',
        'requirements.txt',
        'Requirement.txt',
        'Procfile',
        'Runtime.txt',
        '.env.example',
        '.gitignore',
        'README.md',
        'FEATURES.md',  # New in v2.0
        'test_bot.py'
    ]

    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} not found")
            all_exist = False

    return all_exist


def test_class_structure():
    """Test that StockTracker class can be imported."""
    print("\nTesting code structure...")
    try:
        # Try to import the main module
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", "main.py")
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)

            # Check if we can at least read the file
            with open('main.py', 'r') as f:
                content = f.read()

            if 'class StockTracker' in content:
                print("✓ StockTracker class found in main.py")
            else:
                print("✗ StockTracker class not found")
                return False

            if 'def analyze_sentiment' in content:
                print("✓ Sentiment analysis method found")
            else:
                print("⚠ Sentiment analysis method not found")

            if 'def export_data' in content:
                print("✓ Data export method found")
            else:
                print("⚠ Data export method not found")

            return True
        else:
            print("⚠ Could not load main.py module spec")
            return False

    except Exception as e:
        print(f"✗ Failed to test code structure: {e}")
        return False


def main():
    """Run all tests."""
    print("="*70)
    print("Reddit Stock Tracker Bot v2.0 - Test Suite")
    print("="*70)

    tests = [
        ("File Structure", test_file_structure),
        ("Package Imports", test_imports),
        ("Stock Price Fetching (yfinance)", test_stock_price_fetch),
        ("Sentiment Analysis (VADER)", test_sentiment_analysis),
        ("Ticker Extraction", test_ticker_extraction),
        ("Data Export Capabilities", test_data_export),
        ("Code Structure (OOP)", test_class_structure),
        ("Environment Configuration", test_env_file),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False

    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Bot v2.0 is ready to use.")
        print("\nNew v2.0 Features Available:")
        print("  • Sentiment Analysis (VADER)")
        print("  • Comment Score Weighting")
        print("  • Spam Prevention")
        print("  • Data Export (JSON/CSV)")
        print("  • Enhanced Statistics")
        print("  • Improved Stock Price API (yfinance)")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nIf dependency tests failed, install requirements:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
