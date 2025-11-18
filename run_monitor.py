#!/usr/bin/env python3
"""
Automated Crypto Monitor
Run this script to update portfolio and check alerts
Can be scheduled via cron/Task Scheduler
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from src.monitoring.portfolio_tracker import CryptoPortfolioTracker
from src.monitoring.alert_system import CryptoAlertSystem
from src.data.news_fetcher import CryptoNewsFetcher
from src.llm.sentiment_analyzer import CryptoSentimentAnalyzer
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def main():
    print("=" * 60)
    print("CRYPTO PORTFOLIO MONITOR")
    print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Update portfolio
    print("\n[1/4] Updating portfolio...")
    try:
        tracker = CryptoPortfolioTracker()
        portfolio_df = tracker.update_portfolio()

        if not portfolio_df.empty:
            summary = tracker.get_portfolio_summary()
            print(f"✓ Portfolio updated")
            print(f"  Total Value: ${summary['total_value']:,.2f}")

            if summary.get('daily_change'):
                daily = summary['daily_change']
                print(f"  24h Change: {daily['pct_change']:+.2f}% (${daily['value_change']:+,.2f})")
        else:
            print("✗ No portfolio data available")
            return

    except Exception as e:
        print(f"✗ Error updating portfolio: {e}")
        return

    # Generate alerts
    print("\n[2/4] Checking for alerts...")
    try:
        alert_system = CryptoAlertSystem()
        thresholds = alert_system.get_default_thresholds()

        all_alerts = []

        # Price alerts
        price_alerts = alert_system.check_price_alerts(portfolio_df, thresholds)
        all_alerts.extend(price_alerts)

        # Portfolio alerts
        portfolio_alerts = alert_system.check_portfolio_alerts(summary, thresholds)
        all_alerts.extend(portfolio_alerts)

        if all_alerts:
            print(f"⚠ Found {len(all_alerts)} alert(s)")
            report = alert_system.format_alerts_report(all_alerts)
            print("\n" + report)
        else:
            print("✓ No alerts")

    except Exception as e:
        print(f"✗ Error generating alerts: {e}")

    # Fetch news
    print("\n[3/4] Fetching crypto news...")
    try:
        news_fetcher = CryptoNewsFetcher()
        news_summary = news_fetcher.get_news_summary(hours_back=24)

        for symbol, articles in news_summary.items():
            print(f"  {symbol}: {len(articles)} articles")

    except Exception as e:
        print(f"✗ Error fetching news: {e}")

    # Sentiment analysis
    print("\n[4/4] Analyzing sentiment...")
    if os.getenv('OPENAI_API_KEY'):
        try:
            analyzer = CryptoSentimentAnalyzer()

            for symbol, articles in news_summary.items():
                if articles:
                    print(f"\n  Analyzing {symbol}...")
                    analyzed = analyzer.analyze_news_batch(articles[:5], symbol, max_articles=5)
                    overall = analyzer.get_overall_sentiment(analyzed)

                    print(f"    Sentiment: {overall['sentiment_label']} ({overall['avg_score']:+.1f})")
                    print(f"    Bullish: {overall['bullish_count']}, "
                          f"Bearish: {overall['bearish_count']}, "
                          f"Neutral: {overall['neutral_count']}")

                    if overall['critical_count'] > 0:
                        print(f"    ⚠ {overall['critical_count']} critical news items")

        except Exception as e:
            print(f"✗ Error analyzing sentiment: {e}")
    else:
        print("  ⊘ Skipped (OPENAI_API_KEY not set)")

    print("\n" + "=" * 60)
    print("Monitor run complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
