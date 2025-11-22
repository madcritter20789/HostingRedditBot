#!/usr/bin/env python3
"""
Test script to validate bot functionality without running the full bot.
This script tests:
1. All required dependencies are installed
2. Stock price fetching works
3. Ticker extraction logic works
4. Environment variable loading
"""

import sys
import os

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    try:
        import praw
        print("✓ praw imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import praw: {e}")
        return False

    try:
        from yahoo_fin import stock_info as si
        print("✓ yahoo_fin imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import yahoo_fin: {e}")
        return False

    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import python-dotenv: {e}")
        return False

    try:
        from heapq import nlargest
        print("✓ heapq imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import heapq: {e}")
        return False

    return True


def test_stock_price_fetch():
    """Test fetching stock price."""
    print("\nTesting stock price fetching...")
    try:
        from yahoo_fin import stock_info as si

        # Test with a known ticker
        ticker = "AAPL"
        print(f"Fetching price for {ticker}...")
        price = si.get_live_price(ticker)
        print(f"✓ Successfully fetched price for {ticker}: ${price:.2f}")
        return True
    except Exception as e:
        print(f"✗ Failed to fetch stock price: {e}")
        return False


def test_ticker_extraction():
    """Test the ticker extraction logic."""
    print("\nTesting ticker extraction logic...")

    test_cases = [
        ("I bought $TSLA today", "$TSLA"),
        ("$AAPL is going up!", "$AAPL"),
        ("Check out $GME and $AMC", "$GME"),  # Should get first one
        ("Price is $100.50", None),  # Should skip (number after $)
        ("$TOOLONGticker", None),  # Should skip (too long)
    ]

    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, " ", ".", ";", ")", ",", "$", "?", ">", "<", "\"", "!", "+", "-", "*"]
    phrase = "$"

    all_passed = True

    for text, expected in test_cases:
        ticker = None

        if phrase in text:
            index = text.index(phrase)
            ticker = ""
            ticker += text[index]
            x = 1

            try:
                if text[index + x] in str(numbers):
                    ticker = None
                else:
                    while True:
                        try:
                            if text[index + x] not in numbers:
                                ticker += text[index + x]
                                x += 1
                            else:
                                break
                        except IndexError:
                            break

                    ticker = ticker.upper()

                    if len(ticker) > 6:
                        ticker = None
            except IndexError:
                ticker = None

        if ticker == expected:
            print(f"✓ '{text}' -> {ticker}")
        else:
            print(f"✗ '{text}' -> Expected: {expected}, Got: {ticker}")
            all_passed = False

    return all_passed


def test_env_file():
    """Test if .env.example exists."""
    print("\nTesting environment configuration...")

    if os.path.exists('.env.example'):
        print("✓ .env.example file exists")
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
        'README.md'
    ]

    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} not found")
            all_exist = False

    return all_exist


def main():
    """Run all tests."""
    print("="*60)
    print("Reddit Stock Tracker Bot - Test Suite")
    print("="*60)

    tests = [
        ("File Structure", test_file_structure),
        ("Package Imports", test_imports),
        ("Stock Price Fetching", test_stock_price_fetch),
        ("Ticker Extraction", test_ticker_extraction),
        ("Environment Configuration", test_env_file),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! The bot is ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
