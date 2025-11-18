"""
Performance Calculator
Calculate advanced performance metrics for trading recommendations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class PerformanceCalculator:
    """Calculate trading performance metrics"""

    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sharpe Ratio

        Args:
            returns: Series of returns (as percentages)
            risk_free_rate: Annual risk-free rate (default 0%)

        Returns:
            Sharpe ratio
        """
        if len(returns) < 2:
            return 0.0

        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        if excess_returns.std() == 0:
            return 0.0

        sharpe = np.sqrt(252) * (excess_returns.mean() / excess_returns.std())
        return sharpe

    @staticmethod
    def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sortino Ratio (only considers downside volatility)

        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate

        Returns:
            Sortino ratio
        """
        if len(returns) < 2:
            return 0.0

        excess_returns = returns - (risk_free_rate / 252)
        downside_returns = excess_returns[excess_returns < 0]

        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0

        sortino = np.sqrt(252) * (excess_returns.mean() / downside_returns.std())
        return sortino

    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> Dict:
        """
        Calculate maximum drawdown

        Args:
            equity_curve: Series of cumulative portfolio values

        Returns:
            Dict with max_drawdown_pct, max_drawdown_value, peak_value, trough_value
        """
        if len(equity_curve) < 2:
            return {
                'max_drawdown_pct': 0,
                'max_drawdown_value': 0,
                'peak_value': 0,
                'trough_value': 0,
                'peak_date': None,
                'trough_date': None
            }

        # Calculate running maximum
        running_max = equity_curve.expanding().max()

        # Calculate drawdown
        drawdown = (equity_curve - running_max) / running_max * 100

        # Find maximum drawdown
        max_dd_idx = drawdown.idxmin()
        max_dd_pct = drawdown.min()

        # Find the peak before this drawdown
        peak_idx = equity_curve[:max_dd_idx].idxmax()

        return {
            'max_drawdown_pct': max_dd_pct,
            'max_drawdown_value': equity_curve[peak_idx] - equity_curve[max_dd_idx],
            'peak_value': equity_curve[peak_idx],
            'trough_value': equity_curve[max_dd_idx],
            'peak_date': peak_idx,
            'trough_date': max_dd_idx
        }

    @staticmethod
    def calculate_win_rate(trades_df: pd.DataFrame) -> float:
        """Calculate win rate percentage"""
        if trades_df.empty or 'outcome' not in trades_df.columns:
            return 0.0

        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['outcome'] == 'WIN'])

        return (winning_trades / total_trades * 100) if total_trades > 0 else 0.0

    @staticmethod
    def calculate_profit_factor(trades_df: pd.DataFrame) -> float:
        """
        Calculate profit factor (gross profit / gross loss)

        Returns:
            Profit factor (>1 means profitable, <1 means losing)
        """
        if trades_df.empty or 'profit_loss_pct' not in trades_df.columns:
            return 0.0

        gross_profit = trades_df[trades_df['profit_loss_pct'] > 0]['profit_loss_pct'].sum()
        gross_loss = abs(trades_df[trades_df['profit_loss_pct'] < 0]['profit_loss_pct'].sum())

        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0

        return gross_profit / gross_loss

    @staticmethod
    def calculate_average_win_loss_ratio(trades_df: pd.DataFrame) -> Dict:
        """Calculate average win size vs average loss size"""
        if trades_df.empty or 'profit_loss_pct' not in trades_df.columns:
            return {
                'avg_win': 0,
                'avg_loss': 0,
                'win_loss_ratio': 0
            }

        wins = trades_df[trades_df['profit_loss_pct'] > 0]['profit_loss_pct']
        losses = trades_df[trades_df['profit_loss_pct'] < 0]['profit_loss_pct']

        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = abs(losses.mean()) if len(losses) > 0 else 0

        win_loss_ratio = (avg_win / avg_loss) if avg_loss != 0 else 0

        return {
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'win_loss_ratio': win_loss_ratio
        }

    @staticmethod
    def calculate_expectancy(trades_df: pd.DataFrame) -> float:
        """
        Calculate expectancy (expected value per trade)

        Formula: (Win% * Avg Win) - (Loss% * Avg Loss)
        """
        if trades_df.empty or 'profit_loss_pct' not in trades_df.columns:
            return 0.0

        total_trades = len(trades_df)
        wins = trades_df[trades_df['profit_loss_pct'] > 0]
        losses = trades_df[trades_df['profit_loss_pct'] < 0]

        win_rate = len(wins) / total_trades if total_trades > 0 else 0
        loss_rate = len(losses) / total_trades if total_trades > 0 else 0

        avg_win = wins['profit_loss_pct'].mean() if len(wins) > 0 else 0
        avg_loss = abs(losses['profit_loss_pct'].mean()) if len(losses) > 0 else 0

        expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)

        return expectancy

    @staticmethod
    def build_equity_curve(
        trades_df: pd.DataFrame,
        initial_capital: float = 10000
    ) -> pd.DataFrame:
        """
        Build equity curve from closed trades

        Args:
            trades_df: DataFrame of closed trades
            initial_capital: Starting capital

        Returns:
            DataFrame with timestamp and equity columns
        """
        if trades_df.empty or 'exit_date' not in trades_df.columns:
            return pd.DataFrame({
                'timestamp': [datetime.now()],
                'equity': [initial_capital]
            })

        # Sort by exit date
        sorted_trades = trades_df.sort_values('exit_date').copy()

        # Calculate cumulative return
        equity_curve = []
        current_equity = initial_capital

        # Add starting point
        first_date = sorted_trades['exit_date'].min()
        equity_curve.append({
            'timestamp': first_date - timedelta(days=1),
            'equity': initial_capital
        })

        for _, trade in sorted_trades.iterrows():
            if pd.notna(trade['profit_loss_pct']):
                # Assume we risk the position_size_pct of capital
                position_size = current_equity * (trade['position_size_pct'] / 100)
                pnl = position_size * (trade['profit_loss_pct'] / 100)
                current_equity += pnl

                equity_curve.append({
                    'timestamp': trade['exit_date'],
                    'equity': current_equity
                })

        return pd.DataFrame(equity_curve)

    @staticmethod
    def calculate_comprehensive_metrics(
        trades_df: pd.DataFrame,
        initial_capital: float = 10000
    ) -> Dict:
        """
        Calculate all performance metrics at once

        Args:
            trades_df: DataFrame of closed trades
            initial_capital: Starting capital

        Returns:
            Dictionary with all performance metrics
        """
        if trades_df.empty:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_return_pct': 0,
                'avg_return_per_trade': 0,
                'best_trade': 0,
                'worst_trade': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'sortino_ratio': 0,
                'max_drawdown_pct': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'win_loss_ratio': 0,
                'expectancy': 0,
                'total_profit': 0,
                'final_capital': initial_capital
            }

        # Build equity curve
        equity_curve = PerformanceCalculator.build_equity_curve(trades_df, initial_capital)

        # Calculate returns
        returns = trades_df['profit_loss_pct'].dropna()

        # Calculate metrics
        win_rate = PerformanceCalculator.calculate_win_rate(trades_df)
        profit_factor = PerformanceCalculator.calculate_profit_factor(trades_df)
        sharpe = PerformanceCalculator.calculate_sharpe_ratio(returns)
        sortino = PerformanceCalculator.calculate_sortino_ratio(returns)
        max_dd = PerformanceCalculator.calculate_max_drawdown(equity_curve['equity'])
        win_loss = PerformanceCalculator.calculate_average_win_loss_ratio(trades_df)
        expectancy = PerformanceCalculator.calculate_expectancy(trades_df)

        total_return_pct = ((equity_curve['equity'].iloc[-1] - initial_capital) / initial_capital * 100)

        return {
            'total_trades': len(trades_df),
            'win_rate': win_rate,
            'total_return_pct': total_return_pct,
            'avg_return_per_trade': returns.mean(),
            'best_trade': returns.max(),
            'worst_trade': returns.min(),
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown_pct': max_dd['max_drawdown_pct'],
            'avg_win': win_loss['avg_win'],
            'avg_loss': win_loss['avg_loss'],
            'win_loss_ratio': win_loss['win_loss_ratio'],
            'expectancy': expectancy,
            'total_profit': equity_curve['equity'].iloc[-1] - initial_capital,
            'final_capital': equity_curve['equity'].iloc[-1]
        }
