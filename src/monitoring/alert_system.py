"""
Crypto Alert System
Monitor portfolio and generate alerts for critical events
"""

from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd


class CryptoAlertSystem:
    """Generate and manage crypto portfolio alerts"""

    def __init__(self):
        self.alerts = []

    def check_price_alerts(self, portfolio_df: pd.DataFrame, thresholds: Dict[str, Dict]) -> List[Dict]:
        """
        Check for price-based alerts

        Args:
            portfolio_df: Current portfolio DataFrame
            thresholds: Dict with alert thresholds per symbol
                       e.g., {'BTC': {'drop_pct': 10, 'spike_pct': 15}}

        Returns:
            List of alert dicts
        """
        alerts = []

        for _, row in portfolio_df.iterrows():
            symbol = row['symbol']
            change_24h = row.get('change_24h', 0)

            if symbol not in thresholds:
                continue

            threshold = thresholds[symbol]

            # Check for large price drops
            if 'drop_pct' in threshold and change_24h < -threshold['drop_pct']:
                alerts.append({
                    'type': 'PRICE_DROP',
                    'severity': 'HIGH',
                    'symbol': symbol,
                    'message': f"{symbol} dropped {abs(change_24h):.2f}% in 24h",
                    'current_price': row['current_price'],
                    'change_pct': change_24h,
                    'timestamp': datetime.now()
                })

            # Check for large price spikes
            if 'spike_pct' in threshold and change_24h > threshold['spike_pct']:
                alerts.append({
                    'type': 'PRICE_SPIKE',
                    'severity': 'MEDIUM',
                    'symbol': symbol,
                    'message': f"{symbol} spiked {change_24h:.2f}% in 24h",
                    'current_price': row['current_price'],
                    'change_pct': change_24h,
                    'timestamp': datetime.now()
                })

        return alerts

    def check_portfolio_alerts(self, portfolio_summary: Dict, thresholds: Dict) -> List[Dict]:
        """
        Check for portfolio-level alerts

        Args:
            portfolio_summary: Portfolio summary dict
            thresholds: Dict with alert thresholds
                       e.g., {'portfolio_drop_pct': 5, 'portfolio_spike_pct': 10}

        Returns:
            List of alert dicts
        """
        alerts = []

        daily_change = portfolio_summary.get('daily_change')
        if not daily_change:
            return alerts

        pct_change = daily_change['pct_change']

        # Portfolio-wide drop alert
        if 'portfolio_drop_pct' in thresholds and pct_change < -thresholds['portfolio_drop_pct']:
            alerts.append({
                'type': 'PORTFOLIO_DROP',
                'severity': 'HIGH',
                'message': f"Portfolio dropped {abs(pct_change):.2f}% in 24h",
                'value_change': daily_change['value_change'],
                'pct_change': pct_change,
                'current_value': portfolio_summary['total_value'],
                'timestamp': datetime.now()
            })

        # Portfolio-wide gain alert
        if 'portfolio_spike_pct' in thresholds and pct_change > thresholds['portfolio_spike_pct']:
            alerts.append({
                'type': 'PORTFOLIO_SPIKE',
                'severity': 'MEDIUM',
                'message': f"Portfolio gained {pct_change:.2f}% in 24h",
                'value_change': daily_change['value_change'],
                'pct_change': pct_change,
                'current_value': portfolio_summary['total_value'],
                'timestamp': datetime.now()
            })

        return alerts

    def check_sentiment_alerts(self, sentiment_data: Dict, symbol: str) -> List[Dict]:
        """
        Check for sentiment-based alerts

        Args:
            sentiment_data: Overall sentiment dict from analyzer
            symbol: Crypto symbol

        Returns:
            List of alert dicts
        """
        alerts = []

        avg_score = sentiment_data.get('avg_score', 0)
        critical_count = sentiment_data.get('critical_count', 0)

        # Very negative sentiment alert
        if avg_score <= -7:
            alerts.append({
                'type': 'NEGATIVE_SENTIMENT',
                'severity': 'HIGH',
                'symbol': symbol,
                'message': f"Very negative news sentiment for {symbol} (score: {avg_score:.1f})",
                'sentiment_score': avg_score,
                'sentiment_label': sentiment_data.get('sentiment_label', 'Unknown'),
                'num_articles': sentiment_data.get('num_articles', 0),
                'timestamp': datetime.now()
            })

        # Critical news alert
        if critical_count > 0:
            alerts.append({
                'type': 'CRITICAL_NEWS',
                'severity': 'HIGH',
                'symbol': symbol,
                'message': f"{critical_count} critical news item(s) detected for {symbol}",
                'critical_count': critical_count,
                'timestamp': datetime.now()
            })

        # Very positive sentiment (potential opportunity)
        if avg_score >= 7:
            alerts.append({
                'type': 'POSITIVE_SENTIMENT',
                'severity': 'LOW',
                'symbol': symbol,
                'message': f"Very positive news sentiment for {symbol} (score: {avg_score:.1f})",
                'sentiment_score': avg_score,
                'sentiment_label': sentiment_data.get('sentiment_label', 'Unknown'),
                'num_articles': sentiment_data.get('num_articles', 0),
                'timestamp': datetime.now()
            })

        return alerts

    def check_on_chain_alerts(self, on_chain_data: Dict, symbol: str) -> List[Dict]:
        """
        Check for on-chain metric alerts (placeholder for future implementation)

        Args:
            on_chain_data: On-chain metrics dict
            symbol: Crypto symbol

        Returns:
            List of alert dicts
        """
        alerts = []

        # Example: Could check for unusual GitHub activity, social media spikes, etc.
        # For now, just check if we have the data

        if on_chain_data.get('commit_count_4_weeks', 0) > 1000:
            alerts.append({
                'type': 'HIGH_DEVELOPMENT_ACTIVITY',
                'severity': 'LOW',
                'symbol': symbol,
                'message': f"High development activity for {symbol} ({on_chain_data['commit_count_4_weeks']} commits in 4 weeks)",
                'timestamp': datetime.now()
            })

        return alerts

    def format_alerts_report(self, alerts: List[Dict]) -> str:
        """
        Format alerts into a readable report

        Args:
            alerts: List of alert dicts

        Returns:
            Formatted alert report string
        """
        if not alerts:
            return "No alerts at this time."

        # Sort by severity
        severity_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        sorted_alerts = sorted(alerts, key=lambda x: severity_order.get(x['severity'], 3))

        report_lines = ["=== CRYPTO ALERTS ===\n"]

        high_alerts = [a for a in sorted_alerts if a['severity'] == 'HIGH']
        medium_alerts = [a for a in sorted_alerts if a['severity'] == 'MEDIUM']
        low_alerts = [a for a in sorted_alerts if a['severity'] == 'LOW']

        if high_alerts:
            report_lines.append(f"HIGH PRIORITY ({len(high_alerts)}):")
            for alert in high_alerts:
                report_lines.append(f"  - {alert['message']}")
            report_lines.append("")

        if medium_alerts:
            report_lines.append(f"MEDIUM PRIORITY ({len(medium_alerts)}):")
            for alert in medium_alerts:
                report_lines.append(f"  - {alert['message']}")
            report_lines.append("")

        if low_alerts:
            report_lines.append(f"INFO ({len(low_alerts)}):")
            for alert in low_alerts:
                report_lines.append(f"  - {alert['message']}")

        return '\n'.join(report_lines)

    def get_default_thresholds(self) -> Dict:
        """Get default alert thresholds"""
        return {
            'BTC': {
                'drop_pct': 10,  # Alert on 10%+ drop
                'spike_pct': 15   # Alert on 15%+ spike
            },
            'ETH': {
                'drop_pct': 12,  # ETH is more volatile
                'spike_pct': 18
            },
            'portfolio_drop_pct': 8,    # Alert on 8%+ portfolio drop
            'portfolio_spike_pct': 12   # Alert on 12%+ portfolio gain
        }
