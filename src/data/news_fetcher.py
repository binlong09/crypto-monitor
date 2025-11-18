"""
Crypto News Fetcher
Fetch news from multiple sources for Bitcoin and Ethereum
"""

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time


class CryptoNewsFetcher:
    """Fetch cryptocurrency news from multiple sources"""

    # RSS feeds for crypto news
    RSS_FEEDS = {
        'cointelegraph': 'https://cointelegraph.com/rss',
        'coindesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
        'decrypt': 'https://decrypt.co/feed',
        'theblock': 'https://www.theblockcrypto.com/rss.xml'
    }

    CRYPTO_KEYWORDS = {
        'BTC': ['bitcoin', 'btc'],
        'ETH': ['ethereum', 'eth', 'ether'],
        'SOL': ['solana', 'sol'],
        'ADA': ['cardano', 'ada'],
        'XRP': ['ripple', 'xrp'],
        'DOT': ['polkadot', 'dot'],
        'DOGE': ['dogecoin', 'doge'],
        'MATIC': ['polygon', 'matic'],
        'AVAX': ['avalanche', 'avax'],
        'LINK': ['chainlink', 'link'],
        'UNI': ['uniswap', 'uni'],
        'ATOM': ['cosmos', 'atom'],
        'LTC': ['litecoin', 'ltc'],
        'ALGO': ['algorand', 'algo'],
        'APT': ['aptos', 'apt'],
        'ARB': ['arbitrum', 'arb'],
        'OP': ['optimism', 'op'],
        'SHIB': ['shiba', 'shib'],
        'PEPE': ['pepe'],
    }

    def __init__(self):
        self.session = requests.Session()

    def _generate_keywords(self, symbol: str) -> List[str]:
        """
        Generate search keywords for a cryptocurrency symbol

        Args:
            symbol: Crypto symbol (e.g., 'BTC', 'ETHEREUM')

        Returns:
            List of keywords to search for
        """
        # Check if we have predefined keywords
        symbol_upper = symbol.upper()
        if symbol_upper in self.CRYPTO_KEYWORDS:
            return self.CRYPTO_KEYWORDS[symbol_upper]

        # Generate keywords dynamically
        # Symbol itself and lowercase version
        keywords = [symbol.lower()]

        # If symbol is all caps and short, it's likely a ticker
        if symbol.isupper() and len(symbol) <= 5:
            keywords.append(symbol.lower())
        else:
            # It's likely a name (like 'bitcoin', 'ethereum')
            # Add it as-is
            keywords = [symbol.lower()]

        return keywords

    def fetch_rss_feed(self, feed_url: str, max_articles: int = 20) -> List[Dict]:
        """Fetch articles from RSS feed"""
        try:
            feed = feedparser.parse(feed_url)
            articles = []

            for entry in feed.entries[:max_articles]:
                # Parse publication date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])

                articles.append({
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', ''),
                    'published': pub_date,
                    'source': feed.feed.get('title', 'Unknown')
                })

            return articles

        except Exception as e:
            print(f"Error fetching RSS feed {feed_url}: {e}")
            return []

    def fetch_all_news(self, hours_back: int = 24) -> List[Dict]:
        """
        Fetch news from all sources

        Args:
            hours_back: Only return news from the last N hours

        Returns:
            List of news articles
        """
        all_articles = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        print(f"\n📰 Fetching crypto news from last {hours_back} hours...")
        print(f"   Cutoff time: {cutoff_time.strftime('%Y-%m-%d %H:%M')}")

        for source_name, feed_url in self.RSS_FEEDS.items():
            print(f"   → Fetching from {source_name}...", end=" ")
            articles = self.fetch_rss_feed(feed_url)

            if articles:
                print(f"✓ Got {len(articles)} articles")

                # Filter by time
                articles_in_timeframe = 0
                for article in articles:
                    if article['published'] and article['published'] >= cutoff_time:
                        article['source_name'] = source_name
                        all_articles.append(article)
                        articles_in_timeframe += 1

                print(f"      {articles_in_timeframe} within {hours_back}h timeframe")
            else:
                print(f"✗ No articles fetched")

            time.sleep(1)  # Be nice to servers

        # Sort by date (most recent first)
        all_articles.sort(key=lambda x: x['published'] if x['published'] else datetime.min, reverse=True)

        print(f"\n   Total articles fetched: {len(all_articles)}")
        return all_articles

    def filter_news_by_crypto(self, articles: List[Dict], symbol: str) -> List[Dict]:
        """
        Filter articles relevant to a specific cryptocurrency

        Args:
            articles: List of news articles
            symbol: Crypto symbol (e.g., 'BTC', 'ETH') or name (e.g., 'bitcoin', 'ethereum')

        Returns:
            Filtered list of relevant articles
        """
        # Generate keywords for this crypto (works for any symbol)
        keywords = self._generate_keywords(symbol)

        print(f"\n🔍 Filtering {len(articles)} articles for '{symbol}'...")
        print(f"   Using keywords: {keywords}")

        if not keywords:
            print(f"   ✗ No keywords generated!")
            return []

        relevant_articles = []

        for article in articles:
            text = f"{article['title']} {article['summary']}".lower()

            # Check if any keyword is in the article
            if any(keyword in text for keyword in keywords):
                article['matched_keywords'] = [kw for kw in keywords if kw in text]
                relevant_articles.append(article)

        print(f"   ✓ Found {len(relevant_articles)} relevant articles")

        return relevant_articles

    def get_crypto_news(self, symbol: str, hours_back: int = 24) -> List[Dict]:
        """
        Get news for a specific cryptocurrency

        Args:
            symbol: Crypto symbol (e.g., 'BTC', 'ETH')
            hours_back: Hours of history to fetch

        Returns:
            List of relevant news articles
        """
        all_articles = self.fetch_all_news(hours_back)
        return self.filter_news_by_crypto(all_articles, symbol)

    def get_news_summary(self, hours_back: int = 24) -> Dict[str, List[Dict]]:
        """
        Get news summary for all tracked cryptocurrencies

        Returns:
            Dict mapping symbol to list of articles
        """
        all_articles = self.fetch_all_news(hours_back)

        summary = {}
        for symbol in self.CRYPTO_KEYWORDS.keys():
            summary[symbol] = self.filter_news_by_crypto(all_articles, symbol)

        return summary

    def fetch_crypto_panic_news(self, crypto: str = 'BTC', filter_type: str = 'hot') -> List[Dict]:
        """
        Fetch news from CryptoPanic API (requires API key for full access)

        Args:
            crypto: Cryptocurrency code (BTC, ETH)
            filter_type: 'hot', 'rising', 'bullish', 'bearish'

        Note: Free tier is limited. Consider implementing your own API key.
        """
        try:
            # Public endpoint (limited)
            url = f"https://cryptopanic.com/api/v1/posts/?auth_token=free&currencies={crypto}&filter={filter_type}"

            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            articles = []
            for post in data.get('results', []):
                articles.append({
                    'title': post.get('title', ''),
                    'link': post.get('url', ''),
                    'published': datetime.fromisoformat(post.get('created_at', '').replace('Z', '+00:00')),
                    'source': post.get('source', {}).get('title', 'CryptoPanic'),
                    'votes': post.get('votes', {}).get('positive', 0) - post.get('votes', {}).get('negative', 0)
                })

            return articles

        except Exception as e:
            print(f"Error fetching CryptoPanic news: {e}")
            return []
