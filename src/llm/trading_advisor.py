"""
AI Trading Advisor
Provides buy/sell recommendations with risk management
"""

import os
from typing import Dict, Optional
from openai import OpenAI


class TradingAdvisor:
    """Generate trading recommendations using LLM"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize trading advisor

        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4o for better reasoning)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required.")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def get_trading_recommendation(
        self,
        symbol: str,
        current_price: float,
        market_data: Dict,
        sentiment_score: float,
        news_summary: str,
        risk_factors: list,
        technical_indicators: Optional[Dict] = None,
        market_context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate comprehensive trading recommendation

        Args:
            symbol: Crypto symbol (BTC, ETH)
            current_price: Current price in USD
            market_data: Market metrics dict
            sentiment_score: Overall sentiment score (-10 to +10)
            news_summary: Summary of recent news
            risk_factors: List of identified risk factors
            technical_indicators: Technical analysis indicators (RSI, MACD, etc.)
            market_context: Market context (timeframes, correlations, regime)

        Returns:
            Dict with recommendation, confidence, entry/exit levels
        """

        # Build context for LLM
        context = f"""You are an expert cryptocurrency trading advisor. Analyze the following data for {symbol} and provide a trading recommendation.

CURRENT MARKET DATA:
- Current Price: ${current_price:,.2f}
- 24h Change: {market_data.get('price_change_percentage_24h', 0):.2f}%
- 7d Change: {market_data.get('price_change_percentage_7d', 0):.2f}%
- 30d Change: {market_data.get('price_change_percentage_30d', 0):.2f}%
- Market Cap: ${market_data.get('market_cap', 0)/1e9:.2f}B
- 24h Volume: ${market_data.get('total_volume', 0)/1e9:.2f}B
- Distance from ATH: {((current_price - market_data.get('ath', current_price)) / market_data.get('ath', current_price) * 100):.1f}%
- Distance from ATL: {((current_price - market_data.get('atl', current_price)) / market_data.get('atl', current_price) * 100):.1f}%

NEWS SENTIMENT:
- Sentiment Score: {sentiment_score:.1f}/10 ({self._get_sentiment_label(sentiment_score)})
- Recent News: {news_summary}

TECHNICAL INDICATORS:
{self._format_technical_indicators(technical_indicators) if technical_indicators else '- No technical indicators available'}

MARKET CONTEXT:
{self._format_market_context(market_context) if market_context else '- No market context available'}

RISK FACTORS:
{chr(10).join(['- ' + factor for factor in risk_factors]) if risk_factors else '- None identified'}

Based on this comprehensive analysis, provide:

1. RECOMMENDATION: Should I BUY, SELL, or HOLD? (Choose one)
2. CONFIDENCE: Your confidence level (1-100%)
3. REASONING: Brief explanation (2-3 sentences)
4. ENTRY STRATEGY: If BUY, suggest entry price levels
5. STOP LOSS: Recommended stop-loss percentage and price
6. TAKE PROFIT: Suggested profit-taking levels
7. POSITION SIZE: Recommended portfolio allocation (%)
8. TIME HORIZON: Suggested holding period
9. KEY RISKS: Top 3 risks to watch
10. INVALIDATION: What would invalidate this recommendation?

IMPORTANT GUIDELINES:
- Be conservative and risk-aware
- Consider both technical (price action) and fundamental (news/sentiment) factors
- Stop-loss should be based on volatility and support levels
- For {symbol}, typical volatility is {'10-15%' if symbol == 'BTC' else '15-25%'} daily
- Recommend smaller position sizes when risks are elevated
- Always prioritize capital preservation

Respond in this EXACT format:
RECOMMENDATION: [BUY/SELL/HOLD]
CONFIDENCE: [number]%
REASONING: [text]
ENTRY_PRICE: $[price] (or "Current Market" if HOLD/SELL)
STOP_LOSS: [percentage]% ($[price])
TAKE_PROFIT_1: $[price] (target 1)
TAKE_PROFIT_2: $[price] (target 2)
POSITION_SIZE: [percentage]%
TIME_HORIZON: [short-term/medium-term/long-term]
KEY_RISKS: [risk 1]; [risk 2]; [risk 3]
INVALIDATION: [condition]
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional cryptocurrency trading advisor with expertise in technical analysis, risk management, and market sentiment. Provide conservative, well-reasoned trading advice."
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent advice
                max_tokens=1000
            )

            result_text = response.choices[0].message.content.strip()

            # Parse the structured response
            parsed = self._parse_recommendation(result_text, current_price)

            # Add metadata
            parsed['model'] = self.model
            parsed['raw_response'] = result_text

            return parsed

        except Exception as e:
            print(f"Error getting trading recommendation: {e}")
            return {
                'recommendation': 'HOLD',
                'confidence': 0,
                'reasoning': f'Error generating recommendation: {str(e)}',
                'entry_price': current_price,
                'stop_loss_pct': 10.0,
                'stop_loss_price': current_price * 0.90,
                'error': True
            }

    def _parse_recommendation(self, response: str, current_price: float) -> Dict:
        """Parse LLM response into structured format"""
        lines = response.split('\n')
        parsed = {}

        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()

                if key == 'recommendation':
                    parsed['recommendation'] = value.upper()
                elif key == 'confidence':
                    parsed['confidence'] = int(value.replace('%', '').strip())
                elif key == 'reasoning':
                    parsed['reasoning'] = value
                elif key == 'entry_price':
                    parsed['entry_price'] = self._extract_price(value, current_price)
                elif key == 'stop_loss':
                    # Extract percentage and price
                    if '%' in value and '$' in value:
                        pct_part = value.split('%')[0].strip()
                        price_part = value.split('$')[1].split(')')[0].strip()
                        parsed['stop_loss_pct'] = float(pct_part)
                        parsed['stop_loss_price'] = float(price_part.replace(',', ''))
                    else:
                        parsed['stop_loss_pct'] = 10.0
                        parsed['stop_loss_price'] = current_price * 0.90
                elif key == 'take_profit_1':
                    parsed['take_profit_1'] = self._extract_price(value, current_price)
                elif key == 'take_profit_2':
                    parsed['take_profit_2'] = self._extract_price(value, current_price)
                elif key == 'position_size':
                    parsed['position_size'] = float(value.replace('%', '').strip())
                elif key == 'time_horizon':
                    parsed['time_horizon'] = value
                elif key == 'key_risks':
                    parsed['key_risks'] = [r.strip() for r in value.split(';')]
                elif key == 'invalidation':
                    parsed['invalidation'] = value

        return parsed

    def _extract_price(self, text: str, default: float) -> float:
        """Extract price from text"""
        try:
            # Remove $ and commas, extract number
            price_str = text.replace('$', '').replace(',', '').split('(')[0].strip()
            if 'current' in price_str.lower() or 'market' in price_str.lower():
                return default
            return float(price_str)
        except:
            return default

    def _get_sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score >= 7:
            return "Very Bullish"
        elif score >= 3:
            return "Bullish"
        elif score <= -7:
            return "Very Bearish"
        elif score <= -3:
            return "Bearish"
        else:
            return "Neutral"

    def _format_technical_indicators(self, indicators: Dict) -> str:
        """Format technical indicators for LLM context"""
        if not indicators:
            return "- No technical indicators available"

        lines = []

        # Overall signal
        if 'signals' in indicators:
            signals = indicators['signals']
            lines.append(f"- Overall Technical Signal: {signals.get('overall', 'NEUTRAL')} ({signals.get('confidence', 0):.0f}% confidence)")
            lines.append(f"  Signal Breakdown: {signals.get('bullish', 0)} bullish, {signals.get('bearish', 0)} bearish, {signals.get('neutral', 0)} neutral")

        # RSI
        if 'rsi' in indicators and 'value' in indicators['rsi']:
            rsi = indicators['rsi']
            lines.append(f"- RSI (14): {rsi['value']:.1f} - {rsi['signal']} ({rsi['recommendation']})")

        # MACD
        if 'macd' in indicators and 'macd' in indicators['macd']:
            macd = indicators['macd']
            lines.append(f"- MACD: {macd['macd']:.2f}, Signal: {macd['signal']:.2f}, Histogram: {macd['histogram']:.2f}")
            lines.append(f"  MACD Signal: {macd['trade_signal']} - {macd['recommendation']}")

        # Bollinger Bands
        if 'bollinger' in indicators and 'current_price' in indicators['bollinger']:
            bb = indicators['bollinger']
            lines.append(f"- Bollinger Bands: Price at {bb['price_position']:.0f}% of band range")
            lines.append(f"  BB Signal: {bb['signal']} - {bb['recommendation']}")
            lines.append(f"  Band Width: {bb['band_width']:.1f}% ({'High Volatility' if bb.get('high_volatility') else 'Normal Volatility'})")

        # Moving Averages
        if 'sma' in indicators:
            sma = indicators['sma']

            # SMA values
            sma_lines = []
            for key, value in sma.items():
                if key.startswith('SMA_') and isinstance(value, dict):
                    period = key.replace('SMA_', '')
                    sma_lines.append(f"SMA-{period}: ${value['value']:,.0f} ({value['signal']})")

            if sma_lines:
                lines.append(f"- Moving Averages: {', '.join(sma_lines)}")

            # Golden/Death Cross
            if sma.get('golden_cross'):
                lines.append(f"  🌟 GOLDEN CROSS DETECTED - SMA 50 crossed above SMA 200 (STRONG BULLISH)")
            elif sma.get('death_cross'):
                lines.append(f"  💀 DEATH CROSS DETECTED - SMA 50 crossed below SMA 200 (STRONG BEARISH)")
            elif 'cross_signal' in sma:
                lines.append(f"  MA Trend: {sma['cross_signal']}")

        # Support/Resistance
        if 'support_resistance' in indicators:
            sr = indicators['support_resistance']
            if 'current_price' in sr:
                lines.append(f"- Support: ${sr['nearest_support']:,.0f} ({sr['distance_to_support_pct']:.1f}% below)")
                lines.append(f"- Resistance: ${sr['nearest_resistance']:,.0f} ({sr['distance_to_resistance_pct']:.1f}% above)")
                lines.append(f"  Position: {sr['recommendation']}")

        # Volume Analysis
        if 'volume_analysis' in indicators and 'error' not in indicators['volume_analysis']:
            vol = indicators['volume_analysis']
            lines.append(f"\n📊 VOLUME ANALYSIS:")
            lines.append(f"- Volume Level: {vol['signal']} (Ratio: {vol['volume_ratio']:.2f}x average)")
            lines.append(f"  {vol['recommendation']}")

            # Volume trend
            if vol['trend_direction'] != 'UNKNOWN':
                trend_emoji = "📈" if vol['trend_direction'] == 'INCREASING' else "📉"
                lines.append(f"- Volume Trend: {trend_emoji} {vol['trend_direction']} ({vol['trend_change_pct']:+.1f}% over last 5 periods)")

            # Volume divergence (CRITICAL for LLM)
            if vol['divergence_signal'] != 'UNKNOWN':
                divergence_emoji = "✅" if vol['divergence_type'] == 'BULLISH' else "⚠️" if vol['divergence_type'] == 'BEARISH' else "➖"
                lines.append(f"- Price/Volume Divergence: {divergence_emoji} {vol['divergence_signal']}")
                lines.append(f"  {vol['divergence_recommendation']}")

            # Volume spikes
            if vol['spike_detected']:
                lines.append(f"- Volume Spike: 🚨 {vol['spike_magnitude']} spike detected - unusual activity!")

            # Overall volume assessment
            lines.append(f"- Volume Confirmation: {vol['overall_assessment']} (Score: {vol['confirmation_score']}/100)")

        # Advanced Indicators
        lines.append(f"\n🔬 ADVANCED INDICATORS:")

        # Stochastic Oscillator
        if 'stochastic' in indicators and 'error' not in indicators['stochastic']:
            stoch = indicators['stochastic']
            lines.append(f"- Stochastic Oscillator: %K={stoch['k']:.1f}, %D={stoch['d']:.1f}")
            lines.append(f"  Signal: {stoch['signal']} - {stoch['recommendation']}")

        # ADX (Trend Strength)
        if 'adx' in indicators and 'error' not in indicators['adx']:
            adx = indicators['adx']
            strength_emoji = "💪" if adx['strength'] in ['STRONG', 'VERY_STRONG'] else "📊"
            lines.append(f"- ADX (Trend Strength): {strength_emoji} {adx['value']:.1f} - {adx['strength']}")
            lines.append(f"  {adx['recommendation']}")

        # ATR (Volatility)
        if 'atr' in indicators and 'error' not in indicators['atr']:
            atr = indicators['atr']
            lines.append(f"- ATR (Volatility): {atr['volatility']} - {atr['atr_pct']:.2f}% of price")
            lines.append(f"  {atr['recommendation']}")
            lines.append(f"  Suggested stop-loss distance: {atr['suggested_stop_pct']:.1f}% (2x ATR)")

        # OBV (On-Balance Volume)
        if 'obv' in indicators and 'error' not in indicators['obv']:
            obv = indicators['obv']
            lines.append(f"- OBV (On-Balance Volume): {obv['trend']} trend - {obv['signal']}")
            lines.append(f"  {obv['recommendation']}")
            if obv.get('divergence_warning'):
                lines.append(f"  {obv['divergence_warning']}")

        # Pattern Recognition
        if ('price_patterns' in indicators and 'error' not in indicators['price_patterns']) or \
           ('chart_patterns' in indicators and 'error' not in indicators['chart_patterns']):
            lines.append(f"\n🔍 PATTERN RECOGNITION:")

            # Price Patterns
            if 'price_patterns' in indicators and 'error' not in indicators['price_patterns']:
                pp = indicators['price_patterns']
                if pp['pattern_count'] > 0:
                    lines.append(f"- Price Patterns Detected: {pp['pattern_count']} ({pp['overall_signal']} signal)")
                    for pattern in pp['patterns_detected'][:3]:  # Show top 3
                        emoji = "📈" if pattern['signal'] == 'BULLISH' else "📉" if pattern['signal'] == 'BEARISH' else "➖"
                        lines.append(f"  {emoji} {pattern['name']}: {pattern['description']}")

            # Chart Patterns
            if 'chart_patterns' in indicators and 'error' not in indicators['chart_patterns']:
                cp = indicators['chart_patterns']
                if cp['pattern_count'] > 0:
                    lines.append(f"- Chart Patterns Detected: {cp['pattern_count']} ({cp['overall_signal']} signal)")
                    for pattern in cp['patterns_detected'][:3]:  # Show top 3
                        emoji = "📈" if pattern['signal'] == 'BULLISH' else "📉" if pattern['signal'] == 'BEARISH' else "⚠️"
                        lines.append(f"  {emoji} {pattern['name']}: {pattern['description']}")

        return '\n'.join(lines) if lines else "- No technical indicators available"

    def _format_market_context(self, market_context: Dict) -> str:
        """Format market context for LLM"""
        if not market_context:
            return "- No market context available"

        lines = []

        # Multi-timeframe analysis
        if 'timeframe_analysis' in market_context:
            tf_analysis = market_context['timeframe_analysis']
            alignment = tf_analysis.get('alignment', {})

            lines.append("\n🕐 MULTI-TIMEFRAME ANALYSIS:")

            # Show alignment first (most important)
            if 'assessment' in alignment and alignment['assessment'] != 'INSUFFICIENT_DATA':
                lines.append(f"- Timeframe Alignment: {alignment['recommendation']}")
                lines.append(f"  Score: {alignment['score']}/100 - {alignment['bullish_timeframes']} bullish, {alignment['bearish_timeframes']} bearish, {alignment['neutral_timeframes']} neutral")

                # Show individual timeframes
                timeframes = tf_analysis.get('timeframes', {})
                for tf_name, tf_data in sorted(timeframes.items()):
                    if 'error' in tf_data:
                        continue

                    signal = tf_data.get('overall_signal', 'NEUTRAL')
                    confidence = tf_data.get('confidence', 0)
                    trend = tf_data.get('trend', 'UNKNOWN')
                    price_change = tf_data.get('price_change_pct', 0)

                    emoji = "📈" if signal == 'BULLISH' else "📉" if signal == 'BEARISH' else "➖"
                    lines.append(f"  {emoji} {tf_name}: {signal} ({confidence:.0f}% confidence) | Trend: {trend} | Change: {price_change:+.1f}%")

        # BTC Correlation
        if 'btc_correlation' in market_context:
            btc_corr = market_context['btc_correlation']

            if 'error' not in btc_corr and 'note' not in btc_corr:
                lines.append("\n₿ BTC CORRELATION:")
                lines.append(f"- {btc_corr['recommendation']}")
                lines.append(f"  Correlation: {btc_corr['correlation']:.2f} ({btc_corr['strength']} {btc_corr['direction']})")
                lines.append(f"  {btc_corr['direction_description']}")

        # Market Regime (Fear & Greed)
        if 'market_regime' in market_context:
            regime = market_context['market_regime']

            if regime.get('regime') != 'UNKNOWN':
                lines.append("\n😱 MARKET REGIME:")
                lines.append(f"- Fear & Greed Index: {regime['fear_greed']}/100 - {regime['sentiment']}")
                lines.append(f"  {regime['recommendation']}")
                lines.append(f"  Position Sizing: {regime['position_sizing']}")
                lines.append(f"  Strategy: {regime['strategy']}")

        return '\n'.join(lines) if lines else "- No market context available"

    def get_risk_reward_analysis(
        self,
        entry_price: float,
        stop_loss_price: float,
        take_profit_price: float
    ) -> Dict:
        """
        Calculate risk/reward ratio

        Args:
            entry_price: Entry price
            stop_loss_price: Stop loss price
            take_profit_price: Take profit price

        Returns:
            Dict with risk/reward metrics
        """
        risk = entry_price - stop_loss_price
        reward = take_profit_price - entry_price

        risk_pct = (risk / entry_price) * 100
        reward_pct = (reward / entry_price) * 100

        rr_ratio = reward / risk if risk > 0 else 0

        return {
            'risk_amount': risk,
            'reward_amount': reward,
            'risk_pct': risk_pct,
            'reward_pct': reward_pct,
            'risk_reward_ratio': rr_ratio,
            'is_favorable': rr_ratio >= 2.0  # At least 2:1 RR is favorable
        }
