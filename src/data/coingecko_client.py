"""
CoinGecko API client for fetching crypto data
Requires free API key from https://www.coingecko.com/en/api
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
import os


class CoinGeckoClient:
    """Client for fetching cryptocurrency data from CoinGecko API"""

    BASE_URL = "https://api.coingecko.com/api/v3"

    # Supported cryptocurrencies
    SUPPORTED_COINS = {
        'bitcoin': 'btc',
        'ethereum': 'eth'
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize CoinGecko client

        Args:
            api_key: CoinGecko API key (or set COINGECKO_API_KEY env variable)
        """
        self.api_key = api_key or os.getenv('COINGECKO_API_KEY')
        self.session = requests.Session()
        self.last_request_time = 0
        self.rate_limit_delay = 1.5  # CoinGecko free tier: ~50 calls/min

        # Set up authentication header if API key is provided
        if self.api_key:
            self.session.headers.update({
                'x-cg-demo-api-key': self.api_key  # For free tier API key
            })

    def _rate_limit(self):
        """Ensure we don't exceed API rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request with rate limiting and authentication"""
        self._rate_limit()
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print(f"❌ CoinGecko API Authentication Error!")
                print(f"   Your API key may be missing or invalid.")
                print(f"   Get a free API key from: https://www.coingecko.com/en/api")
                print(f"   Then set COINGECKO_API_KEY in your .env file")
            else:
                print(f"Error fetching data from CoinGecko: {e}")
            return {}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from CoinGecko: {e}")
            return {}

    def get_price(self, coin_id: str) -> Optional[Dict]:
        """
        Get current price and 24h change for a coin

        Args:
            coin_id: CoinGecko coin ID (e.g., 'bitcoin', 'ethereum')

        Returns:
            Dict with price, market_cap, volume, and 24h change
        """
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }

        data = self._make_request('simple/price', params)

        if not data or coin_id not in data:
            return None

        coin_data = data[coin_id]
        return {
            'price': coin_data.get('usd', 0),
            'market_cap': coin_data.get('usd_market_cap', 0),
            'volume_24h': coin_data.get('usd_24h_vol', 0),
            'change_24h': coin_data.get('usd_24h_change', 0),
            'last_updated': datetime.fromtimestamp(coin_data.get('last_updated_at', 0))
        }

    def get_market_data(self, coin_id: str) -> Optional[Dict]:
        """
        Get detailed market data for a coin

        Returns:
            Dict with comprehensive market data
        """
        data = self._make_request(f'coins/{coin_id}', {
            'localization': 'false',
            'tickers': 'false',
            'community_data': 'false',
            'developer_data': 'false'
        })

        if not data:
            return None

        market_data = data.get('market_data', {})

        return {
            'current_price': market_data.get('current_price', {}).get('usd', 0),
            'market_cap': market_data.get('market_cap', {}).get('usd', 0),
            'total_volume': market_data.get('total_volume', {}).get('usd', 0),
            'high_24h': market_data.get('high_24h', {}).get('usd', 0),
            'low_24h': market_data.get('low_24h', {}).get('usd', 0),
            'price_change_24h': market_data.get('price_change_24h', 0),
            'price_change_percentage_24h': market_data.get('price_change_percentage_24h', 0),
            'price_change_percentage_7d': market_data.get('price_change_percentage_7d', 0),
            'price_change_percentage_30d': market_data.get('price_change_percentage_30d', 0),
            'circulating_supply': market_data.get('circulating_supply', 0),
            'total_supply': market_data.get('total_supply', 0),
            'max_supply': market_data.get('max_supply'),
            'ath': market_data.get('ath', {}).get('usd', 0),
            'ath_date': market_data.get('ath_date', {}).get('usd'),
            'atl': market_data.get('atl', {}).get('usd', 0),
            'atl_date': market_data.get('atl_date', {}).get('usd'),
            'last_updated': market_data.get('last_updated')
        }

    def get_historical_prices(self, coin_id: str, days: int = 30) -> pd.DataFrame:
        """
        Get historical price data

        Args:
            coin_id: CoinGecko coin ID
            days: Number of days of historical data (max 365 for free tier)

        Returns:
            DataFrame with timestamp, price, market_cap, volume
        """
        # CoinGecko free tier doesn't support hourly data (requires API key)
        # So we use daily data for all periods
        # This means we need at least 30 days for good technical indicators
        params = {
            'vs_currency': 'usd',
            'days': days
        }

        data = self._make_request(f'coins/{coin_id}/market_chart', params)

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame({
            'timestamp': [datetime.fromtimestamp(p[0]/1000) for p in data.get('prices', [])],
            'price': [p[1] for p in data.get('prices', [])],
            'market_cap': [p[1] for p in data.get('market_caps', [])],
            'volume': [p[1] for p in data.get('total_volumes', [])]
        })

        return df

    def get_fear_greed_index(self) -> Optional[Dict]:
        """
        Get crypto Fear & Greed Index
        Note: This requires alternative.me API, not CoinGecko
        """
        try:
            response = requests.get('https://api.alternative.me/fng/', timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('data'):
                latest = data['data'][0]
                return {
                    'value': int(latest.get('value', 0)),
                    'classification': latest.get('value_classification', 'Unknown'),
                    'timestamp': datetime.fromtimestamp(int(latest.get('timestamp', 0)))
                }
        except Exception as e:
            print(f"Error fetching Fear & Greed Index: {e}")

        return None

    def get_on_chain_metrics(self, coin_id: str) -> Optional[Dict]:
        """
        Get on-chain metrics (limited on free tier)

        Returns basic on-chain data available from CoinGecko
        """
        data = self._make_request(f'coins/{coin_id}', {
            'localization': 'false',
            'tickers': 'false',
            'community_data': 'true',
            'developer_data': 'true'
        })

        if not data:
            return None

        community = data.get('community_data', {})
        developer = data.get('developer_data', {})

        return {
            'twitter_followers': community.get('twitter_followers', 0),
            'reddit_subscribers': community.get('reddit_subscribers', 0),
            'reddit_active_48h': community.get('reddit_accounts_active_48h', 0),
            'github_stars': developer.get('stars', 0),
            'github_forks': developer.get('forks', 0),
            'github_subscribers': developer.get('subscribers', 0),
            'total_issues': developer.get('total_issues', 0),
            'closed_issues': developer.get('closed_issues', 0),
            'pull_requests_merged': developer.get('pull_requests_merged', 0),
            'commit_count_4_weeks': developer.get('commit_count_4_weeks', 0)
        }

    def get_all_prices(self) -> Dict[str, Dict]:
        """Get current prices for all supported coins"""
        prices = {}
        for coin_id, symbol in self.SUPPORTED_COINS.items():
            price_data = self.get_price(coin_id)
            if price_data:
                prices[symbol.upper()] = price_data
        return prices
