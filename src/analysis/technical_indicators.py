"""
Technical Indicators for Cryptocurrency Analysis
Calculates RSI, MACD, Bollinger Bands, Moving Averages, Support/Resistance
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class TechnicalIndicators:
    """Calculate technical indicators for price data"""

    def __init__(self, price_df: pd.DataFrame):
        """
        Initialize with price DataFrame

        Args:
            price_df: DataFrame with columns ['timestamp', 'price']
        """
        if price_df is None or price_df.empty:
            raise ValueError("Price DataFrame is empty or None")

        self.df = price_df.copy()

        # Validate required columns
        if 'timestamp' not in self.df.columns:
            raise ValueError(f"DataFrame missing 'timestamp' column. Available columns: {list(self.df.columns)}")

        if 'price' not in self.df.columns:
            raise ValueError(f"DataFrame missing 'price' column. Available columns: {list(self.df.columns)}")

        # Sort by timestamp
        self.df = self.df.sort_values('timestamp').reset_index(drop=True)

    def calculate_all(self) -> Dict:
        """
        Calculate all technical indicators

        Returns:
            Dictionary with all indicator values and signals
        """
        indicators = {}

        # Moving Averages
        indicators['sma'] = self.calculate_sma()
        indicators['ema'] = self.calculate_ema()

        # Momentum Indicators
        indicators['rsi'] = self.calculate_rsi()
        indicators['macd'] = self.calculate_macd()

        # Volatility Indicators
        indicators['bollinger'] = self.calculate_bollinger_bands()

        # Support/Resistance
        indicators['support_resistance'] = self.calculate_support_resistance()

        # Volume Analysis
        if 'volume' in self.df.columns:
            indicators['volume_analysis'] = self.analyze_volume()

        # Advanced Indicators
        indicators['stochastic'] = self.calculate_stochastic()
        indicators['adx'] = self.calculate_adx()
        indicators['atr'] = self.calculate_atr()

        if 'volume' in self.df.columns:
            indicators['obv'] = self.calculate_obv()

        # Pattern Recognition
        indicators['price_patterns'] = self.detect_price_patterns()
        indicators['chart_patterns'] = self.detect_chart_patterns()

        # Trading Signals
        indicators['signals'] = self.generate_signals(indicators)

        return indicators

    def calculate_sma(self, periods: List[int] = [20, 50, 200]) -> Dict:
        """Calculate Simple Moving Averages"""
        sma = {}

        for period in periods:
            if len(self.df) >= period:
                self.df[f'SMA_{period}'] = self.df['price'].rolling(window=period).mean()
                sma[f'SMA_{period}'] = {
                    'value': self.df[f'SMA_{period}'].iloc[-1],
                    'current_price': self.df['price'].iloc[-1],
                    'signal': 'BULLISH' if self.df['price'].iloc[-1] > self.df[f'SMA_{period}'].iloc[-1] else 'BEARISH'
                }

        # Golden Cross / Death Cross detection (SMA 50 vs SMA 200)
        if len(self.df) >= 200 and 'SMA_50' in self.df.columns and 'SMA_200' in self.df.columns:
            sma_50_current = self.df['SMA_50'].iloc[-1]
            sma_200_current = self.df['SMA_200'].iloc[-1]
            sma_50_prev = self.df['SMA_50'].iloc[-2] if len(self.df) > 1 else sma_50_current
            sma_200_prev = self.df['SMA_200'].iloc[-2] if len(self.df) > 1 else sma_200_current

            if sma_50_prev <= sma_200_prev and sma_50_current > sma_200_current:
                sma['golden_cross'] = True
                sma['cross_signal'] = 'STRONG_BULLISH'
            elif sma_50_prev >= sma_200_prev and sma_50_current < sma_200_current:
                sma['death_cross'] = True
                sma['cross_signal'] = 'STRONG_BEARISH'
            else:
                sma['golden_cross'] = False
                sma['death_cross'] = False
                sma['cross_signal'] = 'BULLISH' if sma_50_current > sma_200_current else 'BEARISH'

        return sma

    def calculate_ema(self, periods: List[int] = [12, 26, 50]) -> Dict:
        """Calculate Exponential Moving Averages"""
        ema = {}

        for period in periods:
            if len(self.df) >= period:
                self.df[f'EMA_{period}'] = self.df['price'].ewm(span=period, adjust=False).mean()
                ema[f'EMA_{period}'] = {
                    'value': self.df[f'EMA_{period}'].iloc[-1],
                    'current_price': self.df['price'].iloc[-1],
                    'signal': 'BULLISH' if self.df['price'].iloc[-1] > self.df[f'EMA_{period}'].iloc[-1] else 'BEARISH'
                }

        return ema

    def calculate_rsi(self, period: int = 14) -> Dict:
        """
        Calculate Relative Strength Index (RSI)

        RSI ranges from 0-100:
        - Above 70: Overbought (potential sell signal)
        - Below 30: Oversold (potential buy signal)
        """
        if len(self.df) < period + 1:
            return {'error': 'Insufficient data for RSI calculation'}

        # Calculate price changes
        delta = self.df['price'].diff()

        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)

        # Calculate average gains and losses
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()

        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))

        self.df['RSI'] = rsi
        current_rsi = rsi.iloc[-1]

        # Determine signal
        if current_rsi > 70:
            signal = 'OVERBOUGHT'
            recommendation = 'Consider selling or taking profits'
        elif current_rsi < 30:
            signal = 'OVERSOLD'
            recommendation = 'Potential buying opportunity'
        elif current_rsi > 60:
            signal = 'BULLISH'
            recommendation = 'Upward momentum'
        elif current_rsi < 40:
            signal = 'BEARISH'
            recommendation = 'Downward momentum'
        else:
            signal = 'NEUTRAL'
            recommendation = 'No strong signal'

        return {
            'value': current_rsi,
            'signal': signal,
            'recommendation': recommendation,
            'overbought': current_rsi > 70,
            'oversold': current_rsi < 30
        }

    def calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """
        Calculate MACD (Moving Average Convergence Divergence)

        Returns:
            MACD line, signal line, histogram, and trading signal
        """
        if len(self.df) < slow:
            return {'error': 'Insufficient data for MACD calculation'}

        # Calculate EMAs
        ema_fast = self.df['price'].ewm(span=fast, adjust=False).mean()
        ema_slow = self.df['price'].ewm(span=slow, adjust=False).mean()

        # MACD line
        macd_line = ema_fast - ema_slow

        # Signal line
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()

        # Histogram
        histogram = macd_line - signal_line

        self.df['MACD'] = macd_line
        self.df['MACD_signal'] = signal_line
        self.df['MACD_histogram'] = histogram

        # Current values
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_histogram = histogram.iloc[-1]

        # Previous values for crossover detection
        prev_macd = macd_line.iloc[-2] if len(macd_line) > 1 else current_macd
        prev_signal = signal_line.iloc[-2] if len(signal_line) > 1 else current_signal

        # Determine signal
        if prev_macd <= prev_signal and current_macd > current_signal:
            trade_signal = 'BULLISH_CROSSOVER'
            recommendation = 'Buy signal - MACD crossed above signal line'
        elif prev_macd >= prev_signal and current_macd < current_signal:
            trade_signal = 'BEARISH_CROSSOVER'
            recommendation = 'Sell signal - MACD crossed below signal line'
        elif current_macd > current_signal and current_histogram > 0:
            trade_signal = 'BULLISH'
            recommendation = 'Upward momentum - MACD above signal line'
        elif current_macd < current_signal and current_histogram < 0:
            trade_signal = 'BEARISH'
            recommendation = 'Downward momentum - MACD below signal line'
        else:
            trade_signal = 'NEUTRAL'
            recommendation = 'No clear trend'

        return {
            'macd': current_macd,
            'signal': current_signal,
            'histogram': current_histogram,
            'trade_signal': trade_signal,
            'recommendation': recommendation
        }

    def calculate_bollinger_bands(self, period: int = 20, std_dev: float = 2.0) -> Dict:
        """
        Calculate Bollinger Bands

        Bollinger Bands consist of:
        - Middle band: SMA
        - Upper band: SMA + (std_dev * standard deviation)
        - Lower band: SMA - (std_dev * standard deviation)
        """
        if len(self.df) < period:
            return {'error': 'Insufficient data for Bollinger Bands'}

        # Calculate middle band (SMA)
        sma = self.df['price'].rolling(window=period).mean()

        # Calculate standard deviation
        std = self.df['price'].rolling(window=period).std()

        # Calculate upper and lower bands
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)

        self.df['BB_middle'] = sma
        self.df['BB_upper'] = upper_band
        self.df['BB_lower'] = lower_band

        # Current values
        current_price = self.df['price'].iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_middle = sma.iloc[-1]
        current_lower = lower_band.iloc[-1]

        # Band width (volatility indicator)
        band_width = ((current_upper - current_lower) / current_middle) * 100

        # Price position within bands
        price_position = ((current_price - current_lower) / (current_upper - current_lower)) * 100

        # Determine signal
        if current_price > current_upper:
            signal = 'OVERBOUGHT'
            recommendation = 'Price above upper band - potential reversal down'
        elif current_price < current_lower:
            signal = 'OVERSOLD'
            recommendation = 'Price below lower band - potential reversal up'
        elif current_price > current_middle:
            signal = 'BULLISH'
            recommendation = 'Price above middle band - upward trend'
        elif current_price < current_middle:
            signal = 'BEARISH'
            recommendation = 'Price below middle band - downward trend'
        else:
            signal = 'NEUTRAL'
            recommendation = 'Price at middle band'

        return {
            'upper': current_upper,
            'middle': current_middle,
            'lower': current_lower,
            'current_price': current_price,
            'band_width': band_width,
            'price_position': price_position,
            'signal': signal,
            'recommendation': recommendation,
            'high_volatility': band_width > 10  # Threshold for high volatility
        }

    def calculate_support_resistance(self, window: int = 20) -> Dict:
        """
        Calculate support and resistance levels using local minima/maxima
        """
        if len(self.df) < window:
            return {'error': 'Insufficient data'}

        prices = self.df['price'].values
        current_price = prices[-1]

        # Find local minima (support) and maxima (resistance)
        support_levels = []
        resistance_levels = []

        for i in range(window, len(prices) - window):
            # Local minimum (support)
            if prices[i] == min(prices[i-window:i+window+1]):
                support_levels.append(prices[i])

            # Local maximum (resistance)
            if prices[i] == max(prices[i-window:i+window+1]):
                resistance_levels.append(prices[i])

        # Get nearest support and resistance
        support_below = [s for s in support_levels if s < current_price]
        resistance_above = [r for r in resistance_levels if r > current_price]

        nearest_support = max(support_below) if support_below else min(prices)
        nearest_resistance = min(resistance_above) if resistance_above else max(prices)

        # Calculate distance from support/resistance
        distance_to_support = ((current_price - nearest_support) / current_price) * 100
        distance_to_resistance = ((nearest_resistance - current_price) / current_price) * 100

        return {
            'current_price': current_price,
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance,
            'distance_to_support_pct': distance_to_support,
            'distance_to_resistance_pct': distance_to_resistance,
            'all_support_levels': sorted(set(support_levels), reverse=True)[:5],
            'all_resistance_levels': sorted(set(resistance_levels))[:5],
            'recommendation': self._support_resistance_recommendation(
                distance_to_support,
                distance_to_resistance
            )
        }

    def _support_resistance_recommendation(self, dist_support: float, dist_resistance: float) -> str:
        """Generate recommendation based on support/resistance"""
        if dist_support < 2:
            return 'Near support - potential bounce zone'
        elif dist_resistance < 2:
            return 'Near resistance - potential reversal zone'
        elif dist_support < dist_resistance:
            return 'Closer to support than resistance'
        else:
            return 'Closer to resistance than support'

    def analyze_volume(self) -> Dict:
        """
        Comprehensive volume analysis including trends, spikes, and divergence

        Returns:
            Dict with volume metrics, trends, spikes, and divergence signals
        """
        if 'volume' not in self.df.columns:
            return {'error': 'Volume data not available'}

        if len(self.df) < 20:
            return {'error': 'Insufficient data for volume analysis (need 20+ data points)'}

        # Calculate volume moving averages
        self.df['volume_ma_20'] = self.df['volume'].rolling(window=20).mean()
        self.df['volume_ma_50'] = self.df['volume'].rolling(window=min(50, len(self.df))).mean()

        # Current metrics
        current_volume = self.df['volume'].iloc[-1]
        avg_volume_20 = self.df['volume_ma_20'].iloc[-1]
        avg_volume_50 = self.df['volume_ma_50'].iloc[-1] if len(self.df) >= 50 else avg_volume_20

        # Volume ratio
        volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1

        # 1. Volume Level Signal
        if volume_ratio > 2.5:
            volume_signal = 'EXTREME_VOLUME'
            volume_recommendation = 'Extreme volume spike - major event or whale activity'
        elif volume_ratio > 2:
            volume_signal = 'VERY_HIGH_VOLUME'
            volume_recommendation = 'Very high volume - strong conviction in price move'
        elif volume_ratio > 1.5:
            volume_signal = 'HIGH_VOLUME'
            volume_recommendation = 'Above average volume - increased interest'
        elif volume_ratio < 0.5:
            volume_signal = 'LOW_VOLUME'
            volume_recommendation = 'Low volume - lack of conviction, weak move'
        else:
            volume_signal = 'NORMAL'
            volume_recommendation = 'Normal volume levels'

        # 2. Volume Trend (last 5 periods)
        if len(self.df) >= 5:
            recent_volumes = self.df['volume'].iloc[-5:].values
            volume_trend_slope = np.polyfit(range(5), recent_volumes, 1)[0]
            volume_trend_direction = 'INCREASING' if volume_trend_slope > 0 else 'DECREASING'

            # Calculate percentage change
            volume_change_pct = ((recent_volumes[-1] - recent_volumes[0]) / recent_volumes[0] * 100) if recent_volumes[0] > 0 else 0
        else:
            volume_trend_direction = 'UNKNOWN'
            volume_change_pct = 0

        # 3. Volume Divergence (price vs volume direction mismatch)
        if len(self.df) >= 10:
            # Recent price trend
            recent_prices = self.df['price'].iloc[-10:].values
            price_trend_slope = np.polyfit(range(10), recent_prices, 1)[0]
            price_direction = 'UP' if price_trend_slope > 0 else 'DOWN'

            # Recent volume trend (last 10 periods)
            recent_vol = self.df['volume'].iloc[-10:].values
            vol_trend_slope = np.polyfit(range(10), recent_vol, 1)[0]
            vol_direction = 'UP' if vol_trend_slope > 0 else 'DOWN'

            # Check for divergence
            if price_direction == 'UP' and vol_direction == 'DOWN':
                divergence_signal = 'NEGATIVE_DIVERGENCE'
                divergence_recommendation = '⚠️ WARNING: Price rising but volume declining - weak rally, possible reversal'
                divergence_type = 'BEARISH'
            elif price_direction == 'DOWN' and vol_direction == 'UP':
                divergence_signal = 'NEGATIVE_DIVERGENCE'
                divergence_recommendation = '⚠️ WARNING: Price falling with increasing volume - strong selling pressure'
                divergence_type = 'BEARISH'
            elif price_direction == 'UP' and vol_direction == 'UP':
                divergence_signal = 'POSITIVE_CONFIRMATION'
                divergence_recommendation = '✅ STRONG: Price rising with increasing volume - healthy uptrend'
                divergence_type = 'BULLISH'
            elif price_direction == 'DOWN' and vol_direction == 'DOWN':
                divergence_signal = 'WEAK_MOVE'
                divergence_recommendation = 'Price falling with decreasing volume - selling pressure weakening'
                divergence_type = 'NEUTRAL'
            else:
                divergence_signal = 'NO_DIVERGENCE'
                divergence_recommendation = 'Price and volume aligned'
                divergence_type = 'NEUTRAL'
        else:
            divergence_signal = 'UNKNOWN'
            divergence_recommendation = 'Insufficient data for divergence analysis'
            divergence_type = 'NEUTRAL'

        # 4. Volume Spike Detection (last 3 periods)
        if len(self.df) >= 3:
            last_3_volumes = self.df['volume'].iloc[-3:].values
            avg_3 = np.mean(last_3_volumes[:-1])  # Average of previous 2
            spike_ratio = last_3_volumes[-1] / avg_3 if avg_3 > 0 else 1

            if spike_ratio > 3:
                spike_detected = True
                spike_magnitude = 'EXTREME'
            elif spike_ratio > 2:
                spike_detected = True
                spike_magnitude = 'SIGNIFICANT'
            else:
                spike_detected = False
                spike_magnitude = 'NONE'
        else:
            spike_detected = False
            spike_magnitude = 'UNKNOWN'

        # 5. Volume Confirmation Score (0-100)
        confirmation_score = 0

        # Add points for volume level
        if volume_ratio > 1.5:
            confirmation_score += 30
        elif volume_ratio > 1:
            confirmation_score += 15

        # Add points for volume trend
        if volume_trend_direction == 'INCREASING':
            confirmation_score += 25

        # Add points for positive confirmation
        if divergence_type == 'BULLISH':
            confirmation_score += 45
        elif divergence_type == 'NEUTRAL':
            confirmation_score += 20

        # Reduce for negative divergence
        if divergence_type == 'BEARISH':
            confirmation_score = max(0, confirmation_score - 30)

        # 6. Overall Volume Assessment
        if confirmation_score >= 70:
            overall_assessment = 'STRONG_CONFIRMATION'
        elif confirmation_score >= 50:
            overall_assessment = 'MODERATE_CONFIRMATION'
        elif confirmation_score >= 30:
            overall_assessment = 'WEAK_CONFIRMATION'
        else:
            overall_assessment = 'NO_CONFIRMATION'

        return {
            # Basic metrics
            'current_volume': current_volume,
            'avg_volume_20': avg_volume_20,
            'avg_volume_50': avg_volume_50,
            'volume_ratio': volume_ratio,

            # Volume level
            'signal': volume_signal,
            'recommendation': volume_recommendation,

            # Volume trend
            'trend_direction': volume_trend_direction,
            'trend_change_pct': volume_change_pct,

            # Volume divergence
            'divergence_signal': divergence_signal,
            'divergence_type': divergence_type,
            'divergence_recommendation': divergence_recommendation,

            # Volume spikes
            'spike_detected': spike_detected,
            'spike_magnitude': spike_magnitude,

            # Overall assessment
            'confirmation_score': confirmation_score,
            'overall_assessment': overall_assessment
        }

    def calculate_stochastic(self, k_period: int = 14, d_period: int = 3) -> Dict:
        """
        Calculate Stochastic Oscillator (%K and %D)

        Stochastic shows where the current price is relative to the high/low range
        over a given period. Values range from 0-100.

        Args:
            k_period: Period for %K calculation (default 14)
            d_period: Period for %D (SMA of %K) (default 3)

        Returns:
            Dict with %K, %D, signal, and recommendation
        """
        if len(self.df) < k_period + d_period:
            return {'error': f'Insufficient data for Stochastic (need {k_period + d_period}+ data points)'}

        # Calculate %K
        low_min = self.df['price'].rolling(window=k_period).min()
        high_max = self.df['price'].rolling(window=k_period).max()

        self.df['stoch_k'] = 100 * (self.df['price'] - low_min) / (high_max - low_min)

        # Calculate %D (SMA of %K)
        self.df['stoch_d'] = self.df['stoch_k'].rolling(window=d_period).mean()

        k_value = self.df['stoch_k'].iloc[-1]
        d_value = self.df['stoch_d'].iloc[-1]

        # Determine signal
        if k_value > 80:
            signal = 'OVERBOUGHT'
            recommendation = 'Overbought - price may be due for pullback'
            trade_signal = 'BEARISH'
        elif k_value < 20:
            signal = 'OVERSOLD'
            recommendation = 'Oversold - price may be due for bounce'
            trade_signal = 'BULLISH'
        elif k_value > d_value and k_value < 50:
            signal = 'BULLISH_CROSS'
            recommendation = '%K crossed above %D in oversold zone - bullish signal'
            trade_signal = 'BULLISH'
        elif k_value < d_value and k_value > 50:
            signal = 'BEARISH_CROSS'
            recommendation = '%K crossed below %D in overbought zone - bearish signal'
            trade_signal = 'BEARISH'
        else:
            signal = 'NEUTRAL'
            recommendation = 'No strong signal'
            trade_signal = 'NEUTRAL'

        return {
            'k': k_value,
            'd': d_value,
            'signal': signal,
            'trade_signal': trade_signal,
            'recommendation': recommendation,
            'overbought': k_value > 80,
            'oversold': k_value < 20
        }

    def calculate_adx(self, period: int = 14) -> Dict:
        """
        Calculate ADX (Average Directional Index)

        ADX measures trend strength from 0-100. Does NOT indicate direction,
        only how strong the trend is.

        Args:
            period: Period for ADX calculation (default 14)

        Returns:
            Dict with ADX value, strength assessment, and recommendation
        """
        if len(self.df) < period * 2:
            return {'error': f'Insufficient data for ADX (need {period * 2}+ data points)'}

        # We need high/low data, but we only have price
        # For crypto, we'll estimate using price volatility
        # This is a simplified ADX calculation

        # Calculate True Range (TR) using price differences as proxy
        self.df['tr'] = abs(self.df['price'] - self.df['price'].shift(1))

        # Calculate +DM and -DM
        self.df['up_move'] = self.df['price'] - self.df['price'].shift(1)
        self.df['down_move'] = self.df['price'].shift(1) - self.df['price']

        self.df['plus_dm'] = np.where((self.df['up_move'] > self.df['down_move']) & (self.df['up_move'] > 0), self.df['up_move'], 0)
        self.df['minus_dm'] = np.where((self.df['down_move'] > self.df['up_move']) & (self.df['down_move'] > 0), self.df['down_move'], 0)

        # Smooth with Wilder's moving average
        self.df['tr_smooth'] = self.df['tr'].rolling(window=period).mean()
        self.df['plus_di'] = 100 * (self.df['plus_dm'].rolling(window=period).mean() / self.df['tr_smooth'])
        self.df['minus_di'] = 100 * (self.df['minus_dm'].rolling(window=period).mean() / self.df['tr_smooth'])

        # Calculate DX and ADX
        self.df['dx'] = 100 * abs(self.df['plus_di'] - self.df['minus_di']) / (self.df['plus_di'] + self.df['minus_di'])
        self.df['adx'] = self.df['dx'].rolling(window=period).mean()

        adx_value = self.df['adx'].iloc[-1]

        # Determine trend strength
        if adx_value > 50:
            strength = 'VERY_STRONG'
            recommendation = 'Very strong trend - high conviction trades'
        elif adx_value > 25:
            strength = 'STRONG'
            recommendation = 'Strong trend - good for trend-following'
        elif adx_value > 20:
            strength = 'MODERATE'
            recommendation = 'Moderate trend - some directionality'
        else:
            strength = 'WEAK'
            recommendation = 'Weak trend - choppy/ranging market, avoid trend trades'

        return {
            'value': adx_value,
            'strength': strength,
            'recommendation': recommendation,
            'trending': adx_value > 25
        }

    def calculate_atr(self, period: int = 14) -> Dict:
        """
        Calculate ATR (Average True Range)

        ATR measures volatility. Higher ATR = higher volatility.
        Used for setting stop-losses and position sizing.

        Args:
            period: Period for ATR calculation (default 14)

        Returns:
            Dict with ATR value, volatility assessment, and recommendations
        """
        if len(self.df) < period + 1:
            return {'error': f'Insufficient data for ATR (need {period + 1}+ data points)'}

        # Calculate True Range (using price differences as proxy)
        self.df['tr_atr'] = abs(self.df['price'] - self.df['price'].shift(1))

        # Calculate ATR (moving average of TR)
        self.df['atr'] = self.df['tr_atr'].rolling(window=period).mean()

        atr_value = self.df['atr'].iloc[-1]
        current_price = self.df['price'].iloc[-1]

        # ATR as percentage of price
        atr_pct = (atr_value / current_price) * 100

        # Determine volatility level
        if atr_pct > 5:
            volatility = 'VERY_HIGH'
            recommendation = 'Very high volatility - use wider stops, smaller positions'
        elif atr_pct > 3:
            volatility = 'HIGH'
            recommendation = 'High volatility - expect larger price swings'
        elif atr_pct > 1.5:
            volatility = 'MODERATE'
            recommendation = 'Moderate volatility - normal market conditions'
        else:
            volatility = 'LOW'
            recommendation = 'Low volatility - tight range, potential breakout coming'

        # Suggested stop-loss distance (2x ATR is common)
        suggested_stop_distance = atr_value * 2
        suggested_stop_pct = (suggested_stop_distance / current_price) * 100

        return {
            'value': atr_value,
            'atr_pct': atr_pct,
            'volatility': volatility,
            'recommendation': recommendation,
            'suggested_stop_distance': suggested_stop_distance,
            'suggested_stop_pct': suggested_stop_pct
        }

    def calculate_obv(self) -> Dict:
        """
        Calculate OBV (On-Balance Volume)

        OBV is a cumulative volume indicator that adds volume on up days
        and subtracts volume on down days. Shows buying/selling pressure.

        Returns:
            Dict with OBV value, trend, and recommendation
        """
        if 'volume' not in self.df.columns:
            return {'error': 'Volume data not available for OBV'}

        if len(self.df) < 20:
            return {'error': 'Insufficient data for OBV (need 20+ data points)'}

        # Calculate OBV
        self.df['obv'] = 0
        self.df['price_change'] = self.df['price'].diff()

        obv_values = [0]
        for i in range(1, len(self.df)):
            if self.df['price_change'].iloc[i] > 0:
                obv_values.append(obv_values[-1] + self.df['volume'].iloc[i])
            elif self.df['price_change'].iloc[i] < 0:
                obv_values.append(obv_values[-1] - self.df['volume'].iloc[i])
            else:
                obv_values.append(obv_values[-1])

        self.df['obv'] = obv_values

        # Calculate OBV SMA for trend
        self.df['obv_sma'] = self.df['obv'].rolling(window=20).mean()

        current_obv = self.df['obv'].iloc[-1]
        obv_sma = self.df['obv_sma'].iloc[-1]

        # Determine OBV trend (last 10 periods)
        if len(self.df) >= 10:
            obv_recent = self.df['obv'].iloc[-10:].values
            obv_trend_slope = np.polyfit(range(10), obv_recent, 1)[0]
            trend_direction = 'RISING' if obv_trend_slope > 0 else 'FALLING'
        else:
            trend_direction = 'UNKNOWN'

        # Determine signal
        if current_obv > obv_sma and trend_direction == 'RISING':
            signal = 'BULLISH'
            recommendation = 'OBV rising - accumulation, buying pressure increasing'
        elif current_obv < obv_sma and trend_direction == 'FALLING':
            signal = 'BEARISH'
            recommendation = 'OBV falling - distribution, selling pressure increasing'
        else:
            signal = 'NEUTRAL'
            recommendation = 'OBV trend unclear'

        # Check for divergence with price
        if len(self.df) >= 10:
            price_recent = self.df['price'].iloc[-10:].values
            price_trend_slope = np.polyfit(range(10), price_recent, 1)[0]
            price_direction = 'UP' if price_trend_slope > 0 else 'DOWN'

            if price_direction == 'UP' and trend_direction == 'FALLING':
                divergence = 'NEGATIVE'
                divergence_warning = '⚠️ Price rising but OBV falling - weak rally!'
            elif price_direction == 'DOWN' and trend_direction == 'RISING':
                divergence = 'POSITIVE'
                divergence_warning = '✅ Price falling but OBV rising - potential reversal!'
            else:
                divergence = 'NONE'
                divergence_warning = ''
        else:
            divergence = 'UNKNOWN'
            divergence_warning = ''

        return {
            'value': current_obv,
            'sma': obv_sma,
            'trend': trend_direction,
            'signal': signal,
            'recommendation': recommendation,
            'divergence': divergence,
            'divergence_warning': divergence_warning
        }

    def detect_price_patterns(self) -> Dict:
        """
        Detect price movement patterns (simplified candlestick-style patterns)

        Since we have price data but not full OHLC, we'll detect patterns
        based on consecutive price movements and reversals.

        Returns:
            Dict with detected patterns and signals
        """
        if len(self.df) < 5:
            return {'error': 'Insufficient data for pattern detection (need 5+ data points)'}

        patterns = []
        current_price = self.df['price'].iloc[-1]

        # Calculate price changes
        self.df['pct_change'] = self.df['price'].pct_change() * 100

        # Get recent price changes (last 5 periods)
        recent_changes = self.df['pct_change'].iloc[-5:].values

        # 1. Strong Reversal Detection (Hammer/Shooting Star equivalent)
        last_change = recent_changes[-1]
        prev_change = recent_changes[-2]

        if abs(last_change) > 3 and abs(prev_change) > 3 and np.sign(last_change) != np.sign(prev_change):
            if last_change > 0:
                patterns.append({
                    'name': 'BULLISH_REVERSAL',
                    'description': 'Strong bullish reversal after decline',
                    'signal': 'BULLISH',
                    'strength': 'STRONG'
                })
            else:
                patterns.append({
                    'name': 'BEARISH_REVERSAL',
                    'description': 'Strong bearish reversal after rise',
                    'signal': 'BEARISH',
                    'strength': 'STRONG'
                })

        # 2. Consecutive Moves (Momentum Pattern)
        consecutive_up = 0
        consecutive_down = 0
        for change in recent_changes[-4:]:
            if change > 0:
                consecutive_up += 1
                consecutive_down = 0
            elif change < 0:
                consecutive_down += 1
                consecutive_up = 0

        if consecutive_up >= 3:
            patterns.append({
                'name': 'STRONG_UPTREND',
                'description': f'{consecutive_up} consecutive up days - strong momentum',
                'signal': 'BULLISH',
                'strength': 'MODERATE'
            })
        elif consecutive_down >= 3:
            patterns.append({
                'name': 'STRONG_DOWNTREND',
                'description': f'{consecutive_down} consecutive down days - strong momentum',
                'signal': 'BEARISH',
                'strength': 'MODERATE'
            })

        # 3. Exhaustion Pattern (Many consecutive moves may reverse)
        if consecutive_up >= 5:
            patterns.append({
                'name': 'EXHAUSTION_WARNING',
                'description': 'Extended uptrend - potential exhaustion/reversal',
                'signal': 'CAUTION',
                'strength': 'MODERATE'
            })
        elif consecutive_down >= 5:
            patterns.append({
                'name': 'OVERSOLD_BOUNCE',
                'description': 'Extended downtrend - potential bounce coming',
                'signal': 'WATCH',
                'strength': 'MODERATE'
            })

        # 4. Doji-like Pattern (very small change after volatility)
        if abs(last_change) < 0.5 and abs(prev_change) > 2:
            patterns.append({
                'name': 'INDECISION',
                'description': 'Small move after large move - market indecision',
                'signal': 'NEUTRAL',
                'strength': 'WEAK'
            })

        # Overall pattern assessment
        if patterns:
            # Count bullish/bearish signals
            bullish_count = sum(1 for p in patterns if p['signal'] == 'BULLISH')
            bearish_count = sum(1 for p in patterns if p['signal'] == 'BEARISH')

            if bullish_count > bearish_count:
                overall_signal = 'BULLISH'
            elif bearish_count > bullish_count:
                overall_signal = 'BEARISH'
            else:
                overall_signal = 'NEUTRAL'
        else:
            overall_signal = 'NONE'

        return {
            'patterns_detected': patterns,
            'pattern_count': len(patterns),
            'overall_signal': overall_signal
        }

    def detect_chart_patterns(self) -> Dict:
        """
        Detect chart patterns (double top/bottom, triangles, channels)

        Uses price data to identify classical chart patterns.

        Returns:
            Dict with detected chart patterns
        """
        if len(self.df) < 20:
            return {'error': 'Insufficient data for chart pattern detection (need 20+ data points)'}

        patterns = []
        prices = self.df['price'].values
        recent_prices = prices[-20:]  # Last 20 periods

        # Find local maxima and minima
        local_max_indices = []
        local_min_indices = []

        for i in range(1, len(recent_prices) - 1):
            if recent_prices[i] > recent_prices[i-1] and recent_prices[i] > recent_prices[i+1]:
                local_max_indices.append(i)
            if recent_prices[i] < recent_prices[i-1] and recent_prices[i] < recent_prices[i+1]:
                local_min_indices.append(i)

        # 1. Double Top Detection
        if len(local_max_indices) >= 2:
            last_two_highs = [recent_prices[i] for i in local_max_indices[-2:]]
            if abs(last_two_highs[1] - last_two_highs[0]) / last_two_highs[0] < 0.02:  # Within 2%
                patterns.append({
                    'name': 'DOUBLE_TOP',
                    'description': 'Double top pattern - bearish reversal',
                    'signal': 'BEARISH',
                    'strength': 'STRONG',
                    'price_level': max(last_two_highs)
                })

        # 2. Double Bottom Detection
        if len(local_min_indices) >= 2:
            last_two_lows = [recent_prices[i] for i in local_min_indices[-2:]]
            if abs(last_two_lows[1] - last_two_lows[0]) / last_two_lows[0] < 0.02:  # Within 2%
                patterns.append({
                    'name': 'DOUBLE_BOTTOM',
                    'description': 'Double bottom pattern - bullish reversal',
                    'signal': 'BULLISH',
                    'strength': 'STRONG',
                    'price_level': min(last_two_lows)
                })

        # 3. Triangle/Consolidation Detection (converging highs and lows)
        if len(local_max_indices) >= 2 and len(local_min_indices) >= 2:
            high_range = max(recent_prices) - min(recent_prices)
            recent_range = recent_prices[-5:].max() - recent_prices[-5:].min()

            if recent_range < high_range * 0.5:  # Range compressed by 50%
                patterns.append({
                    'name': 'CONSOLIDATION',
                    'description': 'Price consolidating - potential breakout imminent',
                    'signal': 'WATCH',
                    'strength': 'MODERATE'
                })

        # 4. Breakout Detection
        ma_20 = np.mean(recent_prices)
        std_20 = np.std(recent_prices)
        current_price = prices[-1]

        if current_price > ma_20 + (1.5 * std_20):
            patterns.append({
                'name': 'UPSIDE_BREAKOUT',
                'description': 'Price breaking out above resistance',
                'signal': 'BULLISH',
                'strength': 'STRONG'
            })
        elif current_price < ma_20 - (1.5 * std_20):
            patterns.append({
                'name': 'DOWNSIDE_BREAKDOWN',
                'description': 'Price breaking down below support',
                'signal': 'BEARISH',
                'strength': 'STRONG'
            })

        # 5. Trend Channel Detection
        if len(self.df) >= 10:
            x = np.arange(10)
            y = prices[-10:]
            slope, intercept = np.polyfit(x, y, 1)

            # Calculate deviation from trend line
            trend_line = slope * x + intercept
            deviations = y - trend_line
            avg_deviation = np.mean(np.abs(deviations))

            if avg_deviation / np.mean(y) < 0.02:  # Tight channel (< 2% deviation)
                if slope > 0:
                    patterns.append({
                        'name': 'RISING_CHANNEL',
                        'description': 'Clean uptrend channel - trend-following opportunity',
                        'signal': 'BULLISH',
                        'strength': 'MODERATE'
                    })
                else:
                    patterns.append({
                        'name': 'FALLING_CHANNEL',
                        'description': 'Clean downtrend channel - wait for reversal',
                        'signal': 'BEARISH',
                        'strength': 'MODERATE'
                    })

        # Overall assessment
        if patterns:
            bullish_count = sum(1 for p in patterns if p['signal'] == 'BULLISH')
            bearish_count = sum(1 for p in patterns if p['signal'] == 'BEARISH')

            if bullish_count > bearish_count:
                overall_signal = 'BULLISH'
            elif bearish_count > bullish_count:
                overall_signal = 'BEARISH'
            else:
                overall_signal = 'MIXED'
        else:
            overall_signal = 'NONE'

        return {
            'patterns_detected': patterns,
            'pattern_count': len(patterns),
            'overall_signal': overall_signal
        }

    def generate_signals(self, indicators: Dict) -> Dict:
        """
        Generate overall trading signals based on all indicators

        Returns:
            Overall signal and confidence level
        """
        signals = {
            'bullish': 0,
            'bearish': 0,
            'neutral': 0
        }

        # RSI signals
        if 'rsi' in indicators and 'signal' in indicators['rsi']:
            rsi_signal = indicators['rsi']['signal']
            if rsi_signal == 'OVERSOLD':
                signals['bullish'] += 2  # Strong buy signal
            elif rsi_signal in ['BULLISH', 'OVERBOUGHT']:
                signals['bullish'] += 1
            elif rsi_signal == 'OVERBOUGHT':
                signals['bearish'] += 2  # Strong sell signal
            elif rsi_signal in ['BEARISH']:
                signals['bearish'] += 1
            else:
                signals['neutral'] += 1

        # MACD signals
        if 'macd' in indicators and 'trade_signal' in indicators['macd']:
            macd_signal = indicators['macd']['trade_signal']
            if macd_signal == 'BULLISH_CROSSOVER':
                signals['bullish'] += 2
            elif macd_signal == 'BULLISH':
                signals['bullish'] += 1
            elif macd_signal == 'BEARISH_CROSSOVER':
                signals['bearish'] += 2
            elif macd_signal == 'BEARISH':
                signals['bearish'] += 1
            else:
                signals['neutral'] += 1

        # Bollinger Bands signals
        if 'bollinger' in indicators and 'signal' in indicators['bollinger']:
            bb_signal = indicators['bollinger']['signal']
            if bb_signal == 'OVERSOLD':
                signals['bullish'] += 2
            elif bb_signal == 'BULLISH':
                signals['bullish'] += 1
            elif bb_signal == 'OVERBOUGHT':
                signals['bearish'] += 2
            elif bb_signal == 'BEARISH':
                signals['bearish'] += 1
            else:
                signals['neutral'] += 1

        # SMA signals
        if 'sma' in indicators:
            if indicators['sma'].get('golden_cross'):
                signals['bullish'] += 3  # Very strong signal
            elif indicators['sma'].get('death_cross'):
                signals['bearish'] += 3  # Very strong signal
            elif indicators['sma'].get('cross_signal') == 'BULLISH':
                signals['bullish'] += 1
            elif indicators['sma'].get('cross_signal') == 'BEARISH':
                signals['bearish'] += 1

        # Volume signals
        if 'volume_analysis' in indicators and 'error' not in indicators['volume_analysis']:
            vol = indicators['volume_analysis']

            # Volume confirmation adds weight to existing signals
            if vol.get('divergence_type') == 'BULLISH':
                signals['bullish'] += 2  # Strong confirmation
            elif vol.get('divergence_type') == 'BEARISH':
                signals['bearish'] += 2  # Negative divergence warning

            # High volume adds conviction
            if vol.get('signal') in ['VERY_HIGH_VOLUME', 'EXTREME_VOLUME']:
                # Don't add signal, but note high conviction
                pass

            # Volume spike detection
            if vol.get('spike_detected'):
                # Spikes add urgency but not direction
                signals['neutral'] += 1

        # Stochastic signals
        if 'stochastic' in indicators and 'error' not in indicators['stochastic']:
            stoch = indicators['stochastic']
            if stoch.get('signal') in ['OVERSOLD', 'BULLISH_CROSS']:
                signals['bullish'] += 1
            elif stoch.get('signal') in ['OVERBOUGHT', 'BEARISH_CROSS']:
                signals['bearish'] += 1
            else:
                signals['neutral'] += 1

        # ADX signals (trend strength - doesn't indicate direction)
        # ADX is used more for context than direction

        # OBV signals
        if 'obv' in indicators and 'error' not in indicators['obv']:
            obv = indicators['obv']
            if obv.get('signal') == 'BULLISH':
                signals['bullish'] += 1
            elif obv.get('signal') == 'BEARISH':
                signals['bearish'] += 1

            # OBV divergence is important
            if obv.get('divergence') == 'POSITIVE':
                signals['bullish'] += 2
            elif obv.get('divergence') == 'NEGATIVE':
                signals['bearish'] += 2

        # Price Pattern signals
        if 'price_patterns' in indicators and 'error' not in indicators['price_patterns']:
            pp = indicators['price_patterns']
            if pp.get('overall_signal') == 'BULLISH':
                signals['bullish'] += 1
            elif pp.get('overall_signal') == 'BEARISH':
                signals['bearish'] += 1

        # Chart Pattern signals
        if 'chart_patterns' in indicators and 'error' not in indicators['chart_patterns']:
            cp = indicators['chart_patterns']
            # Chart patterns are important, so give them more weight
            if cp.get('overall_signal') == 'BULLISH':
                signals['bullish'] += 2
            elif cp.get('overall_signal') == 'BEARISH':
                signals['bearish'] += 2

        # Calculate overall signal
        total_signals = signals['bullish'] + signals['bearish'] + signals['neutral']

        if total_signals == 0:
            return {'overall': 'NEUTRAL', 'confidence': 0, 'breakdown': signals}

        bullish_pct = (signals['bullish'] / total_signals) * 100
        bearish_pct = (signals['bearish'] / total_signals) * 100

        if bullish_pct > 60:
            overall = 'BULLISH'
            confidence = bullish_pct
        elif bearish_pct > 60:
            overall = 'BEARISH'
            confidence = bearish_pct
        else:
            overall = 'NEUTRAL'
            confidence = 50

        return {
            'overall': overall,
            'confidence': round(confidence, 1),
            'breakdown': signals,
            'bullish_pct': round(bullish_pct, 1),
            'bearish_pct': round(bearish_pct, 1)
        }

    def get_dataframe_with_indicators(self) -> pd.DataFrame:
        """Return the DataFrame with all calculated indicators"""
        return self.df
