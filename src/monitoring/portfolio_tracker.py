"""
Crypto Portfolio Tracker
Track holdings, calculate values, and monitor performance
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.coingecko_client import CoinGeckoClient


class CryptoPortfolioTracker:
    """Track and monitor cryptocurrency portfolio"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.snapshots_file = self.data_dir / "portfolio_snapshots.json"
        self.holdings_file = self.data_dir / "current_holdings.csv"

        self.client = CoinGeckoClient()
        self.snapshots = self._load_snapshots()

    def _load_snapshots(self) -> List[Dict]:
        """Load historical portfolio snapshots"""
        if self.snapshots_file.exists():
            with open(self.snapshots_file, 'r') as f:
                return json.load(f)
        return []

    def _save_snapshots(self):
        """Save portfolio snapshots to file"""
        with open(self.snapshots_file, 'w') as f:
            json.dump(self.snapshots, f, indent=2, default=str)

    def parse_holdings_csv(self, csv_path: str) -> pd.DataFrame:
        """
        Parse crypto holdings from CSV

        Expected format:
        symbol,amount,cost_basis,purchase_date
        BTC,0.5,25000,2024-01-15
        ETH,5.0,2000,2024-02-01
        """
        try:
            df = pd.read_csv(csv_path)

            # Validate required columns
            required_cols = ['symbol', 'amount']
            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"Missing required column: {col}")

            # Standardize symbols
            df['symbol'] = df['symbol'].str.upper()

            # Add cost_basis and purchase_date if missing
            if 'cost_basis' not in df.columns:
                df['cost_basis'] = 0.0
            if 'purchase_date' not in df.columns:
                df['purchase_date'] = datetime.now().strftime('%Y-%m-%d')

            return df

        except Exception as e:
            print(f"Error parsing CSV: {e}")
            return pd.DataFrame()

    def update_portfolio(self, csv_path: Optional[str] = None) -> pd.DataFrame:
        """
        Update portfolio with current prices

        Args:
            csv_path: Path to holdings CSV. If None, uses last saved holdings.

        Returns:
            DataFrame with updated portfolio values
        """
        # Load holdings
        if csv_path:
            holdings_df = self.parse_holdings_csv(csv_path)
            # Save as current holdings
            holdings_df.to_csv(self.holdings_file, index=False)
        elif self.holdings_file.exists():
            holdings_df = pd.read_csv(self.holdings_file)
        else:
            print("No holdings data available")
            return pd.DataFrame()

        # Get current prices
        prices = self.client.get_all_prices()

        # Calculate portfolio values
        portfolio_data = []
        total_value = 0
        total_cost_basis = 0

        for _, row in holdings_df.iterrows():
            symbol = row['symbol']
            amount = float(row['amount'])
            cost_basis = float(row.get('cost_basis', 0))

            # Get price data
            if symbol in prices:
                price_data = prices[symbol]
                current_price = price_data['price']
                change_24h = price_data['change_24h']
            else:
                print(f"Warning: Price not available for {symbol}")
                current_price = 0
                change_24h = 0

            # Calculate values
            current_value = amount * current_price
            position_cost = amount * cost_basis if cost_basis > 0 else 0
            profit_loss = current_value - position_cost if cost_basis > 0 else 0
            profit_loss_pct = (profit_loss / position_cost * 100) if position_cost > 0 else 0

            total_value += current_value
            total_cost_basis += position_cost

            portfolio_data.append({
                'symbol': symbol,
                'amount': amount,
                'current_price': current_price,
                'current_value': current_value,
                'cost_basis': cost_basis,
                'position_cost': position_cost,
                'profit_loss': profit_loss,
                'profit_loss_pct': profit_loss_pct,
                'change_24h': change_24h,
                'purchase_date': row.get('purchase_date', '')
            })

        portfolio_df = pd.DataFrame(portfolio_data)

        # Calculate portfolio weights
        if total_value > 0:
            portfolio_df['weight'] = (portfolio_df['current_value'] / total_value * 100)

        # Save snapshot
        self._save_snapshot(portfolio_df, total_value, total_cost_basis)

        return portfolio_df

    def _save_snapshot(self, portfolio_df: pd.DataFrame, total_value: float, total_cost_basis: float):
        """Save portfolio snapshot"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'total_value': total_value,
            'total_cost_basis': total_cost_basis,
            'total_pnl': total_value - total_cost_basis if total_cost_basis > 0 else 0,
            'total_pnl_pct': ((total_value - total_cost_basis) / total_cost_basis * 100) if total_cost_basis > 0 else 0,
            'num_holdings': len(portfolio_df),
            'holdings': portfolio_df.to_dict('records')
        }

        self.snapshots.append(snapshot)
        self._save_snapshots()

    def get_latest_snapshot(self) -> Optional[Dict]:
        """Get most recent portfolio snapshot"""
        if self.snapshots:
            return self.snapshots[-1]
        return None

    def get_performance_history(self, days: int = 30) -> pd.DataFrame:
        """
        Get portfolio performance history

        Args:
            days: Number of days of history to return

        Returns:
            DataFrame with timestamp, total_value, total_pnl
        """
        if not self.snapshots:
            return pd.DataFrame()

        cutoff_date = datetime.now() - timedelta(days=days)

        history = []
        for snapshot in self.snapshots:
            timestamp = datetime.fromisoformat(snapshot['timestamp'])
            if timestamp >= cutoff_date:
                history.append({
                    'timestamp': timestamp,
                    'total_value': snapshot['total_value'],
                    'total_pnl': snapshot['total_pnl'],
                    'total_pnl_pct': snapshot['total_pnl_pct'],
                    'num_holdings': snapshot['num_holdings']
                })

        return pd.DataFrame(history)

    def calculate_daily_change(self) -> Optional[Dict]:
        """Calculate portfolio change in last 24 hours"""
        if len(self.snapshots) < 2:
            return None

        latest = self.snapshots[-1]
        latest_time = datetime.fromisoformat(latest['timestamp'])

        # Find snapshot from ~24 hours ago
        previous = None
        for snapshot in reversed(self.snapshots[:-1]):
            snapshot_time = datetime.fromisoformat(snapshot['timestamp'])
            if (latest_time - snapshot_time).total_seconds() >= 86400:  # 24 hours
                previous = snapshot
                break

        if not previous:
            return None

        value_change = latest['total_value'] - previous['total_value']
        pct_change = (value_change / previous['total_value'] * 100) if previous['total_value'] > 0 else 0

        return {
            'value_change': value_change,
            'pct_change': pct_change,
            'current_value': latest['total_value'],
            'previous_value': previous['total_value']
        }

    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary"""
        latest = self.get_latest_snapshot()
        if not latest:
            return {}

        daily_change = self.calculate_daily_change()

        return {
            'total_value': latest['total_value'],
            'total_cost_basis': latest['total_cost_basis'],
            'total_pnl': latest['total_pnl'],
            'total_pnl_pct': latest['total_pnl_pct'],
            'num_holdings': latest['num_holdings'],
            'daily_change': daily_change,
            'last_updated': latest['timestamp']
        }

    def create_sample_csv(self, output_path: str = "data/sample_holdings.csv"):
        """Create sample holdings CSV template"""
        sample_data = pd.DataFrame({
            'symbol': ['BTC', 'ETH'],
            'amount': [0.0, 0.0],
            'cost_basis': [0.0, 0.0],
            'purchase_date': [datetime.now().strftime('%Y-%m-%d')] * 2
        })

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        sample_data.to_csv(output_path, index=False)
        print(f"Sample holdings template created at: {output_path}")
