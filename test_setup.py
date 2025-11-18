#!/usr/bin/env python3
"""
Test script to verify crypto monitor setup
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_setup():
    """Test basic setup requirements"""

    print("=" * 60)
    print("CRYPTO MONITOR SETUP TEST")
    print("=" * 60)

    # Test 1: Check OpenAI API Key
    print("\n[1/5] Checking OpenAI API Key...")
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"    ✓ API key found (length: {len(api_key)} chars)")
        print(f"    ✓ Key starts with: {api_key[:10]}...")
    else:
        print("    ✗ API key not found!")
        print("    → Create a .env file with OPENAI_API_KEY=your-key")
        return False

    # Test 2: Check imports
    print("\n[2/5] Testing module imports...")
    try:
        from src.data.coingecko_client import CoinGeckoClient
        from src.data.news_fetcher import CryptoNewsFetcher
        from src.monitoring.portfolio_tracker import CryptoPortfolioTracker
        from src.llm.sentiment_analyzer import CryptoSentimentAnalyzer
        print("    ✓ All modules imported successfully")
    except Exception as e:
        print(f"    ✗ Import error: {e}")
        return False

    # Test 3: Test CoinGecko API
    print("\n[3/5] Testing CoinGecko API...")
    try:
        client = CoinGeckoClient()
        btc_price = client.get_price('bitcoin')
        if btc_price and btc_price['price'] > 0:
            print(f"    ✓ CoinGecko API working")
            print(f"    ✓ Current BTC price: ${btc_price['price']:,.2f}")
        else:
            print("    ✗ Failed to get BTC price")
            return False
    except Exception as e:
        print(f"    ✗ CoinGecko error: {e}")
        return False

    # Test 4: Test OpenAI connection
    print("\n[4/5] Testing OpenAI API...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'test'"}],
            max_tokens=5
        )
        print("    ✓ OpenAI API working")
        print(f"    ✓ Model: {response.model}")
    except Exception as e:
        print(f"    ✗ OpenAI error: {e}")
        print("    → Check your API key is valid")
        return False

    # Test 5: Check directory structure
    print("\n[5/5] Checking directory structure...")
    required_dirs = ['src/data', 'src/monitoring', 'src/llm', 'data', 'logs']
    all_exist = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"    ✓ {dir_path}/ exists")
        else:
            print(f"    ✗ {dir_path}/ missing")
            all_exist = False

    if not all_exist:
        return False

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)
    print("\nYou're ready to run the dashboard:")
    print("  streamlit run dashboard.py")
    print()
    return True

if __name__ == "__main__":
    success = test_setup()
    sys.exit(0 if success else 1)
