"""
Recommendation Tracker
Saves and tracks trading recommendations from the LLM for performance analysis
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class RecommendationTracker:
    """Track and store trading recommendations for backtesting and performance analysis"""

    def __init__(self, data_file: str = "data/recommendations.json"):
        """
        Initialize the recommendation tracker

        Args:
            data_file: Path to JSON file for storing recommendations
        """
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing recommendations
        self.recommendations = self._load_recommendations()

    def _load_recommendations(self) -> List[Dict]:
        """Load recommendations from JSON file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading recommendations: {e}")
                return []
        return []

    def _save_recommendations(self):
        """Save recommendations to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.recommendations, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving recommendations: {e}")

    def add_recommendation(
        self,
        crypto_symbol: str,
        recommendation_type: str,
        entry_price: float,
        current_price: float,
        stop_loss_price: float,
        take_profit_1: float,
        take_profit_2: Optional[float],
        position_size_pct: float,
        confidence: float,
        reasoning: str,
        technical_signals: Dict,
        market_context: Optional[Dict] = None,
        sentiment_score: float = 0,
        model_used: str = "gpt-4o"
    ) -> str:
        """
        Add a new recommendation to track

        Args:
            crypto_symbol: Symbol of the cryptocurrency (e.g., BTC, ETH)
            recommendation_type: BUY, SELL, or HOLD
            entry_price: Recommended entry price
            current_price: Current market price when recommendation was made
            stop_loss_price: Stop loss price
            take_profit_1: First take profit target
            take_profit_2: Second take profit target (optional)
            position_size_pct: Recommended position size as % of portfolio
            confidence: Confidence level (0-100)
            reasoning: LLM's reasoning for the recommendation
            technical_signals: Dictionary of technical indicator signals
            market_context: Market context data (timeframes, BTC correlation, etc.)
            sentiment_score: News sentiment score
            model_used: AI model used for recommendation

        Returns:
            Recommendation ID
        """
        rec_id = f"{crypto_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        recommendation = {
            'id': rec_id,
            'timestamp': datetime.now().isoformat(),
            'crypto_symbol': crypto_symbol,
            'recommendation': recommendation_type,
            'entry_price': entry_price,
            'current_price_at_recommendation': current_price,
            'stop_loss_price': stop_loss_price,
            'take_profit_1': take_profit_1,
            'take_profit_2': take_profit_2,
            'position_size_pct': position_size_pct,
            'confidence': confidence,
            'reasoning': reasoning,
            'technical_signals': technical_signals,
            'market_context': market_context,
            'sentiment_score': sentiment_score,
            'model_used': model_used,

            # Trade tracking fields
            'status': 'PENDING',  # PENDING, ENTERED, CLOSED, CANCELLED
            'entered': False,
            'entry_date': None,
            'actual_entry_price': None,
            'exit_date': None,
            'exit_price': None,
            'exit_reason': None,  # TP1, TP2, STOP_LOSS, MANUAL, EXPIRED
            'profit_loss': None,
            'profit_loss_pct': None,
            'outcome': None,  # WIN, LOSS, BREAKEVEN
            'notes': ''
        }

        self.recommendations.append(recommendation)
        self._save_recommendations()

        return rec_id

    def update_recommendation_status(
        self,
        rec_id: str,
        status: str,
        **kwargs
    ):
        """
        Update a recommendation's status and tracking fields

        Args:
            rec_id: Recommendation ID
            status: New status (ENTERED, CLOSED, CANCELLED)
            **kwargs: Additional fields to update (entry_price, exit_price, etc.)
        """
        for rec in self.recommendations:
            if rec['id'] == rec_id:
                rec['status'] = status

                # Update any additional fields
                for key, value in kwargs.items():
                    if key in rec:
                        rec[key] = value

                # If closing a trade, calculate P&L
                if status == 'CLOSED' and 'exit_price' in kwargs and rec['actual_entry_price']:
                    entry = rec['actual_entry_price']
                    exit_price = kwargs['exit_price']

                    # Calculate P&L
                    if rec['recommendation'] == 'BUY':
                        pnl_pct = ((exit_price - entry) / entry) * 100
                    elif rec['recommendation'] == 'SELL':
                        pnl_pct = ((entry - exit_price) / entry) * 100
                    else:
                        pnl_pct = 0

                    rec['profit_loss_pct'] = pnl_pct
                    rec['profit_loss'] = entry * (pnl_pct / 100)  # Approximate

                    # Determine outcome
                    if pnl_pct > 1:
                        rec['outcome'] = 'WIN'
                    elif pnl_pct < -1:
                        rec['outcome'] = 'LOSS'
                    else:
                        rec['outcome'] = 'BREAKEVEN'

                    rec['exit_date'] = datetime.now().isoformat()

                self._save_recommendations()
                return True

        return False

    def enter_trade(self, rec_id: str, actual_entry_price: float, notes: str = ""):
        """Mark a recommendation as entered"""
        return self.update_recommendation_status(
            rec_id,
            'ENTERED',
            entered=True,
            entry_date=datetime.now().isoformat(),
            actual_entry_price=actual_entry_price,
            notes=notes
        )

    def close_trade(
        self,
        rec_id: str,
        exit_price: float,
        exit_reason: str,
        notes: str = ""
    ):
        """Close a trade and calculate P&L"""
        return self.update_recommendation_status(
            rec_id,
            'CLOSED',
            exit_price=exit_price,
            exit_reason=exit_reason,
            notes=notes
        )

    def cancel_recommendation(self, rec_id: str, reason: str = ""):
        """Cancel a recommendation that wasn't entered"""
        return self.update_recommendation_status(
            rec_id,
            'CANCELLED',
            notes=reason
        )

    def get_all_recommendations(self) -> pd.DataFrame:
        """Get all recommendations as a DataFrame"""
        if not self.recommendations:
            return pd.DataFrame()

        df = pd.DataFrame(self.recommendations)

        # Convert timestamps
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        if 'entry_date' in df.columns:
            df['entry_date'] = pd.to_datetime(df['entry_date'])
        if 'exit_date' in df.columns:
            df['exit_date'] = pd.to_datetime(df['exit_date'])

        return df

    def get_pending_recommendations(self) -> pd.DataFrame:
        """Get recommendations that haven't been entered yet"""
        df = self.get_all_recommendations()
        if df.empty:
            return df
        return df[df['status'] == 'PENDING']

    def get_active_trades(self) -> pd.DataFrame:
        """Get trades that are currently open"""
        df = self.get_all_recommendations()
        if df.empty:
            return df
        return df[df['status'] == 'ENTERED']

    def get_closed_trades(self) -> pd.DataFrame:
        """Get all closed trades"""
        df = self.get_all_recommendations()
        if df.empty:
            return df
        return df[df['status'] == 'CLOSED']

    def get_recommendation_by_id(self, rec_id: str) -> Optional[Dict]:
        """Get a specific recommendation by ID"""
        for rec in self.recommendations:
            if rec['id'] == rec_id:
                return rec
        return None

    def delete_recommendation(self, rec_id: str) -> bool:
        """Delete a recommendation"""
        for i, rec in enumerate(self.recommendations):
            if rec['id'] == rec_id:
                self.recommendations.pop(i)
                self._save_recommendations()
                return True
        return False

    def get_statistics(self) -> Dict:
        """Get overall performance statistics"""
        closed_trades = self.get_closed_trades()

        if closed_trades.empty:
            return {
                'total_recommendations': len(self.recommendations),
                'pending': len(self.get_pending_recommendations()),
                'active': len(self.get_active_trades()),
                'closed': 0,
                'win_rate': 0,
                'total_return': 0,
                'avg_return_per_trade': 0,
                'best_trade': 0,
                'worst_trade': 0
            }

        wins = len(closed_trades[closed_trades['outcome'] == 'WIN'])
        losses = len(closed_trades[closed_trades['outcome'] == 'LOSS'])
        total_closed = len(closed_trades)

        win_rate = (wins / total_closed * 100) if total_closed > 0 else 0

        returns = closed_trades['profit_loss_pct'].dropna()
        total_return = returns.sum()
        avg_return = returns.mean()
        best_trade = returns.max()
        worst_trade = returns.min()

        return {
            'total_recommendations': len(self.recommendations),
            'pending': len(self.get_pending_recommendations()),
            'active': len(self.get_active_trades()),
            'closed': total_closed,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'total_return': total_return,
            'avg_return_per_trade': avg_return,
            'best_trade': best_trade,
            'worst_trade': worst_trade
        }
