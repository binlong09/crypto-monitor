"""
Market Context Analysis
Provides multi-timeframe analysis, BTC correlation, dominance tracking, and market regime detection
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

from .technical_indicators import TechnicalIndicators


class MarketContext:
    """Analyzes market context including timeframes, correlations, and dominance"""

    def __init__(self, coingecko_client):
        """
        Initialize MarketContext analyzer

        Args:
            coingecko_client: CoinGeckoClient instance for fetching data
        """
        self.client = coingecko_client

    def analyze_multiple_timeframes(self, crypto_id: str, timeframes: List[int] = [7, 30, 90]) -> Dict:
        """
        Analyze crypto across multiple timeframes and find signal alignment

        Args:
            crypto_id: CoinGecko crypto ID
            timeframes: List of timeframes in days (default: [7, 30, 90])

        Returns:
            Dict with timeframe analysis and alignment
        """
        results = {}

        for days in timeframes:
            # Fetch historical data
            hist_df = self.client.get_historical_prices(crypto_id, days)

            if hist_df is None or hist_df.empty:
                results[f'{days}d'] = {'error': 'No data available'}
                continue

            # Calculate indicators
            try:
                tech = TechnicalIndicators(hist_df)
                indicators = tech.calculate_all()

                # Extract key signals
                signals = indicators.get('signals', {})

                results[f'{days}d'] = {
                    'overall_signal': signals.get('overall', 'NEUTRAL'),
                    'confidence': signals.get('confidence', 0),
                    'bullish_count': signals.get('bullish', 0),
                    'bearish_count': signals.get('bearish', 0),
                    'rsi': indicators.get('rsi', {}).get('value'),
                    'macd_signal': indicators.get('macd', {}).get('trade_signal'),
                    'trend': self._determine_trend(hist_df),
                    'volatility': self._calculate_volatility(hist_df),
                    'price_change_pct': ((hist_df['price'].iloc[-1] - hist_df['price'].iloc[0]) / hist_df['price'].iloc[0] * 100)
                }
            except Exception as e:
                results[f'{days}d'] = {'error': str(e)}

        # Calculate timeframe alignment
        alignment = self._calculate_timeframe_alignment(results)

        return {
            'timeframes': results,
            'alignment': alignment
        }

    def _determine_trend(self, df: pd.DataFrame) -> str:
        """Determine trend direction from price data"""
        if len(df) < 10:
            return 'UNKNOWN'

        prices = df['price'].values[-10:]
        slope = np.polyfit(range(10), prices, 1)[0]

        if slope > prices[-1] * 0.01:  # >1% slope
            return 'STRONG_UP'
        elif slope > 0:
            return 'UP'
        elif slope < -prices[-1] * 0.01:
            return 'STRONG_DOWN'
        elif slope < 0:
            return 'DOWN'
        else:
            return 'SIDEWAYS'

    def _calculate_volatility(self, df: pd.DataFrame) -> float:
        """Calculate volatility as percentage"""
        if len(df) < 5:
            return 0

        returns = df['price'].pct_change().dropna()
        volatility = returns.std() * 100  # as percentage
        return volatility

    def _calculate_timeframe_alignment(self, timeframe_results: Dict) -> Dict:
        """
        Calculate how well signals align across timeframes

        Returns:
            Dict with alignment score and assessment
        """
        valid_timeframes = [tf for tf in timeframe_results.values() if 'error' not in tf]

        if len(valid_timeframes) < 2:
            return {
                'score': 0,
                'assessment': 'INSUFFICIENT_DATA',
                'recommendation': 'Need data from multiple timeframes'
            }

        # Count bullish/bearish signals
        bullish_count = sum(1 for tf in valid_timeframes if tf.get('overall_signal') == 'BULLISH')
        bearish_count = sum(1 for tf in valid_timeframes if tf.get('overall_signal') == 'BEARISH')
        neutral_count = sum(1 for tf in valid_timeframes if tf.get('overall_signal') == 'NEUTRAL')

        total = len(valid_timeframes)

        # Calculate alignment score (0-100)
        if bullish_count == total:
            score = 100
            assessment = 'PERFECT_BULLISH_ALIGNMENT'
            recommendation = '🟢 All timeframes bullish - very strong signal!'
        elif bearish_count == total:
            score = 100
            assessment = 'PERFECT_BEARISH_ALIGNMENT'
            recommendation = '🔴 All timeframes bearish - very strong signal!'
        elif bullish_count > bearish_count:
            score = (bullish_count / total) * 100
            assessment = 'BULLISH_MAJORITY'
            recommendation = f'🟢 {bullish_count}/{total} timeframes bullish - moderately strong signal'
        elif bearish_count > bullish_count:
            score = (bearish_count / total) * 100
            assessment = 'BEARISH_MAJORITY'
            recommendation = f'🔴 {bearish_count}/{total} timeframes bearish - moderately strong signal'
        else:
            score = 50
            assessment = 'MIXED_SIGNALS'
            recommendation = '⚠️ Mixed signals across timeframes - proceed with caution'

        return {
            'score': round(score, 1),
            'assessment': assessment,
            'recommendation': recommendation,
            'bullish_timeframes': bullish_count,
            'bearish_timeframes': bearish_count,
            'neutral_timeframes': neutral_count,
            'total_timeframes': total
        }

    def analyze_btc_correlation(self, crypto_id: str, days: int = 30) -> Dict:
        """
        Calculate correlation with Bitcoin

        Args:
            crypto_id: CoinGecko crypto ID
            days: Period for correlation (default 30 days)

        Returns:
            Dict with correlation coefficient and analysis
        """
        # Skip if analyzing Bitcoin itself
        if crypto_id == 'bitcoin':
            return {
                'correlation': 1.0,
                'strength': 'SELF',
                'recommendation': 'Analyzing Bitcoin itself'
            }

        # Fetch both crypto and BTC data
        crypto_df = self.client.get_historical_prices(crypto_id, days)
        btc_df = self.client.get_historical_prices('bitcoin', days)

        if crypto_df is None or crypto_df.empty or btc_df is None or btc_df.empty:
            return {'error': 'Unable to fetch data for correlation analysis'}

        # Align dataframes by timestamp
        merged = pd.merge(crypto_df, btc_df, on='timestamp', suffixes=('_crypto', '_btc'))

        if len(merged) < 10:
            return {'error': 'Insufficient overlapping data for correlation'}

        # Calculate correlation
        correlation = merged['price_crypto'].corr(merged['price_btc'])

        # Determine correlation strength
        abs_corr = abs(correlation)
        if abs_corr > 0.8:
            strength = 'VERY_STRONG'
        elif abs_corr > 0.6:
            strength = 'STRONG'
        elif abs_corr > 0.4:
            strength = 'MODERATE'
        elif abs_corr > 0.2:
            strength = 'WEAK'
        else:
            strength = 'VERY_WEAK'

        # Determine direction
        if correlation > 0:
            direction = 'POSITIVE'
            direction_desc = 'moves with Bitcoin'
        else:
            direction = 'NEGATIVE'
            direction_desc = 'moves opposite to Bitcoin'

        # Generate recommendation
        if abs_corr > 0.7:
            if correlation > 0:
                recommendation = f'⚠️ Highly correlated with BTC ({correlation:.2f}) - BTC trend dominates'
            else:
                recommendation = f'⚠️ Strongly inversely correlated with BTC ({correlation:.2f}) - rare!'
        elif abs_corr > 0.4:
            recommendation = f'Moderately correlated with BTC ({correlation:.2f}) - some independence'
        else:
            recommendation = f'✅ Low correlation with BTC ({correlation:.2f}) - moves independently'

        return {
            'correlation': correlation,
            'strength': strength,
            'direction': direction,
            'direction_description': direction_desc,
            'recommendation': recommendation
        }

    def get_btc_dominance(self) -> Dict:
        """
        Get Bitcoin dominance (% of total crypto market cap)

        Returns:
            Dict with dominance data and market regime
        """
        try:
            # Get BTC market data
            btc_data = self.client.get_market_data('bitcoin')

            if not btc_data:
                return {'error': 'Unable to fetch BTC market data'}

            btc_market_cap = btc_data.get('market_cap', 0)

            # Get global crypto market data (if available from CoinGecko)
            # Note: CoinGecko free tier may not have this endpoint
            # We'll estimate or mark as unavailable

            # For now, we'll use a typical range and mark it as estimated
            # In production, you'd fetch from /global endpoint

            # Typical BTC dominance ranges: 40-60%
            # We'll return a placeholder for now
            return {
                'btc_market_cap': btc_market_cap,
                'dominance_pct': None,  # Would need /global endpoint
                'note': 'BTC dominance requires CoinGecko Pro API',
                'recommendation': 'Check coinmarketcap.com for current BTC dominance'
            }

        except Exception as e:
            return {'error': str(e)}

    def analyze_market_regime(self, fear_greed_index: Optional[int] = None) -> Dict:
        """
        Determine overall market regime based on available data

        Args:
            fear_greed_index: Fear & Greed Index value (0-100)

        Returns:
            Dict with market regime assessment
        """
        regime = {
            'fear_greed': None,
            'regime': 'UNKNOWN',
            'recommendation': ''
        }

        if fear_greed_index is not None:
            regime['fear_greed'] = fear_greed_index

            if fear_greed_index < 20:
                regime['regime'] = 'EXTREME_FEAR'
                regime['sentiment'] = 'Extreme Fear'
                regime['recommendation'] = '💰 CONTRARIAN BUY ZONE - Market panic creates opportunities'
                regime['position_sizing'] = 'INCREASE'
                regime['strategy'] = 'Accumulate quality assets'
            elif fear_greed_index < 40:
                regime['regime'] = 'FEAR'
                regime['sentiment'] = 'Fear'
                regime['recommendation'] = '✅ BUY ZONE - Market nervous, good entry prices'
                regime['position_sizing'] = 'NORMAL_TO_INCREASE'
                regime['strategy'] = 'Buy dips, DCA'
            elif fear_greed_index < 60:
                regime['regime'] = 'NEUTRAL'
                regime['sentiment'] = 'Neutral'
                regime['recommendation'] = '➖ BALANCED MARKET - Trade based on technicals'
                regime['position_sizing'] = 'NORMAL'
                regime['strategy'] = 'Follow technical signals'
            elif fear_greed_index < 80:
                regime['regime'] = 'GREED'
                regime['sentiment'] = 'Greed'
                regime['recommendation'] = '⚠️ CAUTION ZONE - Market getting heated, take some profits'
                regime['position_sizing'] = 'REDUCE'
                regime['strategy'] = 'Scale out of positions'
            else:
                regime['regime'] = 'EXTREME_GREED'
                regime['sentiment'] = 'Extreme Greed'
                regime['recommendation'] = '🔴 SELL ZONE - Market euphoric, significant correction likely'
                regime['position_sizing'] = 'MINIMIZE'
                regime['strategy'] = 'Take profits, wait for pullback'

        return regime

    def get_comprehensive_context(
        self,
        crypto_id: str,
        current_period_days: int = 30,
        fear_greed_value: Optional[int] = None
    ) -> Dict:
        """
        Get comprehensive market context analysis

        Args:
            crypto_id: CoinGecko crypto ID
            current_period_days: Main analysis period
            fear_greed_value: Fear & Greed Index value

        Returns:
            Dict with all market context data
        """
        print(f"📊 Analyzing market context for {crypto_id}...")

        context = {}

        # Multi-timeframe analysis
        print("  → Multi-timeframe analysis...")
        context['timeframe_analysis'] = self.analyze_multiple_timeframes(crypto_id)

        # BTC correlation (if not Bitcoin)
        if crypto_id != 'bitcoin':
            print("  → BTC correlation...")
            context['btc_correlation'] = self.analyze_btc_correlation(crypto_id, current_period_days)
        else:
            context['btc_correlation'] = {'note': 'Analyzing Bitcoin itself'}

        # BTC dominance
        print("  → BTC dominance...")
        context['btc_dominance'] = self.get_btc_dominance()

        # Market regime
        print("  → Market regime...")
        context['market_regime'] = self.analyze_market_regime(fear_greed_value)

        print("  ✓ Market context analysis complete!")

        return context
