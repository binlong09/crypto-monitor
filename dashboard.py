"""
Crypto Portfolio Monitor Dashboard
Interactive UI for crypto portfolio tracking with news sentiment analysis
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our modules
from src.data.coingecko_client import CoinGeckoClient
from src.data.news_fetcher import CryptoNewsFetcher
from src.data.defi_tracker import DeFiTracker
from src.monitoring.portfolio_tracker import CryptoPortfolioTracker
from src.monitoring.alert_system import CryptoAlertSystem
from src.llm.sentiment_analyzer import CryptoSentimentAnalyzer
from src.analysis.technical_indicators import TechnicalIndicators
from src.analysis.market_context import MarketContext

# Page configuration
st.set_page_config(
    page_title="Crypto Portfolio Monitor",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #f7931a;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #f7931a;
    }
    .success-metric {
        border-left-color: #28a745;
    }
    .danger-metric {
        border-left-color: #dc3545;
    }
    .bullish-sentiment {
        color: #28a745;
        font-weight: bold;
    }
    .bearish-sentiment {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize clients
@st.cache_resource
def get_clients():
    return {
        'coingecko': CoinGeckoClient(),
        'news': CryptoNewsFetcher(),
        'defi': DeFiTracker(),
        'alerts': CryptoAlertSystem()
    }

clients = get_clients()

# Sidebar navigation
st.sidebar.title("₿ Navigation")
page = st.sidebar.radio(
    "Choose a view:",
    ["🏠 Portfolio Overview", "📊 Market Data", "📰 News & Sentiment", "🔍 Analyze Individual Crypto", "💎 DeFi Positions", "📈 Performance Tracking", "🚨 Alerts", "⚙️ Settings"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Quick Stats")

# Load portfolio stats for sidebar
try:
    tracker = CryptoPortfolioTracker()
    summary = tracker.get_portfolio_summary()
    if summary:
        st.sidebar.metric("Portfolio Value", f"${summary['total_value']:,.2f}")
        if summary.get('daily_change'):
            daily = summary['daily_change']
            st.sidebar.metric("24h Change", f"{daily['pct_change']:+.2f}%",
                            delta=f"${daily['value_change']:+,.2f}")
except Exception as e:
    st.sidebar.info("Upload holdings to see stats")

# ============================================================
# PAGE 1: PORTFOLIO OVERVIEW
# ============================================================
if page == "🏠 Portfolio Overview":
    st.markdown('<p class="main-header">Crypto Portfolio</p>', unsafe_allow_html=True)
    st.markdown("**Track your Bitcoin and Ethereum holdings**")

    st.markdown("---")

    # File upload
    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader("Upload your holdings CSV", type=['csv'])
        st.caption("Expected format: symbol, amount, cost_basis, purchase_date")

    with col2:
        if st.button("Create Sample CSV"):
            tracker = CryptoPortfolioTracker()
            tracker.create_sample_csv("data/sample_holdings.csv")
            st.success("Sample CSV created in data/sample_holdings.csv")

    # Update portfolio button
    if st.button("Update Portfolio", type="primary") or uploaded_file:
        with st.spinner("Fetching latest prices..."):
            tracker = CryptoPortfolioTracker()

            if uploaded_file:
                # Save uploaded file temporarily
                temp_path = f"data/temp_{uploaded_file.name}"
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                portfolio_df = tracker.update_portfolio(temp_path)
            else:
                portfolio_df = tracker.update_portfolio()

            if not portfolio_df.empty:
                st.success("Portfolio updated!")

                # Portfolio summary
                summary = tracker.get_portfolio_summary()

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Value", f"${summary['total_value']:,.2f}")

                with col2:
                    if summary.get('daily_change'):
                        daily = summary['daily_change']
                        st.metric("24h Change", f"{daily['pct_change']:+.2f}%",
                                delta=f"${daily['value_change']:+,.2f}")

                with col3:
                    if summary['total_cost_basis'] > 0:
                        st.metric("Total P&L", f"${summary['total_pnl']:,.2f}",
                                delta=f"{summary['total_pnl_pct']:+.2f}%")

                with col4:
                    st.metric("Holdings", summary['num_holdings'])

                st.markdown("---")

                # Holdings table
                st.subheader("Current Holdings")

                # Format for display
                display_df = portfolio_df.copy()
                display_df['current_price'] = display_df['current_price'].apply(lambda x: f"${x:,.2f}")
                display_df['current_value'] = display_df['current_value'].apply(lambda x: f"${x:,.2f}")
                display_df['profit_loss'] = display_df['profit_loss'].apply(lambda x: f"${x:,.2f}")
                display_df['change_24h'] = display_df['change_24h'].apply(lambda x: f"{x:+.2f}%")
                display_df['weight'] = display_df['weight'].apply(lambda x: f"{x:.1f}%")

                st.dataframe(
                    display_df[['symbol', 'amount', 'current_price', 'current_value',
                              'weight', 'profit_loss', 'profit_loss_pct', 'change_24h']],
                    use_container_width=True
                )

                # Portfolio allocation chart
                st.subheader("Portfolio Allocation")
                fig = px.pie(portfolio_df, values='current_value', names='symbol',
                           title='Portfolio Distribution')
                st.plotly_chart(fig, use_container_width=True)

            else:
                st.error("Failed to update portfolio")

# ============================================================
# PAGE 2: MARKET DATA
# ============================================================
elif page == "📊 Market Data":
    st.markdown('<p class="main-header">Market Data</p>', unsafe_allow_html=True)

    # Crypto selector - accepts any CoinGecko ID or common symbol
    crypto_input = st.text_input(
        "Enter Cryptocurrency",
        value="bitcoin",
        placeholder="e.g., bitcoin, ethereum, cardano, solana",
        help="Enter CoinGecko ID or common symbol (BTC, ETH, ADA, etc.)"
    )

    # Map common symbols to CoinGecko IDs
    symbol_to_id = {
        'BTC': 'bitcoin', 'ETH': 'ethereum', 'ADA': 'cardano', 'SOL': 'solana',
        'XRP': 'ripple', 'DOT': 'polkadot', 'DOGE': 'dogecoin', 'MATIC': 'matic-network',
        'AVAX': 'avalanche-2', 'LINK': 'chainlink', 'UNI': 'uniswap', 'ATOM': 'cosmos',
        'LTC': 'litecoin', 'BCH': 'bitcoin-cash', 'ALGO': 'algorand', 'XLM': 'stellar',
        'VET': 'vechain', 'ICP': 'internet-computer', 'FIL': 'filecoin', 'AAVE': 'aave',
    }

    # Convert input to CoinGecko ID
    crypto_input_upper = crypto_input.upper()
    if crypto_input_upper in symbol_to_id:
        crypto = symbol_to_id[crypto_input_upper]
        symbol = crypto_input_upper
    else:
        crypto = crypto_input.lower().strip()
        symbol = crypto.upper()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Fetch Market Data", type="primary"):
            with st.spinner(f"Fetching {symbol} data..."):
                client = clients['coingecko']

                # Current price
                price_data = client.get_price(crypto)
                if price_data:
                    st.subheader(f"{symbol} Price")

                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.metric("Current Price", f"${price_data['price']:,.2f}")
                    with c2:
                        st.metric("24h Change", f"{price_data['change_24h']:+.2f}%")
                    with c3:
                        st.metric("Market Cap", f"${price_data['market_cap']/1e9:.2f}B")
                    with c4:
                        st.metric("24h Volume", f"${price_data['volume_24h']/1e9:.2f}B")

                # Market data
                market_data = client.get_market_data(crypto)
                if market_data:
                    st.markdown("---")
                    st.subheader("Detailed Market Data")

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("24h High", f"${market_data['high_24h']:,.2f}")
                        st.metric("7d Change", f"{market_data['price_change_percentage_7d']:+.2f}%")
                        st.metric("ATH", f"${market_data['ath']:,.2f}")

                    with c2:
                        st.metric("24h Low", f"${market_data['low_24h']:,.2f}")
                        st.metric("30d Change", f"{market_data['price_change_percentage_30d']:+.2f}%")
                        st.metric("ATL", f"${market_data['atl']:,.2f}")

                    with c3:
                        st.metric("Circulating Supply", f"{market_data['circulating_supply']/1e6:.2f}M")
                        if market_data['max_supply']:
                            st.metric("Max Supply", f"{market_data['max_supply']/1e6:.2f}M")

    with col2:
        days = st.slider("Historical data (days)", 7, 365, 30)
        if st.button("Fetch Historical Prices"):
            with st.spinner("Fetching historical data..."):
                client = clients['coingecko']
                hist_df = client.get_historical_prices(crypto, days)

                if not hist_df.empty:
                    st.subheader(f"{symbol} Price History")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=hist_df['timestamp'], y=hist_df['price'],
                                           mode='lines', name='Price'))
                    fig.update_layout(title=f'{symbol} Price - Last {days} Days',
                                    xaxis_title='Date', yaxis_title='Price (USD)')
                    st.plotly_chart(fig, use_container_width=True)

    # Fear & Greed Index
    st.markdown("---")
    st.subheader("Crypto Fear & Greed Index")

    if st.button("Fetch Fear & Greed Index"):
        client = clients['coingecko']
        fng = client.get_fear_greed_index()

        if fng:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Index Value", fng['value'])
            with col2:
                st.metric("Classification", fng['classification'])
            with col3:
                st.write(f"Updated: {fng['timestamp'].strftime('%Y-%m-%d %H:%M')}")

            # Visual indicator
            if fng['value'] < 25:
                st.error("🔴 Extreme Fear - Potential buying opportunity")
            elif fng['value'] < 45:
                st.warning("🟠 Fear")
            elif fng['value'] < 55:
                st.info("🟡 Neutral")
            elif fng['value'] < 75:
                st.success("🟢 Greed")
            else:
                st.error("🔴 Extreme Greed - Potential selling opportunity")

# ============================================================
# PAGE 3: NEWS & SENTIMENT
# ============================================================
elif page == "📰 News & Sentiment":
    st.markdown('<p class="main-header">News & Sentiment Analysis</p>', unsafe_allow_html=True)

    # Crypto input - accepts symbols only for news search
    crypto_input = st.text_input(
        "Enter Cryptocurrency Symbol",
        value="BTC",
        placeholder="e.g., BTC, ETH, ADA, SOL",
        help="Enter ticker symbol (BTC, ETH, ADA, etc.) for news search"
    )
    crypto_symbol = crypto_input.upper().strip()

    hours_back = st.slider("Hours of news to fetch", 6, 48, 24)

    if st.button("Fetch & Analyze News", type="primary"):
        news_fetcher = clients['news']

        with st.spinner("Fetching news articles..."):
            articles = news_fetcher.get_crypto_news(crypto_symbol, hours_back)

            if articles:
                st.success(f"Found {len(articles)} articles for {crypto_symbol}")

                # Sentiment analysis
                if os.getenv('OPENAI_API_KEY'):
                    with st.spinner("Analyzing sentiment with AI..."):
                        try:
                            analyzer = CryptoSentimentAnalyzer()
                            analyzed = analyzer.analyze_news_batch(articles, crypto_symbol, max_articles=10)
                            overall_sentiment = analyzer.get_overall_sentiment(analyzed)

                            # Overall sentiment
                            st.subheader("Overall Sentiment")
                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                sentiment_class = "bullish-sentiment" if overall_sentiment['avg_score'] > 0 else "bearish-sentiment"
                                st.markdown(f"<p class='{sentiment_class}'>{overall_sentiment['sentiment_label']}</p>",
                                          unsafe_allow_html=True)
                                st.metric("Avg Score", f"{overall_sentiment['avg_score']:.1f}/10")

                            with col2:
                                st.metric("Bullish", overall_sentiment['bullish_count'],
                                        delta="positive" if overall_sentiment['bullish_count'] > overall_sentiment['bearish_count'] else None)

                            with col3:
                                st.metric("Bearish", overall_sentiment['bearish_count'],
                                        delta="negative" if overall_sentiment['bearish_count'] > overall_sentiment['bullish_count'] else None)

                            with col4:
                                st.metric("Critical News", overall_sentiment['critical_count'])

                            # Sentiment distribution
                            st.subheader("Sentiment Distribution")
                            fig = go.Figure(data=[go.Bar(
                                x=['Bullish', 'Neutral', 'Bearish'],
                                y=[overall_sentiment['bullish_count'],
                                   overall_sentiment['neutral_count'],
                                   overall_sentiment['bearish_count']],
                                marker_color=['green', 'gray', 'red']
                            )])
                            fig.update_layout(title='Article Sentiment Breakdown')
                            st.plotly_chart(fig, use_container_width=True)

                            # Display analyzed articles
                            st.markdown("---")
                            st.subheader("Recent Articles with Sentiment")

                            for article in analyzed:
                                sentiment = article['sentiment']

                                with st.expander(f"{article['title']} - {sentiment['label']} ({sentiment['score']:+.1f})"):
                                    st.write(f"**Source:** {article.get('source_name', 'Unknown')}")
                                    st.write(f"**Published:** {article['published'].strftime('%Y-%m-%d %H:%M')}")
                                    st.write(f"**Link:** {article['link']}")
                                    st.write(f"**Sentiment:** {sentiment['explanation']}")

                                    if sentiment['flags']['hack']:
                                        st.error("⚠️ Security/Hack Alert")
                                    if sentiment['flags']['regulation']:
                                        st.warning("⚖️ Regulation News")
                                    if sentiment['flags']['adoption']:
                                        st.success("🚀 Adoption News")
                                    if sentiment['flags']['tech']:
                                        st.info("🔧 Technical Update")

                        except Exception as e:
                            st.error(f"Sentiment analysis failed: {e}")
                            st.info("Showing news without sentiment analysis")

                            for article in articles[:10]:
                                with st.expander(article['title']):
                                    st.write(f"**Source:** {article.get('source_name', 'Unknown')}")
                                    st.write(f"**Published:** {article['published'].strftime('%Y-%m-%d %H:%M')}")
                                    st.write(f"**Link:** {article['link']}")
                                    st.write(article['summary'])
                else:
                    st.warning("Set OPENAI_API_KEY environment variable for sentiment analysis")
                    st.info("Showing news without sentiment analysis")

                    for article in articles[:10]:
                        with st.expander(article['title']):
                            st.write(f"**Source:** {article.get('source_name', 'Unknown')}")
                            st.write(f"**Published:** {article['published'].strftime('%Y-%m-%d %H:%M')}")
                            st.write(f"**Link:** {article['link']}")
                            st.write(article['summary'])
            else:
                st.warning(f"No recent news found for {crypto_symbol}")

# ============================================================
# PAGE 4: ANALYZE INDIVIDUAL CRYPTO
# ============================================================
elif page == "🔍 Analyze Individual Crypto":
    st.markdown('<p class="main-header">Analyze Individual Crypto</p>', unsafe_allow_html=True)
    st.markdown("**Deep dive analysis with AI trading recommendations**")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Crypto selector - now accepts any CoinGecko ID or common symbol
        crypto_input = st.text_input(
            "Enter Cryptocurrency to Analyze",
            value="bitcoin",
            placeholder="e.g., bitcoin, ethereum, cardano, solana",
            key='analyze_crypto',
            help="Enter CoinGecko ID (like 'bitcoin', 'ethereum') or common symbol (like 'BTC', 'ETH'). "
                 "Find crypto IDs at: https://www.coingecko.com/"
        )

        # Map common symbols to CoinGecko IDs
        symbol_to_id = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'ADA': 'cardano',
            'SOL': 'solana',
            'XRP': 'ripple',
            'DOT': 'polkadot',
            'DOGE': 'dogecoin',
            'MATIC': 'matic-network',
            'AVAX': 'avalanche-2',
            'LINK': 'chainlink',
            'UNI': 'uniswap',
            'ATOM': 'cosmos',
            'LTC': 'litecoin',
            'BCH': 'bitcoin-cash',
            'ALGO': 'algorand',
            'XLM': 'stellar',
            'VET': 'vechain',
            'ICP': 'internet-computer',
            'FIL': 'filecoin',
            'AAVE': 'aave',
        }

        # Convert input to CoinGecko ID (handle both symbols and IDs)
        crypto_input_upper = crypto_input.upper()
        if crypto_input_upper in symbol_to_id:
            crypto_id = symbol_to_id[crypto_input_upper]
            crypto_symbol = crypto_input_upper
        else:
            # Assume it's already a CoinGecko ID (lowercase)
            crypto_id = crypto_input.lower().strip()
            crypto_symbol = crypto_id.upper()

        st.caption(f"📊 Analyzing: **{crypto_symbol}** (CoinGecko ID: `{crypto_id}`)")

    with col2:
        # Model selector
        if os.getenv('OPENAI_API_KEY'):
            from src.llm.sentiment_analyzer import CryptoSentimentAnalyzer
            model_options = {
                'gpt-4o-mini': 'GPT-4o Mini (Fast & Cheap)',
                'gpt-4o': 'GPT-4o (Recommended)',
                'gpt-4-turbo': 'GPT-4 Turbo (Most Capable)',
                'o1-mini': 'O1 Mini (Reasoning)'
            }
            selected_model = st.selectbox(
                "AI Model",
                options=list(model_options.keys()),
                format_func=lambda x: model_options[x],
                index=1,  # Default to gpt-4o
                key='model_select'
            )

            # Show cost estimate
            costs = CryptoSentimentAnalyzer.MODELS[selected_model]
            st.caption(f"Cost: ~${costs['input']}/M input, ~${costs['output']}/M output tokens")

    # Initialize session state for showing analysis
    if 'run_analysis' not in st.session_state:
        st.session_state.run_analysis = False

    if 'analysis_crypto' not in st.session_state:
        st.session_state.analysis_crypto = None

    # Track if we just ran a fresh analysis
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False

    # Button to trigger analysis
    run_fresh_analysis = st.button("Run Complete Analysis", type="primary", key="analyze_btn")

    if run_fresh_analysis:
        st.session_state.run_analysis = True
        st.session_state.analysis_crypto = crypto_symbol
        st.session_state.analysis_complete = False  # Mark as needing fresh data

    # Display analysis if triggered (persists across reruns)
    if st.session_state.run_analysis and st.session_state.analysis_crypto == crypto_symbol:
        client = clients['coingecko']
        news_fetcher = clients['news']

        # Only fetch data if this is a fresh analysis (not a rerun from Q&A)
        if not st.session_state.analysis_complete:
            with st.spinner(f"Analyzing {crypto_symbol}..."):
                # Fetch all data once and cache it
                market_data = client.get_market_data(crypto_id)

                # Store in session state for reuse
                st.session_state.cached_market_data = market_data
        else:
            # Use cached data
            market_data = st.session_state.get('cached_market_data')

        # Section 1: Current Price & Market Data
        st.subheader(f"📈 {crypto_symbol} Market Overview")

        if market_data:
            if market_data:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Current Price", f"${market_data['current_price']:,.2f}")
                    st.metric("24h High", f"${market_data['high_24h']:,.2f}")

                with col2:
                    change_24h = market_data['price_change_percentage_24h']
                    st.metric("24h Change", f"{change_24h:+.2f}%")
                    st.metric("24h Low", f"${market_data['low_24h']:,.2f}")

                with col3:
                    st.metric("Market Cap", f"${market_data['market_cap']/1e9:.2f}B")
                    st.metric("24h Volume", f"${market_data['total_volume']/1e9:.2f}B")

                with col4:
                    st.metric("7d Change", f"{market_data['price_change_percentage_7d']:+.2f}%")
                    st.metric("30d Change", f"{market_data['price_change_percentage_30d']:+.2f}%")

                # Supply metrics
                st.markdown("---")
                st.subheader("💰 Supply Metrics")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Circulating Supply", f"{market_data['circulating_supply']/1e6:.2f}M {crypto_symbol}")
                with col2:
                    if market_data['total_supply']:
                        st.metric("Total Supply", f"{market_data['total_supply']/1e6:.2f}M {crypto_symbol}")
                with col3:
                    if market_data['max_supply']:
                        st.metric("Max Supply", f"{market_data['max_supply']/1e6:.2f}M {crypto_symbol}")
                        supply_pct = (market_data['circulating_supply'] / market_data['max_supply'] * 100)
                        st.caption(f"{supply_pct:.1f}% of max supply in circulation")

                # ATH/ATL
                st.markdown("---")
                st.subheader("📊 All-Time Stats")

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("All-Time High", f"${market_data['ath']:,.2f}")
                    if market_data['ath_date']:
                        ath_date = market_data['ath_date'][:10]
                        st.caption(f"Reached on {ath_date}")

                    # Distance from ATH
                    distance_from_ath = ((market_data['current_price'] - market_data['ath']) / market_data['ath'] * 100)
                    if distance_from_ath < -20:
                        st.error(f"{distance_from_ath:.1f}% from ATH")
                    else:
                        st.warning(f"{distance_from_ath:.1f}% from ATH")

                with col2:
                    st.metric("All-Time Low", f"${market_data['atl']:,.2f}")
                    if market_data['atl_date']:
                        atl_date = market_data['atl_date'][:10]
                        st.caption(f"Reached on {atl_date}")

                    # Distance from ATL
                    distance_from_atl = ((market_data['current_price'] - market_data['atl']) / market_data['atl'] * 100)
                    st.success(f"+{distance_from_atl:.1f}% from ATL")

            # Section 2: Historical Price Chart
            st.markdown("---")
            st.subheader("📉 Price History & Technical Indicators")
            st.caption("💡 Tip: Use 30+ days for reliable technical indicators (RSI, MACD need sufficient data)")

            period = st.selectbox("Select Period", ['30 Days', '90 Days', '1 Year', '7 Days'], key='hist_period')
            days_map = {'7 Days': 7, '30 Days': 30, '90 Days': 90, '1 Year': 365}
            days = days_map[period]

            # Fetch historical data only if fresh analysis
            if not st.session_state.analysis_complete:
                hist_df = client.get_historical_prices(crypto_id, days)

                # Check if data fetch was successful
                if hist_df is None or hist_df.empty:
                    st.warning(f"⚠️ Could not fetch historical data for {crypto_symbol}. This may be due to API limits.")
                    st.info("Technical indicators require historical price data. Try again in a moment or check your API access.")
                    hist_df = pd.DataFrame()  # Ensure it's an empty DataFrame
                    indicators = {}
                    st.session_state.cached_hist_df = hist_df
                    st.session_state.cached_hist_days = days
                    st.session_state.cached_indicators = indicators
                else:
                    st.session_state.cached_hist_df = hist_df
                    st.session_state.cached_hist_days = days

                    # Calculate technical indicators
                    try:
                        if hist_df is not None and not hist_df.empty:
                            tech_indicators = TechnicalIndicators(hist_df)
                            indicators = tech_indicators.calculate_all()
                            st.session_state.cached_indicators = indicators
                            st.session_state.cached_indicators_df = tech_indicators.get_dataframe_with_indicators()
                        else:
                            st.warning("No historical data available to calculate technical indicators")
                            indicators = {}
                            st.session_state.cached_indicators = indicators
                    except Exception as e:
                        st.error(f"Error calculating technical indicators: {e}")
                        st.info(f"Historical data columns: {list(hist_df.columns) if hist_df is not None and not hist_df.empty else 'No data'}")
                        indicators = {}
                        st.session_state.cached_indicators = indicators
            else:
                # Use cached data (or refetch if user changed the period)
                if st.session_state.get('cached_hist_days') != days:
                    hist_df = client.get_historical_prices(crypto_id, days)
                    st.session_state.cached_hist_df = hist_df
                    st.session_state.cached_hist_days = days

                    # Recalculate technical indicators for new period
                    try:
                        if hist_df is not None and not hist_df.empty:
                            tech_indicators = TechnicalIndicators(hist_df)
                            indicators = tech_indicators.calculate_all()
                            st.session_state.cached_indicators = indicators
                            st.session_state.cached_indicators_df = tech_indicators.get_dataframe_with_indicators()
                        else:
                            st.warning("No historical data available to calculate technical indicators")
                            indicators = {}
                            st.session_state.cached_indicators = indicators
                    except Exception as e:
                        st.error(f"Error calculating technical indicators: {e}")
                        st.info(f"Historical data columns: {list(hist_df.columns) if hist_df is not None and not hist_df.empty else 'No data'}")
                        indicators = {}
                        st.session_state.cached_indicators = indicators
                else:
                    hist_df = st.session_state.get('cached_hist_df')
                    indicators = st.session_state.get('cached_indicators', {})

            if not hist_df.empty and indicators:
                # Get DataFrame with indicators
                indicators_df = st.session_state.get('cached_indicators_df', hist_df)

                # Create enhanced price chart with technical indicators
                fig = go.Figure()

                # Price line
                fig.add_trace(go.Scatter(
                    x=indicators_df['timestamp'],
                    y=indicators_df['price'],
                    mode='lines',
                    name='Price',
                    line=dict(color='#f7931a', width=2.5),
                    showlegend=True
                ))

                # Add Bollinger Bands
                if 'BB_upper' in indicators_df.columns:
                    fig.add_trace(go.Scatter(
                        x=indicators_df['timestamp'],
                        y=indicators_df['BB_upper'],
                        mode='lines',
                        name='BB Upper',
                        line=dict(color='rgba(128, 128, 128, 0.5)', width=1, dash='dash'),
                        showlegend=True
                    ))
                    fig.add_trace(go.Scatter(
                        x=indicators_df['timestamp'],
                        y=indicators_df['BB_middle'],
                        mode='lines',
                        name='BB Middle (SMA 20)',
                        line=dict(color='rgba(0, 0, 255, 0.5)', width=1),
                        showlegend=True
                    ))
                    fig.add_trace(go.Scatter(
                        x=indicators_df['timestamp'],
                        y=indicators_df['BB_lower'],
                        mode='lines',
                        name='BB Lower',
                        line=dict(color='rgba(128, 128, 128, 0.5)', width=1, dash='dash'),
                        fill='tonexty',
                        fillcolor='rgba(128, 128, 128, 0.1)',
                        showlegend=True
                    ))

                # Add moving averages
                if 'SMA_50' in indicators_df.columns:
                    fig.add_trace(go.Scatter(
                        x=indicators_df['timestamp'],
                        y=indicators_df['SMA_50'],
                        mode='lines',
                        name='SMA 50',
                        line=dict(color='green', width=1.5),
                        showlegend=True
                    ))

                if 'SMA_200' in indicators_df.columns:
                    fig.add_trace(go.Scatter(
                        x=indicators_df['timestamp'],
                        y=indicators_df['SMA_200'],
                        mode='lines',
                        name='SMA 200',
                        line=dict(color='red', width=1.5),
                        showlegend=True
                    ))

                # Add support/resistance lines
                if 'support_resistance' in indicators:
                    sr = indicators['support_resistance']
                    if 'nearest_support' in sr:
                        fig.add_hline(
                            y=sr['nearest_support'],
                            line_dash="dot",
                            line_color="green",
                            annotation_text=f"Support: ${sr['nearest_support']:,.0f}",
                            annotation_position="right"
                        )
                    if 'nearest_resistance' in sr:
                        fig.add_hline(
                            y=sr['nearest_resistance'],
                            line_dash="dot",
                            line_color="red",
                            annotation_text=f"Resistance: ${sr['nearest_resistance']:,.0f}",
                            annotation_position="right"
                        )

                # Calculate percentage change
                start_price = indicators_df['price'].iloc[0]
                end_price = indicators_df['price'].iloc[-1]
                pct_change = ((end_price - start_price) / start_price * 100)

                fig.update_layout(
                    title=f'{crypto_symbol} Price with Technical Indicators - Last {period} ({pct_change:+.2f}%)',
                    xaxis_title='Date',
                    yaxis_title='Price (USD)',
                    hovermode='x unified',
                    template='plotly_white',
                    height=500,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )

                st.plotly_chart(fig, use_container_width=True)

                # RSI Chart
                if 'RSI' in indicators_df.columns:
                    fig_rsi = go.Figure()
                    fig_rsi.add_trace(go.Scatter(
                        x=indicators_df['timestamp'],
                        y=indicators_df['RSI'],
                        mode='lines',
                        name='RSI',
                        line=dict(color='purple', width=2)
                    ))
                    # Add overbought/oversold lines
                    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
                    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
                    fig_rsi.add_hline(y=50, line_dash="dot", line_color="gray")

                    fig_rsi.update_layout(
                        title='RSI (Relative Strength Index)',
                        xaxis_title='Date',
                        yaxis_title='RSI',
                        yaxis=dict(range=[0, 100]),
                        template='plotly_white',
                        height=250
                    )
                    st.plotly_chart(fig_rsi, use_container_width=True)

                # MACD Chart
                if 'MACD' in indicators_df.columns:
                    fig_macd = go.Figure()
                    fig_macd.add_trace(go.Scatter(
                        x=indicators_df['timestamp'],
                        y=indicators_df['MACD'],
                        mode='lines',
                        name='MACD',
                        line=dict(color='blue', width=2)
                    ))
                    fig_macd.add_trace(go.Scatter(
                        x=indicators_df['timestamp'],
                        y=indicators_df['MACD_signal'],
                        mode='lines',
                        name='Signal',
                        line=dict(color='red', width=2)
                    ))
                    # Histogram
                    colors = ['green' if val >= 0 else 'red' for val in indicators_df['MACD_histogram']]
                    fig_macd.add_trace(go.Bar(
                        x=indicators_df['timestamp'],
                        y=indicators_df['MACD_histogram'],
                        name='Histogram',
                        marker_color=colors
                    ))
                    fig_macd.add_hline(y=0, line_dash="dash", line_color="gray")

                    fig_macd.update_layout(
                        title='MACD (Moving Average Convergence Divergence)',
                        xaxis_title='Date',
                        yaxis_title='MACD',
                        template='plotly_white',
                        height=250
                    )
                    st.plotly_chart(fig_macd, use_container_width=True)

                # Price statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Period High", f"${hist_df['price'].max():,.2f}")
                with col2:
                    st.metric("Period Low", f"${hist_df['price'].min():,.2f}")
                with col3:
                    st.metric("Average Price", f"${hist_df['price'].mean():,.2f}")
                with col4:
                    volatility = hist_df['price'].std()
                    st.metric("Volatility (StdDev)", f"${volatility:,.2f}")

                # Technical Analysis Summary
                if indicators:
                    st.markdown("---")
                    st.subheader("📊 Technical Analysis Summary")

                    # Debug: Show what's in indicators (remove this after fixing)
                    with st.expander("🔍 Debug: View Raw Indicators Data"):
                        st.json(indicators)

                    # Overall signal
                    if 'signals' in indicators:
                        signals = indicators['signals']
                        overall_signal = signals.get('overall', 'NEUTRAL')
                        confidence = signals.get('confidence', 0)

                        if overall_signal == 'BULLISH':
                            st.success(f"### 🟢 Overall Signal: {overall_signal} ({confidence}% confidence)")
                        elif overall_signal == 'BEARISH':
                            st.error(f"### 🔴 Overall Signal: {overall_signal} ({confidence}% confidence)")
                        else:
                            st.info(f"### 🟡 Overall Signal: {overall_signal} ({confidence}% confidence)")

                        st.write(f"**Breakdown:** {signals.get('bullish', 0)} bullish, "
                                f"{signals.get('bearish', 0)} bearish, "
                                f"{signals.get('neutral', 0)} neutral indicators")

                        # Add explanation for beginners
                        with st.expander("ℹ️ What is Overall Signal?"):
                            st.markdown("""
                            The **Overall Signal** combines ALL technical indicators into one recommendation:

                            - **BULLISH** 🟢 = Most indicators suggest price will go UP (good time to buy/hold)
                            - **BEARISH** 🔴 = Most indicators suggest price will go DOWN (consider selling/waiting)
                            - **NEUTRAL** 🟡 = Mixed signals, no clear direction (wait for clearer trend)

                            **Confidence %** shows how strongly the indicators agree:
                            - 80-100% = Very strong agreement (high confidence)
                            - 60-79% = Good agreement (moderate confidence)
                            - 40-59% = Weak agreement (low confidence)
                            - Below 40% = Contradictory signals (be cautious!)

                            The breakdown shows how many indicators are bullish/bearish/neutral.
                            """)

                    # Display key indicators
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown("**RSI (14)**")
                        try:
                            if 'rsi' in indicators:
                                rsi = indicators['rsi']
                                if isinstance(rsi, dict):
                                    if 'error' in rsi:
                                        st.error(rsi['error'])
                                    elif 'value' in rsi:
                                        rsi_val = rsi['value']
                                        st.metric(
                                            "RSI Value",
                                            f"{rsi_val:.1f}",
                                            help="Relative Strength Index (RSI) measures momentum from 0-100. "
                                                 "Above 70 = Overbought (price may drop soon). "
                                                 "Below 30 = Oversold (price may rise soon). "
                                                 "Between 40-60 = Neutral. "
                                                 "The (14) means it looks at the last 14 days of price changes."
                                        )
                                        st.caption(f"{rsi.get('signal', 'N/A')}: {rsi.get('recommendation', 'N/A')}")
                                    else:
                                        st.warning("RSI data incomplete")
                                        st.write(rsi)
                                else:
                                    st.warning(f"RSI format unexpected: {type(rsi)}")
                            else:
                                st.info("RSI not calculated")
                        except Exception as e:
                            st.error(f"Error displaying RSI: {e}")

                    with col2:
                        st.markdown("**MACD**")
                        try:
                            if 'macd' in indicators:
                                macd = indicators['macd']
                                if isinstance(macd, dict):
                                    if 'error' in macd:
                                        st.error(macd['error'])
                                    elif 'macd' in macd:
                                        st.metric(
                                            "MACD",
                                            f"{macd['macd']:.2f}",
                                            help="Moving Average Convergence Divergence shows trend strength and direction. "
                                                 "When MACD line crosses ABOVE signal line = Bullish (buy signal). "
                                                 "When MACD crosses BELOW signal line = Bearish (sell signal). "
                                                 "Larger histogram bars = stronger momentum. Green bars = upward, Red bars = downward."
                                        )
                                        st.metric(
                                            "Signal",
                                            f"{macd.get('signal', 0):.2f}",
                                            help="The Signal line is a smoothed average of the MACD. "
                                                 "Watch for when MACD crosses the Signal line - that's your trading signal!"
                                        )
                                        st.caption(f"{macd.get('trade_signal', 'N/A')}")
                                    else:
                                        st.warning("MACD data incomplete")
                                        st.write(macd)
                                else:
                                    st.warning(f"MACD format unexpected: {type(macd)}")
                            else:
                                st.info("MACD not calculated")
                        except Exception as e:
                            st.error(f"Error displaying MACD: {e}")

                    with col3:
                        st.markdown("**Bollinger Bands**")
                        try:
                            if 'bollinger' in indicators:
                                bb = indicators['bollinger']
                                if isinstance(bb, dict):
                                    if 'error' in bb:
                                        st.error(bb['error'])
                                    elif 'current_price' in bb:
                                        st.metric(
                                            "Price Position",
                                            f"{bb.get('price_position', 0):.0f}%",
                                            help="Bollinger Bands show price volatility using 3 lines: upper, middle, lower. "
                                                 "Price Position shows where current price is in that range. "
                                                 "Near 100% = Price touching upper band (overbought, may drop). "
                                                 "Near 0% = Price touching lower band (oversold, may rise). "
                                                 "Around 50% = Price at middle line (neutral). "
                                                 "Wide bands = High volatility. Narrow bands = Low volatility."
                                        )
                                        st.caption(f"{bb.get('signal', 'N/A')}: {bb.get('recommendation', 'N/A')}")
                                    else:
                                        st.warning("Bollinger Bands data incomplete")
                                        st.write(bb)
                                else:
                                    st.warning(f"Bollinger Bands format unexpected: {type(bb)}")
                            else:
                                st.info("Bollinger Bands not calculated")
                        except Exception as e:
                            st.error(f"Error displaying Bollinger Bands: {e}")

                    # Moving Averages Summary
                    if 'sma' in indicators:
                        st.markdown("**Moving Averages**")
                        sma = indicators['sma']

                        # Tooltip explanations for each SMA period
                        sma_help = {
                            'SMA_20': "Simple Moving Average of last 20 days. Shows SHORT-TERM trend. "
                                     "Price above SMA 20 = Short-term uptrend. Price below = Short-term downtrend.",
                            'SMA_50': "Simple Moving Average of last 50 days. Shows MEDIUM-TERM trend. "
                                     "Price above SMA 50 = Medium-term uptrend. This is important for swing trading.",
                            'SMA_200': "Simple Moving Average of last 200 days. Shows LONG-TERM trend. "
                                      "Price above SMA 200 = Bull market. Price below = Bear market. "
                                      "Most important moving average used by professionals!",
                            'SMA_100': "Simple Moving Average of last 100 days. Shows intermediate trend between SMA 50 and SMA 200."
                        }

                        cols = st.columns(4)
                        idx = 0
                        for key, value in sma.items():
                            if key.startswith('SMA_') and isinstance(value, dict):
                                with cols[idx % 4]:
                                    period = key.replace('SMA_', '')
                                    signal_emoji = "🟢" if value['signal'] == 'BULLISH' else "🔴"
                                    st.metric(
                                        f"{key}",
                                        f"${value['value']:,.0f}",
                                        delta=value['signal'],
                                        help=sma_help.get(key, f"Moving average of last {period} days")
                                    )
                                    idx += 1

                        # Golden/Death Cross alert
                        if sma.get('golden_cross'):
                            st.success("🌟 **GOLDEN CROSS DETECTED!** SMA 50 crossed above SMA 200 - Strong bullish signal")
                            st.info("💡 What is Golden Cross? When the 50-day average crosses ABOVE the 200-day average, "
                                   "it signals a major uptrend is starting. Historically very bullish!")
                        elif sma.get('death_cross'):
                            st.error("💀 **DEATH CROSS DETECTED!** SMA 50 crossed below SMA 200 - Strong bearish signal")
                            st.info("💡 What is Death Cross? When the 50-day average crosses BELOW the 200-day average, "
                                   "it signals a major downtrend is starting. Historically very bearish!")

                    # Support/Resistance
                    if 'support_resistance' in indicators:
                        sr = indicators['support_resistance']
                        if 'current_price' in sr:
                            st.markdown("**Support & Resistance Levels**")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric(
                                    "Nearest Support",
                                    f"${sr['nearest_support']:,.0f}",
                                    delta=f"-{sr['distance_to_support_pct']:.1f}%",
                                    help="Support is a price level where buying pressure historically prevents further decline. "
                                         "Think of it as a 'floor' - when price drops to this level, buyers tend to step in. "
                                         "Useful for setting stop-loss orders just below support. "
                                         "If price breaks BELOW support, it may continue falling (bearish signal)."
                                )
                            with col2:
                                st.metric("Current Price", f"${sr['current_price']:,.0f}")
                            with col3:
                                st.metric(
                                    "Nearest Resistance",
                                    f"${sr['nearest_resistance']:,.0f}",
                                    delta=f"+{sr['distance_to_resistance_pct']:.1f}%",
                                    help="Resistance is a price level where selling pressure historically prevents further rise. "
                                         "Think of it as a 'ceiling' - when price rises to this level, sellers tend to step in. "
                                         "Useful for setting take-profit targets or identifying potential selling points. "
                                         "If price breaks ABOVE resistance, it may continue rising (bullish signal)."
                                )
                            st.caption(sr['recommendation'])

                            # Add educational note
                            with st.expander("ℹ️ How to use Support & Resistance?"):
                                st.markdown("""
                                **Support & Resistance** are the most important price levels in trading:

                                **Support (Floor)**:
                                - Price level where buyers have historically stepped in
                                - When price approaches support, it often bounces back up
                                - Good place to set stop-loss orders (just below support)
                                - If support breaks = strong sell signal

                                **Resistance (Ceiling)**:
                                - Price level where sellers have historically stepped in
                                - When price approaches resistance, it often gets pushed back down
                                - Good place to take profits or set sell orders
                                - If resistance breaks = strong buy signal (breakout!)

                                **Trading Strategy**:
                                - Buy near support, sell near resistance
                                - Set stop-loss just below support to limit losses
                                - Set take-profit just below resistance to secure gains
                                - Watch for breakouts (price breaking through support/resistance)
                                """)

                    # Volume Analysis Section
                    if 'volume_analysis' in indicators:
                        st.markdown("---")
                        st.subheader("📊 Volume Analysis")

                        vol = indicators['volume_analysis']

                        if 'error' not in vol:
                            # Volume metrics in columns
                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                trend = vol.get('trend', {})
                                trend_direction = trend.get('direction', 'NEUTRAL')
                                trend_emoji = "📈" if trend_direction == 'RISING' else "📉" if trend_direction == 'FALLING' else "➖"
                                st.metric(
                                    "Volume Trend",
                                    trend_direction,
                                    help="Direction of volume over time. RISING = Increasing interest. FALLING = Decreasing interest."
                                )
                                st.caption(f"{trend_emoji} {trend.get('strength', 'N/A')} strength")

                            with col2:
                                spikes = vol.get('spikes', {})
                                spike_count = spikes.get('count', 0)
                                st.metric(
                                    "Volume Spikes",
                                    spike_count,
                                    help="Unusual volume activity. Spikes often precede big price moves. High spikes = major events or high interest."
                                )
                                if spike_count > 0:
                                    st.caption(f"⚠️ {spike_count} spike(s) detected")

                            with col3:
                                divergence = vol.get('divergence', {})
                                div_type = divergence.get('type', 'NONE')
                                div_emoji = "🟢" if div_type == 'BULLISH' else "🔴" if div_type == 'BEARISH' else "⚪"
                                st.metric(
                                    "Price-Volume Divergence",
                                    div_type,
                                    help="Mismatch between price and volume. BULLISH divergence = Price down but volume up (reversal signal). BEARISH divergence = Price up but volume down (weakness)."
                                )
                                st.caption(f"{div_emoji} {divergence.get('strength', 'N/A')}")

                            with col4:
                                confirmation = vol.get('confirmation_score', 0)
                                st.metric(
                                    "Volume Confirmation",
                                    f"{confirmation:.0f}/100",
                                    help="How well volume supports the price trend. >70 = Strong support. 50-70 = Moderate. <50 = Weak or conflicting."
                                )
                                if confirmation >= 70:
                                    st.caption("🟢 Strong confirmation")
                                elif confirmation >= 50:
                                    st.caption("🟡 Moderate confirmation")
                                else:
                                    st.caption("🔴 Weak confirmation")

                            # Volume chart
                            if 'volume' in indicators_df.columns and 'price' in indicators_df.columns:
                                try:
                                    fig_vol = go.Figure()

                                    # Color volume bars by price change
                                    colors = []
                                    for i in range(len(indicators_df)):
                                        if i == 0:
                                            colors.append('gray')  # First bar - no previous price to compare
                                        else:
                                            # Green if price went up, red if price went down
                                            if indicators_df['price'].iloc[i] >= indicators_df['price'].iloc[i-1]:
                                                colors.append('#00c853')  # Green
                                            else:
                                                colors.append('#d32f2f')  # Red

                                    fig_vol.add_trace(go.Bar(
                                        x=indicators_df['timestamp'],
                                        y=indicators_df['volume'],
                                        name='Volume',
                                        marker=dict(
                                            color=colors,
                                            line=dict(width=0)
                                        ),
                                        showlegend=True
                                    ))

                                    # Add average volume line
                                    if 'volume_sma' in indicators_df.columns:
                                        fig_vol.add_trace(go.Scatter(
                                            x=indicators_df['timestamp'],
                                            y=indicators_df['volume_sma'],
                                            mode='lines',
                                            name='Volume SMA (20)',
                                            line=dict(color='orange', width=2)
                                        ))

                                    fig_vol.update_layout(
                                        title='Trading Volume - Green bars = price up, Red bars = price down',
                                        xaxis_title='Date',
                                        yaxis_title='Volume',
                                        template='plotly_white',
                                        height=300,
                                        showlegend=True
                                    )
                                    st.plotly_chart(fig_vol, use_container_width=True)
                                except Exception as e:
                                    st.error(f"Error creating volume chart: {e}")
                                    st.info(f"Available columns: {list(indicators_df.columns)}")

                            # Volume analysis explanation
                            with st.expander("ℹ️ Understanding Volume Analysis"):
                                st.markdown("""
                                **Volume Analysis** measures trading activity and market interest:

                                **Volume Trend**:
                                - RISING = Growing interest, trend likely to continue
                                - FALLING = Declining interest, trend may be weakening
                                - Volume confirms price moves - high volume validates trends

                                **Volume Spikes**:
                                - Sudden surge in trading activity
                                - Often signals major news or events
                                - Can precede large price movements
                                - Multiple spikes = high volatility period

                                **Price-Volume Divergence**:
                                - BULLISH: Price falling but volume rising = Potential reversal up
                                - BEARISH: Price rising but volume falling = Weak rally, may reverse down
                                - NONE: Price and volume aligned = Healthy trend

                                **Volume Confirmation Score**:
                                - Measures how well volume supports the price trend
                                - High score (>70) = Strong conviction, trust the trend
                                - Low score (<50) = Weak support, be cautious

                                **Trading Tips**:
                                - High volume breakouts are more reliable
                                - Low volume moves can reverse quickly
                                - Volume spikes often mark tops/bottoms
                                - Rising volume + rising price = Strong uptrend
                                - Falling volume + rising price = Weak rally (sell signal)
                                """)
                        else:
                            st.info("Volume analysis not available for this dataset")

                    # Advanced Indicators Section
                    if 'advanced_indicators' in indicators:
                        st.markdown("---")
                        st.subheader("🔬 Advanced Indicators")

                        adv = indicators['advanced_indicators']

                        if 'error' not in adv:
                            # Metrics row
                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                # Stochastic Oscillator
                                stoch = adv.get('stochastic', {})
                                if 'k' in stoch:
                                    k_value = stoch['k']
                                    signal = stoch.get('signal', 'NEUTRAL')
                                    signal_emoji = "🟢" if signal == 'OVERSOLD' else "🔴" if signal == 'OVERBOUGHT' else "⚪"
                                    st.metric(
                                        "Stochastic %K",
                                        f"{k_value:.1f}",
                                        help="Measures momentum from 0-100. >80 = Overbought (may drop). <20 = Oversold (may rise). Shows when price is at extremes."
                                    )
                                    st.caption(f"{signal_emoji} {signal}")

                            with col2:
                                # ADX (Trend Strength)
                                adx = adv.get('adx', {})
                                if 'adx' in adx:
                                    adx_value = adx['adx']
                                    strength = adx.get('strength', 'N/A')
                                    st.metric(
                                        "ADX (Trend Strength)",
                                        f"{adx_value:.1f}",
                                        help="Measures trend strength (not direction). >25 = Strong trend. <20 = Weak/no trend. High ADX = Trend worth following."
                                    )
                                    if adx_value > 25:
                                        st.caption(f"🟢 {strength} trend")
                                    else:
                                        st.caption(f"⚪ {strength} trend")

                            with col3:
                                # ATR (Volatility)
                                atr = adv.get('atr', {})
                                if 'atr' in atr:
                                    atr_value = atr['atr']
                                    volatility = atr.get('volatility_level', 'N/A')
                                    st.metric(
                                        "ATR (Volatility)",
                                        f"${atr_value:,.0f}",
                                        help="Average True Range - measures volatility. Higher ATR = bigger price swings. Use for setting stop-loss levels."
                                    )
                                    st.caption(f"{volatility} volatility")

                            with col4:
                                # OBV (Volume Momentum)
                                obv = adv.get('obv', {})
                                if 'trend' in obv:
                                    obv_trend = obv['trend']
                                    divergence = obv.get('divergence', 'NONE')
                                    obv_emoji = "📈" if obv_trend == 'RISING' else "📉" if obv_trend == 'FALLING' else "➖"
                                    st.metric(
                                        "OBV Trend",
                                        obv_trend,
                                        help="On-Balance Volume tracks cumulative volume flow. RISING = Money flowing in (bullish). FALLING = Money flowing out (bearish)."
                                    )
                                    if divergence != 'NONE':
                                        div_emoji = "🟢" if divergence == 'BULLISH' else "🔴"
                                        st.caption(f"{div_emoji} {divergence} divergence")
                                    else:
                                        st.caption(f"{obv_emoji} {obv.get('strength', 'N/A')}")

                            # Charts for advanced indicators
                            chart_col1, chart_col2 = st.columns(2)

                            with chart_col1:
                                # Stochastic Oscillator Chart
                                if 'stochastic_k' in indicators_df.columns and 'stochastic_d' in indicators_df.columns:
                                    fig_stoch = go.Figure()
                                    fig_stoch.add_trace(go.Scatter(
                                        x=indicators_df['timestamp'],
                                        y=indicators_df['stochastic_k'],
                                        mode='lines',
                                        name='%K (Fast)',
                                        line=dict(color='blue', width=2)
                                    ))
                                    fig_stoch.add_trace(go.Scatter(
                                        x=indicators_df['timestamp'],
                                        y=indicators_df['stochastic_d'],
                                        mode='lines',
                                        name='%D (Slow)',
                                        line=dict(color='red', width=2)
                                    ))
                                    # Overbought/Oversold lines
                                    fig_stoch.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Overbought")
                                    fig_stoch.add_hline(y=20, line_dash="dash", line_color="green", annotation_text="Oversold")
                                    fig_stoch.update_layout(
                                        title='Stochastic Oscillator (%K and %D)',
                                        yaxis=dict(range=[0, 100]),
                                        template='plotly_white',
                                        height=300
                                    )
                                    st.plotly_chart(fig_stoch, use_container_width=True)

                                # ATR Chart
                                if 'ATR' in indicators_df.columns:
                                    fig_atr = go.Figure()
                                    fig_atr.add_trace(go.Scatter(
                                        x=indicators_df['timestamp'],
                                        y=indicators_df['ATR'],
                                        mode='lines',
                                        name='ATR',
                                        line=dict(color='purple', width=2),
                                        fill='tozeroy',
                                        fillcolor='rgba(128, 0, 128, 0.1)'
                                    ))
                                    fig_atr.update_layout(
                                        title='Average True Range (ATR) - Volatility Measure',
                                        yaxis_title='ATR ($)',
                                        template='plotly_white',
                                        height=250
                                    )
                                    st.plotly_chart(fig_atr, use_container_width=True)

                            with chart_col2:
                                # ADX Chart
                                if 'ADX' in indicators_df.columns:
                                    fig_adx = go.Figure()
                                    fig_adx.add_trace(go.Scatter(
                                        x=indicators_df['timestamp'],
                                        y=indicators_df['ADX'],
                                        mode='lines',
                                        name='ADX',
                                        line=dict(color='darkgreen', width=2.5)
                                    ))
                                    # Add DI+ and DI- if available
                                    if 'DI_plus' in indicators_df.columns:
                                        fig_adx.add_trace(go.Scatter(
                                            x=indicators_df['timestamp'],
                                            y=indicators_df['DI_plus'],
                                            mode='lines',
                                            name='DI+',
                                            line=dict(color='green', width=1.5)
                                        ))
                                    if 'DI_minus' in indicators_df.columns:
                                        fig_adx.add_trace(go.Scatter(
                                            x=indicators_df['timestamp'],
                                            y=indicators_df['DI_minus'],
                                            mode='lines',
                                            name='DI-',
                                            line=dict(color='red', width=1.5)
                                        ))
                                    # Strong trend line
                                    fig_adx.add_hline(y=25, line_dash="dash", line_color="orange", annotation_text="Strong Trend Threshold")
                                    fig_adx.update_layout(
                                        title='ADX - Trend Strength Indicator',
                                        yaxis=dict(range=[0, 100]),
                                        template='plotly_white',
                                        height=300
                                    )
                                    st.plotly_chart(fig_adx, use_container_width=True)

                                # OBV Chart
                                if 'OBV' in indicators_df.columns:
                                    fig_obv = go.Figure()
                                    fig_obv.add_trace(go.Scatter(
                                        x=indicators_df['timestamp'],
                                        y=indicators_df['OBV'],
                                        mode='lines',
                                        name='OBV',
                                        line=dict(color='teal', width=2),
                                        fill='tozeroy',
                                        fillcolor='rgba(0, 128, 128, 0.1)'
                                    ))
                                    fig_obv.update_layout(
                                        title='On-Balance Volume (OBV) - Volume Flow',
                                        yaxis_title='OBV',
                                        template='plotly_white',
                                        height=250
                                    )
                                    st.plotly_chart(fig_obv, use_container_width=True)

                            # Advanced indicators explanation
                            with st.expander("ℹ️ Understanding Advanced Indicators"):
                                st.markdown("""
                                **Advanced Technical Indicators** provide deeper market insights:

                                **Stochastic Oscillator (%K and %D)**:
                                - Momentum indicator showing where price is in recent range
                                - %K (fast line) = Current momentum
                                - %D (slow line) = Moving average of %K
                                - Above 80 = OVERBOUGHT (may drop soon)
                                - Below 20 = OVERSOLD (may rise soon)
                                - When %K crosses above %D = Buy signal
                                - When %K crosses below %D = Sell signal

                                **ADX (Average Directional Index)**:
                                - Measures STRENGTH of trend, not direction
                                - 0-20 = Weak or no trend (ranging market)
                                - 20-40 = Emerging trend
                                - 40-60 = Strong trend (follow it!)
                                - 60+ = Very strong trend (but may be exhausted)
                                - DI+ > DI- = Uptrend | DI- > DI+ = Downtrend

                                **ATR (Average True Range)**:
                                - Measures volatility (price movement range)
                                - Higher ATR = More volatile (bigger swings)
                                - Lower ATR = Less volatile (calmer)
                                - Use 2x ATR for stop-loss distance
                                - Rising ATR = Increasing volatility
                                - Falling ATR = Decreasing volatility

                                **OBV (On-Balance Volume)**:
                                - Cumulative volume flow indicator
                                - RISING = Money flowing INTO the asset (bullish)
                                - FALLING = Money flowing OUT of the asset (bearish)
                                - DIVERGENCE = OBV and price disagree (reversal signal)
                                - OBV leads price - watch for early signals

                                **Trading Tips**:
                                - Use ADX to confirm trend strength before entering
                                - Use Stochastic for timing entries (buy oversold, sell overbought)
                                - Use ATR to set appropriate stop-loss distances
                                - Use OBV to confirm price trends with volume
                                - Combine multiple indicators for higher confidence
                                """)
                        else:
                            st.info("Advanced indicators not available for this dataset")

                    # Pattern Recognition Section
                    if 'pattern_recognition' in indicators:
                        st.markdown("---")
                        st.subheader("🔍 Pattern Recognition")

                        patterns = indicators['pattern_recognition']

                        if 'error' not in patterns:
                            # Count patterns
                            price_patterns = patterns.get('price_patterns', [])
                            chart_patterns = patterns.get('chart_patterns', [])
                            total_patterns = len(price_patterns) + len(chart_patterns)

                            if total_patterns > 0:
                                # Summary metrics
                                col1, col2, col3, col4 = st.columns(4)

                                with col1:
                                    st.metric("Total Patterns", total_patterns)

                                with col2:
                                    bullish_count = sum(1 for p in price_patterns + chart_patterns if p.get('signal') == 'BULLISH')
                                    st.metric("Bullish Patterns", bullish_count)
                                    if bullish_count > 0:
                                        st.caption("🟢 Upward signals")

                                with col3:
                                    bearish_count = sum(1 for p in price_patterns + chart_patterns if p.get('signal') == 'BEARISH')
                                    st.metric("Bearish Patterns", bearish_count)
                                    if bearish_count > 0:
                                        st.caption("🔴 Downward signals")

                                with col4:
                                    neutral_count = sum(1 for p in price_patterns + chart_patterns if p.get('signal') == 'NEUTRAL')
                                    st.metric("Neutral Patterns", neutral_count)
                                    if neutral_count > 0:
                                        st.caption("⚪ No clear direction")

                                # Display patterns in columns
                                pattern_col1, pattern_col2 = st.columns(2)

                                with pattern_col1:
                                    # Price Patterns
                                    if price_patterns:
                                        st.markdown("**📈 Price Patterns**")
                                        for pattern in price_patterns:
                                            signal = pattern.get('signal', 'NEUTRAL')
                                            pattern_type = pattern.get('type', 'Unknown')
                                            confidence = pattern.get('confidence', 0)
                                            description = pattern.get('description', '')

                                            # Color-code by signal
                                            if signal == 'BULLISH':
                                                st.success(f"**{pattern_type}** 🟢 BULLISH")
                                            elif signal == 'BEARISH':
                                                st.error(f"**{pattern_type}** 🔴 BEARISH")
                                            else:
                                                st.info(f"**{pattern_type}** ⚪ NEUTRAL")

                                            st.caption(f"Confidence: {confidence:.0f}% | {description}")
                                            st.write("")
                                    else:
                                        st.info("No price patterns detected")

                                with pattern_col2:
                                    # Chart Patterns
                                    if chart_patterns:
                                        st.markdown("**📊 Chart Patterns**")
                                        for pattern in chart_patterns:
                                            signal = pattern.get('signal', 'NEUTRAL')
                                            pattern_type = pattern.get('type', 'Unknown')
                                            confidence = pattern.get('confidence', 0)
                                            description = pattern.get('description', '')

                                            # Color-code by signal
                                            if signal == 'BULLISH':
                                                st.success(f"**{pattern_type}** 🟢 BULLISH")
                                            elif signal == 'BEARISH':
                                                st.error(f"**{pattern_type}** 🔴 BEARISH")
                                            else:
                                                st.info(f"**{pattern_type}** ⚪ NEUTRAL")

                                            st.caption(f"Confidence: {confidence:.0f}% | {description}")
                                            st.write("")
                                    else:
                                        st.info("No chart patterns detected")

                                # Pattern recognition explanation
                                with st.expander("ℹ️ Understanding Pattern Recognition"):
                                    st.markdown("""
                                    **Pattern Recognition** identifies recurring price formations that often lead to predictable outcomes:

                                    **Price Patterns** (Candlestick/Price Action):
                                    - **Higher Highs/Lows**: Uptrend - each peak and valley is higher than the last
                                    - **Lower Highs/Lows**: Downtrend - each peak and valley is lower than the last
                                    - **Doji**: Indecision - opening and closing prices nearly equal
                                    - **Hammer/Shooting Star**: Reversal signals after trends
                                    - **Engulfing**: Strong reversal pattern when one candle engulfs the previous

                                    **Chart Patterns** (Formations):
                                    - **Head & Shoulders**: Bearish reversal - three peaks with middle highest
                                    - **Inverse H&S**: Bullish reversal - three valleys with middle lowest
                                    - **Double Top/Bottom**: Reversal patterns at resistance/support
                                    - **Triangle**: Consolidation before breakout (ascending = bullish, descending = bearish)
                                    - **Channel**: Parallel support and resistance (trade within bounds)
                                    - **Flags/Pennants**: Continuation patterns - brief pause before trend resumes
                                    - **Cup & Handle**: Bullish continuation - rounded bottom with consolidation

                                    **How to Use Patterns**:
                                    1. **Reversal Patterns**: Signal trend change - consider exiting current position
                                    2. **Continuation Patterns**: Signal trend will resume - stay in position
                                    3. **Confirmation**: Wait for breakout/breakdown to confirm the pattern
                                    4. **Volume**: Patterns with high volume are more reliable
                                    5. **Multiple Patterns**: More patterns = stronger signal

                                    **Important Notes**:
                                    - Patterns are NOT guarantees - they show probability
                                    - Higher confidence patterns are more reliable
                                    - Combine with indicators for better accuracy
                                    - Always use stop-losses with pattern trading
                                    - Some patterns fail - manage your risk!
                                    """)
                            else:
                                st.info("No significant patterns detected in current timeframe")
                        else:
                            st.info("Pattern recognition not available for this dataset")

                    # Multi-Timeframe Analysis Section
                    # This requires market_context which is fetched during recommendation generation
                    if 'cached_market_context' in st.session_state:
                        market_ctx = st.session_state.cached_market_context
                        if market_ctx and 'timeframe_analysis' in market_ctx:
                            st.markdown("---")
                            st.subheader("🕐 Multi-Timeframe Analysis")

                            tf_analysis = market_ctx['timeframe_analysis']
                            timeframes = tf_analysis.get('timeframes', {})
                            alignment = tf_analysis.get('alignment', {})

                            # Alignment score visualization
                            col1, col2 = st.columns([1, 3])

                            with col1:
                                # Alignment score gauge
                                score = alignment.get('score', 0)
                                st.metric("Timeframe Alignment", f"{score:.0f}/100")

                                # Color-coded assessment
                                assessment = alignment.get('assessment', '')
                                if 'PERFECT_BULLISH' in assessment or score >= 80:
                                    st.success("🟢 Strong alignment")
                                elif 'PERFECT_BEARISH' in assessment or score >= 80:
                                    st.error("🔴 Strong alignment")
                                elif score >= 60:
                                    st.warning("🟡 Moderate alignment")
                                else:
                                    st.info("⚪ Mixed signals")

                                st.caption(f"{alignment.get('bullish_timeframes', 0)} bullish, {alignment.get('bearish_timeframes', 0)} bearish, {alignment.get('neutral_timeframes', 0)} neutral")

                            with col2:
                                st.write(alignment.get('recommendation', 'Analyzing timeframes...'))

                            # Timeframe comparison table
                            st.markdown("**Timeframe Breakdown:**")

                            tf_data = []
                            for tf_name in sorted(timeframes.keys()):
                                tf = timeframes[tf_name]
                                if 'error' not in tf:
                                    tf_data.append({
                                        'Timeframe': tf_name,
                                        'Signal': tf.get('overall_signal', 'N/A'),
                                        'Confidence': f"{tf.get('confidence', 0):.0f}%",
                                        'Trend': tf.get('trend', 'N/A'),
                                        'Change': f"{tf.get('price_change_pct', 0):+.1f}%",
                                        'Volatility': f"{tf.get('volatility', 0):.1f}%"
                                    })

                            if tf_data:
                                tf_df = pd.DataFrame(tf_data)

                                # Color code the dataframe
                                def color_signal(val):
                                    if val == 'BULLISH':
                                        return 'background-color: #d4edda; color: #155724'
                                    elif val == 'BEARISH':
                                        return 'background-color: #f8d7da; color: #721c24'
                                    else:
                                        return 'background-color: #fff3cd; color: #856404'

                                styled_df = tf_df.style.applymap(color_signal, subset=['Signal'])
                                st.dataframe(styled_df, use_container_width=True, hide_index=True)

                            # Visual chart - Timeframe signal strength
                            if tf_data:
                                fig_tf = go.Figure()

                                timeframe_names = [d['Timeframe'] for d in tf_data]
                                confidences = [float(d['Confidence'].replace('%', '')) for d in tf_data]
                                signals = [d['Signal'] for d in tf_data]

                                # Color by signal
                                colors = ['green' if s == 'BULLISH' else 'red' if s == 'BEARISH' else 'gray' for s in signals]

                                fig_tf.add_trace(go.Bar(
                                    x=timeframe_names,
                                    y=confidences,
                                    marker_color=colors,
                                    text=[f"{s}<br>{c}%" for s, c in zip(signals, confidences)],
                                    textposition='auto',
                                    hovertemplate='<b>%{x}</b><br>Signal: %{text}<extra></extra>'
                                ))

                                fig_tf.update_layout(
                                    title='Signal Confidence Across Timeframes',
                                    xaxis_title='Timeframe',
                                    yaxis_title='Confidence (%)',
                                    yaxis=dict(range=[0, 100]),
                                    template='plotly_white',
                                    height=300
                                )
                                st.plotly_chart(fig_tf, use_container_width=True)

                            # Multi-timeframe explanation
                            with st.expander("ℹ️ Understanding Multi-Timeframe Analysis"):
                                st.markdown("""
                                **Multi-Timeframe Analysis** examines the crypto across different time periods to find signal alignment:

                                **Why Multiple Timeframes Matter**:
                                - **Short-term (7 days)**: Day trading, scalping signals
                                - **Medium-term (30 days)**: Swing trading, weekly trends
                                - **Long-term (90 days)**: Position trading, major trends
                                - **Alignment = Conviction**: When all timeframes agree, the signal is stronger

                                **Alignment Score**:
                                - **100/100**: Perfect alignment - ALL timeframes show same signal (very strong!)
                                - **66-80**: Majority alignment - 2 out of 3 agree (moderately strong)
                                - **50 or below**: Mixed signals - conflicting timeframes (be cautious!)

                                **How to Use This**:
                                1. **Perfect Alignment (100)**: Highest conviction trades - all timeframes agree
                                   - Example: All 3 bullish = Strong buy signal
                                   - Example: All 3 bearish = Strong sell signal

                                2. **Majority Alignment (66-80)**: Good trades but watch for conflicts
                                   - Example: 7d & 30d bullish, 90d bearish = Short-term rally in long-term downtrend
                                   - Strategy: Trade the short-term but be ready to exit

                                3. **Mixed Signals (50 or below)**: Proceed with caution
                                   - Conflicting timeframes = unclear direction
                                   - Wait for better alignment or use smaller position size

                                **Trading Strategy**:
                                - Use **long-term** (90d) for overall direction
                                - Use **medium-term** (30d) for swing trade entries
                                - Use **short-term** (7d) for precise entry timing
                                - Best trades = When all three align in same direction

                                **Example Scenarios**:
                                - All bullish (100 score) = Very strong uptrend, high conviction buy
                                - 7d bullish, 30d/90d bearish = Bear market rally, risky to buy
                                - 7d bearish, 30d/90d bullish = Healthy pullback, potential buy opportunity
                                """)

                    # Market Context Dashboard Section
                    # This also requires market_context from session state
                    if 'cached_market_context' in st.session_state:
                        market_ctx = st.session_state.cached_market_context
                        if market_ctx:
                            st.markdown("---")
                            st.subheader("🌍 Market Context & Sentiment")

                            context_col1, context_col2 = st.columns(2)

                            with context_col1:
                                # BTC Correlation
                                if 'btc_correlation' in market_ctx and 'note' not in market_ctx['btc_correlation']:
                                    st.markdown("**₿ Bitcoin Correlation**")

                                    btc_corr = market_ctx['btc_correlation']
                                    correlation = btc_corr.get('correlation', 0)
                                    strength = btc_corr.get('strength', 'N/A')
                                    direction = btc_corr.get('direction', 'N/A')

                                    # Correlation gauge
                                    col_a, col_b = st.columns([1, 2])

                                    with col_a:
                                        st.metric("Correlation", f"{correlation:.2f}")
                                        st.caption(f"{strength} {direction}")

                                    with col_b:
                                        # Visual correlation gauge
                                        fig_corr = go.Figure(go.Indicator(
                                            mode="gauge+number",
                                            value=abs(correlation) * 100,
                                            domain={'x': [0, 1], 'y': [0, 1]},
                                            title={'text': "Correlation Strength"},
                                            gauge={
                                                'axis': {'range': [0, 100]},
                                                'bar': {'color': "darkblue"},
                                                'steps': [
                                                    {'range': [0, 20], 'color': "lightgray"},
                                                    {'range': [20, 40], 'color': "lightyellow"},
                                                    {'range': [40, 60], 'color': "lightblue"},
                                                    {'range': [60, 80], 'color': "lightcoral"},
                                                    {'range': [80, 100], 'color': "salmon"}
                                                ],
                                                'threshold': {
                                                    'line': {'color': "red", 'width': 4},
                                                    'thickness': 0.75,
                                                    'value': 70
                                                }
                                            }
                                        ))
                                        fig_corr.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
                                        st.plotly_chart(fig_corr, use_container_width=True)

                                    # Recommendation
                                    recommendation = btc_corr.get('recommendation', '')
                                    if abs(correlation) > 0.7:
                                        st.warning(recommendation)
                                    elif abs(correlation) > 0.4:
                                        st.info(recommendation)
                                    else:
                                        st.success(recommendation)

                                    # Explanation
                                    with st.expander("ℹ️ What does BTC correlation mean?"):
                                        st.markdown("""
                                        **Bitcoin Correlation** measures how closely this crypto moves with Bitcoin:

                                        **Correlation Ranges**:
                                        - **> 0.8**: VERY STRONG - Crypto moves almost identically with BTC
                                        - **0.6 - 0.8**: STRONG - Crypto mostly follows BTC movements
                                        - **0.4 - 0.6**: MODERATE - Some relationship with BTC
                                        - **0.2 - 0.4**: WEAK - Slight relationship with BTC
                                        - **< 0.2**: VERY WEAK - Independent from BTC

                                        **Positive vs Negative**:
                                        - POSITIVE (+): Moves WITH Bitcoin (most common)
                                        - NEGATIVE (-): Moves OPPOSITE to Bitcoin (rare!)

                                        **Trading Implications**:
                                        - **High Correlation (>0.7)**: Watch BTC first! If BTC is bearish, even strong altcoin signals may fail
                                        - **Low Correlation (<0.3)**: Independent mover - can trade based on crypto's own signals
                                        - **Negative Correlation**: Inverse play - rises when BTC falls (very rare)

                                        **Important**: Most altcoins have high BTC correlation (0.7-0.9). This means:
                                        - BTC drives the market
                                        - Check BTC trend before entering altcoin trades
                                        - When BTC crashes, altcoins usually crash harder
                                        - When BTC rallies, altcoins often rally stronger
                                        """)

                            with context_col2:
                                # Market Regime (Fear & Greed)
                                if 'market_regime' in market_ctx:
                                    st.markdown("**😱 Market Sentiment (Fear & Greed)**")

                                    regime = market_ctx['market_regime']
                                    fng_value = regime.get('fear_greed')

                                    if fng_value is not None:
                                        # Fear & Greed gauge
                                        col_a, col_b = st.columns([1, 2])

                                        with col_a:
                                            st.metric("Index", f"{fng_value}/100")
                                            st.caption(regime.get('sentiment', 'N/A'))

                                        with col_b:
                                            # Visual fear & greed gauge
                                            fig_fng = go.Figure(go.Indicator(
                                                mode="gauge+number",
                                                value=fng_value,
                                                domain={'x': [0, 1], 'y': [0, 1]},
                                                title={'text': "Fear & Greed Index"},
                                                gauge={
                                                    'axis': {'range': [0, 100]},
                                                    'bar': {'color': "darkgreen" if fng_value < 40 else "red" if fng_value > 60 else "gray"},
                                                    'steps': [
                                                        {'range': [0, 20], 'color': "darkred", 'name': 'Extreme Fear'},
                                                        {'range': [20, 40], 'color': "red", 'name': 'Fear'},
                                                        {'range': [40, 60], 'color': "gray", 'name': 'Neutral'},
                                                        {'range': [60, 80], 'color': "lightgreen", 'name': 'Greed'},
                                                        {'range': [80, 100], 'color': "darkgreen", 'name': 'Extreme Greed'}
                                                    ],
                                                    'threshold': {
                                                        'line': {'color': "black", 'width': 4},
                                                        'thickness': 0.75,
                                                        'value': fng_value
                                                    }
                                                }
                                            ))
                                            fig_fng.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
                                            st.plotly_chart(fig_fng, use_container_width=True)

                                        # Regime recommendation
                                        regime_name = regime.get('regime', '')
                                        recommendation = regime.get('recommendation', '')

                                        if 'EXTREME_FEAR' in regime_name:
                                            st.success(recommendation)
                                        elif 'FEAR' in regime_name:
                                            st.info(recommendation)
                                        elif 'EXTREME_GREED' in regime_name:
                                            st.error(recommendation)
                                        elif 'GREED' in regime_name:
                                            st.warning(recommendation)
                                        else:
                                            st.info(recommendation)

                                        # Position sizing and strategy
                                        st.write(f"**Position Sizing**: {regime.get('position_sizing', 'N/A')}")
                                        st.write(f"**Strategy**: {regime.get('strategy', 'N/A')}")

                                        # Explanation
                                        with st.expander("ℹ️ How to use Fear & Greed Index?"):
                                            st.markdown("""
                                            **Fear & Greed Index** measures overall crypto market sentiment from 0-100:

                                            **The 5 Market Regimes**:

                                            1. **Extreme Fear (<20)** 💰:
                                               - Market in panic mode
                                               - **Strategy**: CONTRARIAN BUY - "Be greedy when others are fearful"
                                               - **Position Size**: INCREASE - Best entry opportunities
                                               - **History**: Major market bottoms occur in extreme fear

                                            2. **Fear (20-40)** ✅:
                                               - Market nervous but not panicking
                                               - **Strategy**: BUY ZONE - Good entry prices
                                               - **Position Size**: NORMAL to INCREASE
                                               - **Approach**: Buy dips, dollar-cost averaging (DCA)

                                            3. **Neutral (40-60)** ➖:
                                               - Market balanced, no extreme sentiment
                                               - **Strategy**: Follow technical signals
                                               - **Position Size**: NORMAL
                                               - **Approach**: Regular trading based on analysis

                                            4. **Greed (60-80)** ⚠️:
                                               - Market getting heated
                                               - **Strategy**: CAUTION - Take some profits
                                               - **Position Size**: REDUCE exposure
                                               - **Approach**: Scale out, tighten stop-losses

                                            5. **Extreme Greed (>80)** 🔴:
                                               - Market euphoric, FOMO in full swing
                                               - **Strategy**: SELL ZONE - Correction likely
                                               - **Position Size**: MINIMIZE exposure
                                               - **History**: Major market tops occur in extreme greed

                                            **Key Principle**: Be a **CONTRARIAN**
                                            - Buy when others are fearful (low index)
                                            - Sell when others are greedy (high index)
                                            - "The best time to buy is when there's blood in the streets"

                                            **Risk Management**:
                                            - Extreme Fear = Increase position sizes (buy the fear)
                                            - Extreme Greed = Decrease position sizes (sell the greed)
                                            - This adjusts your risk based on market conditions
                                            """)
                                    else:
                                        st.info("Fear & Greed Index data not available")

            # Section 3: Recent News & Sentiment
            st.markdown("---")
            st.subheader("📰 Recent News & Sentiment Analysis")

            # Fetch news only if fresh analysis
            if not st.session_state.analysis_complete:
                articles = news_fetcher.get_crypto_news(crypto_symbol, hours_back=48)
                st.session_state.cached_articles = articles
            else:
                articles = st.session_state.get('cached_articles', [])

            if articles:
                st.write(f"Found {len(articles)} recent articles")

                # Sentiment analysis if API key available
                if os.getenv('OPENAI_API_KEY'):
                    # Only run sentiment analysis if fresh analysis
                    if not st.session_state.analysis_complete:
                        with st.spinner("Analyzing sentiment..."):
                            try:
                                # Use selected model (or default if not set)
                                model_to_use = selected_model if 'selected_model' in locals() else 'gpt-4o-mini'
                                analyzer = CryptoSentimentAnalyzer(model=model_to_use)
                                analyzed = analyzer.analyze_news_batch(articles, crypto_symbol, max_articles=10)
                                overall = analyzer.get_overall_sentiment(analyzed)

                                # Cache the sentiment results
                                st.session_state.cached_analyzed = analyzed
                                st.session_state.cached_overall = overall
                            except Exception as e:
                                st.error(f"Sentiment analysis failed: {e}")
                                analyzed = []
                                overall = None
                    else:
                        # Use cached sentiment analysis
                        analyzed = st.session_state.get('cached_analyzed', [])
                        overall = st.session_state.get('cached_overall')

                    if analyzed and overall:
                        # Overall sentiment display
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            sentiment_class = "bullish-sentiment" if overall['avg_score'] > 0 else "bearish-sentiment"
                            st.markdown(f"<p class='{sentiment_class}'>{overall['sentiment_label']}</p>",
                                      unsafe_allow_html=True)
                            st.metric("Sentiment Score", f"{overall['avg_score']:.1f}/10")

                        with col2:
                            st.metric("Bullish Articles", overall['bullish_count'])

                        with col3:
                            st.metric("Bearish Articles", overall['bearish_count'])

                        with col4:
                            if overall['critical_count'] > 0:
                                st.metric("Critical News", overall['critical_count'])
                                st.error("⚠️ Critical events detected")
                            else:
                                st.metric("Critical News", 0)

                        # Top articles
                        st.markdown("**Top Recent Articles:**")
                        for i, article in enumerate(analyzed[:5], 1):
                            sentiment = article['sentiment']
                            sentiment_emoji = "🟢" if sentiment['score'] > 3 else "🔴" if sentiment['score'] < -3 else "⚪"

                            with st.expander(f"{sentiment_emoji} {article['title']} ({sentiment['score']:+.1f})"):
                                st.write(f"**Published:** {article['published'].strftime('%Y-%m-%d %H:%M')}")
                                st.write(f"**Source:** {article.get('source_name', 'Unknown')}")
                                st.write(f"**Sentiment:** {sentiment['label']} - {sentiment['explanation']}")
                                st.write(f"**Link:** {article['link']}")

                                # Flags
                                if sentiment['flags']['hack']:
                                    st.error("⚠️ Security/Hack Alert")
                                if sentiment['flags']['regulation']:
                                    st.warning("⚖️ Regulation News")
                                if sentiment['flags']['adoption']:
                                    st.success("🚀 Adoption News")
                                if sentiment['flags']['tech']:
                                    st.info("🔧 Technical Update")
                else:
                    st.info("Set OPENAI_API_KEY for sentiment analysis")
                    for article in articles[:5]:
                        with st.expander(article['title']):
                            st.write(f"**Published:** {article['published'].strftime('%Y-%m-%d %H:%M')}")
                            st.write(f"**Source:** {article.get('source_name', 'Unknown')}")
                            st.write(f"**Link:** {article['link']}")
            else:
                st.warning("No recent news found")

            # Section 4: On-Chain Metrics
            st.markdown("---")
            st.subheader("🔗 On-Chain & Social Metrics")

            # Fetch on-chain data only if fresh analysis
            if not st.session_state.analysis_complete:
                on_chain = client.get_on_chain_metrics(crypto_id)
                st.session_state.cached_on_chain = on_chain
            else:
                on_chain = st.session_state.get('cached_on_chain')

            if on_chain:
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Social Metrics**")
                    if on_chain['twitter_followers']:
                        st.metric("Twitter Followers", f"{on_chain['twitter_followers']:,}")
                    if on_chain['reddit_subscribers']:
                        st.metric("Reddit Subscribers", f"{on_chain['reddit_subscribers']:,}")
                    if on_chain['reddit_active_48h']:
                        st.metric("Reddit Active (48h)", f"{on_chain['reddit_active_48h']:,}")

                with col2:
                    st.write("**Development Activity**")
                    if on_chain['github_stars']:
                        st.metric("GitHub Stars", f"{on_chain['github_stars']:,}")
                    if on_chain['commit_count_4_weeks']:
                        st.metric("Commits (4 weeks)", f"{on_chain['commit_count_4_weeks']:,}")
                        if on_chain['commit_count_4_weeks'] > 500:
                            st.success("🔥 High development activity")
                    if on_chain['pull_requests_merged']:
                        st.metric("PRs Merged", f"{on_chain['pull_requests_merged']:,}")

            # Section 5: Risk Assessment Summary
            st.markdown("---")
            st.subheader("⚠️ Risk Assessment Summary")

            risk_factors = []

            # Volatility check
            if hist_df is not None and not hist_df.empty:
                volatility_pct = (hist_df['price'].std() / hist_df['price'].mean() * 100)
                if volatility_pct > 15:
                    risk_factors.append(f"High volatility: {volatility_pct:.1f}% standard deviation")

            # Price decline check
            if market_data:
                if market_data['price_change_percentage_24h'] < -10:
                    risk_factors.append(f"Significant 24h decline: {market_data['price_change_percentage_24h']:.1f}%")
                if market_data['price_change_percentage_7d'] < -20:
                    risk_factors.append(f"Sharp weekly decline: {market_data['price_change_percentage_7d']:.1f}%")

            # Sentiment check
            critical_news = []
            if os.getenv('OPENAI_API_KEY') and articles:
                try:
                    if overall['avg_score'] < -5:
                        risk_factors.append(f"Very negative news sentiment: {overall['avg_score']:.1f}/10")
                    if overall['critical_count'] > 0:
                        risk_factors.append(f"{overall['critical_count']} critical news event(s) detected")

                        # Extract critical news articles
                        if 'analyzed' in locals() and analyzed:
                            critical_news = [
                                article for article in analyzed
                                if article.get('sentiment', {}).get('flags', {}).get('hack', False) or
                                   article.get('sentiment', {}).get('flags', {}).get('regulation', False) or
                                   article.get('sentiment', {}).get('score', 0) < -7
                            ]
                except:
                    pass

            if risk_factors:
                st.warning("**Risk Factors Identified:**")
                for factor in risk_factors:
                    st.write(f"- {factor}")

                # Show critical news details
                if critical_news:
                    st.markdown("**Critical News Events:**")
                    for article in critical_news[:5]:  # Show top 5 critical news
                        sentiment = article.get('sentiment', {})
                        score = sentiment.get('score', 0)
                        flags = sentiment.get('flags', {})

                        # Build flag indicators
                        flag_indicators = []
                        if flags.get('hack'):
                            flag_indicators.append("🚨 Security/Hack")
                        if flags.get('regulation'):
                            flag_indicators.append("⚖️ Regulation")

                        flag_text = " | ".join(flag_indicators) if flag_indicators else "⚠️ Critical"

                        st.write(f"  - **{article['title']}**")
                        st.caption(f"    {flag_text} | Sentiment: {score:.1f}/10 | {article['published'].strftime('%Y-%m-%d %H:%M')}")
                        if sentiment.get('explanation'):
                            st.caption(f"    _{sentiment['explanation']}_")
                        st.write("")
            else:
                st.success("✅ No major risk factors detected")

            # Section 6: AI Trading Recommendation
            st.markdown("---")
            st.subheader("🤖 AI Trading Recommendation")

            if os.getenv('OPENAI_API_KEY') and market_data:
                # Only generate recommendation if fresh analysis
                if not st.session_state.analysis_complete:
                    with st.spinner("Generating trading recommendation..."):
                        try:
                            from src.llm.trading_advisor import TradingAdvisor

                            # Use selected model for trading advice (default to gpt-4o for better reasoning)
                            advisor_model = selected_model if 'selected_model' in locals() else 'gpt-4o'
                            advisor = TradingAdvisor(model=advisor_model)

                            # Prepare news summary (handle case where no articles found)
                            if articles and len(articles) > 0:
                                news_summary = f"{len(articles)} articles analyzed"
                                if 'overall' in locals() and overall:
                                    news_summary += f" - Overall sentiment: {overall['sentiment_label']} ({overall['avg_score']:.1f}/10)"
                            else:
                                news_summary = "No recent news articles available for analysis"

                            # Get sentiment score (default to 0 if no sentiment data)
                            sentiment_score = overall['avg_score'] if 'overall' in locals() and overall else 0

                            # Get market context (multi-timeframe, BTC correlation, Fear & Greed)
                            try:
                                # Get Fear & Greed Index
                                fng = client.get_fear_greed_index()
                                fng_value = fng['value'] if fng else None

                                # Analyze market context
                                market_context_analyzer = MarketContext(client)
                                market_context = market_context_analyzer.get_comprehensive_context(
                                    crypto_id=crypto_id,
                                    current_period_days=days,
                                    fear_greed_value=fng_value
                                )
                            except Exception as e:
                                st.warning(f"Could not fetch complete market context: {e}")
                                market_context = None

                            # Get recommendation with technical indicators and market context
                            recommendation = advisor.get_trading_recommendation(
                                symbol=crypto_symbol,
                                current_price=market_data['current_price'],
                                market_data=market_data,
                                sentiment_score=sentiment_score,
                                news_summary=news_summary,
                                risk_factors=risk_factors,
                                technical_indicators=indicators,
                                market_context=market_context
                            )

                            # Cache the recommendation and related data
                            st.session_state.cached_recommendation = recommendation
                            st.session_state.cached_advisor_model = advisor_model
                            st.session_state.cached_sentiment_score = sentiment_score
                            st.session_state.cached_news_summary = news_summary
                            st.session_state.cached_risk_factors = risk_factors
                            st.session_state.cached_market_context = market_context
                        except Exception as e:
                            st.error(f"Error generating trading recommendation: {e}")
                            recommendation = None
                else:
                    # Use cached recommendation
                    recommendation = st.session_state.get('cached_recommendation')
                    advisor_model = st.session_state.get('cached_advisor_model', 'gpt-4o')
                    sentiment_score = st.session_state.get('cached_sentiment_score', 0)
                    news_summary = st.session_state.get('cached_news_summary', '')
                    risk_factors = st.session_state.get('cached_risk_factors', [])
                    market_context = st.session_state.get('cached_market_context')

                if recommendation:
                    # Create advisor instance for risk/reward calculation
                    from src.llm.trading_advisor import TradingAdvisor
                    advisor = TradingAdvisor(model=advisor_model)

                    # Display recommendation
                    rec_type = recommendation.get('recommendation', 'HOLD')

                    # Color-coded recommendation
                    if rec_type == 'BUY':
                        st.success(f"### 🟢 RECOMMENDATION: {rec_type}")
                    elif rec_type == 'SELL':
                        st.error(f"### 🔴 RECOMMENDATION: {rec_type}")
                    else:
                        st.info(f"### 🟡 RECOMMENDATION: {rec_type}")

                    # Confidence meter
                    confidence = recommendation.get('confidence', 0)
                    st.progress(confidence / 100)
                    st.write(f"**Confidence Level:** {confidence}%")

                    # Main metrics in columns
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        entry = recommendation.get('entry_price', market_data['current_price'])
                        st.metric("Entry Price", f"${entry:,.2f}")

                    with col2:
                        stop_loss_price = recommendation.get('stop_loss_price', entry * 0.90)
                        stop_loss_pct = recommendation.get('stop_loss_pct', 10.0)
                        st.metric("Stop Loss", f"${stop_loss_price:,.2f}", f"-{stop_loss_pct:.1f}%")

                    with col3:
                        tp1 = recommendation.get('take_profit_1', entry * 1.10)
                        st.metric("Take Profit 1", f"${tp1:,.2f}")

                    with col4:
                        position_size = recommendation.get('position_size', 5.0)
                        st.metric("Position Size", f"{position_size:.1f}%")

                    # Reasoning
                    st.markdown("**Reasoning:**")
                    st.write(recommendation.get('reasoning', 'No reasoning provided'))

                    # Save Recommendation Button
                    st.markdown("---")
                    col_save1, col_save2 = st.columns([1, 3])

                    with col_save1:
                        if st.button("💾 Save Recommendation", type="primary", key="save_rec_btn"):
                            try:
                                from src.backtesting.recommendation_tracker import RecommendationTracker

                                tracker = RecommendationTracker()

                                # Extract technical signals summary
                                tech_signals = {}
                                if indicators:
                                    tech_signals = {
                                        'overall_signal': indicators.get('signals', {}).get('overall', 'NEUTRAL'),
                                        'confidence': indicators.get('signals', {}).get('confidence', 0),
                                        'rsi': indicators.get('rsi', {}).get('value'),
                                        'macd_signal': indicators.get('macd', {}).get('trade_signal'),
                                        'volume_confirmation': indicators.get('volume_analysis', {}).get('confirmation_score', 0)
                                    }

                                # Save recommendation
                                rec_id = tracker.add_recommendation(
                                    crypto_symbol=crypto_symbol,
                                    recommendation_type=rec_type,
                                    entry_price=entry,
                                    current_price=market_data['current_price'],
                                    stop_loss_price=stop_loss_price,
                                    take_profit_1=tp1,
                                    take_profit_2=recommendation.get('take_profit_2'),
                                    position_size_pct=position_size,
                                    confidence=confidence,
                                    reasoning=recommendation.get('reasoning', ''),
                                    technical_signals=tech_signals,
                                    market_context=market_context,
                                    sentiment_score=sentiment_score,
                                    model_used=advisor_model
                                )

                                st.session_state.last_saved_rec_id = rec_id
                                st.success(f"✅ Recommendation saved! ID: {rec_id}")
                                st.info("View it in the '📊 Performance Tracking' page")

                            except Exception as e:
                                st.error(f"Error saving recommendation: {e}")

                    with col_save2:
                        if 'last_saved_rec_id' in st.session_state:
                            st.caption(f"Last saved: {st.session_state.last_saved_rec_id}")

                    # Additional details in expander
                    with st.expander("📋 View Detailed Trading Plan"):
                        st.markdown("**Entry Strategy:**")
                        if rec_type == 'BUY':
                            st.write(f"- Enter at current market price: ${entry:,.2f}")
                            st.write(f"- Or wait for dip to: ${entry * 0.98:,.2f} (2% lower)")
                        else:
                            st.write("- N/A (Not a buy recommendation)")

                        st.markdown("**Exit Strategy:**")
                        st.write(f"- Stop Loss: ${stop_loss_price:,.2f} ({stop_loss_pct:.1f}% risk)")
                        if 'take_profit_1' in recommendation:
                            st.write(f"- Take Profit 1 (50%): ${recommendation['take_profit_1']:,.2f}")
                        if 'take_profit_2' in recommendation:
                            st.write(f"- Take Profit 2 (50%): ${recommendation['take_profit_2']:,.2f}")

                        st.markdown("**Risk/Reward Analysis:**")
                        if rec_type == 'BUY' and 'take_profit_1' in recommendation:
                            rr = advisor.get_risk_reward_analysis(
                                entry,
                                stop_loss_price,
                                recommendation['take_profit_1']
                            )
                            st.write(f"- Risk: ${rr['risk_amount']:,.2f} ({rr['risk_pct']:.1f}%)")
                            st.write(f"- Reward: ${rr['reward_amount']:,.2f} ({rr['reward_pct']:.1f}%)")
                            st.write(f"- Risk/Reward Ratio: 1:{rr['risk_reward_ratio']:.2f}")
                            if rr['is_favorable']:
                                st.success("✅ Favorable risk/reward ratio (>2:1)")
                            else:
                                st.warning("⚠️ Risk/reward ratio below 2:1")

                        st.markdown("**Position Sizing:**")
                        st.write(f"- Recommended allocation: {position_size:.1f}% of portfolio")
                        portfolio_value = st.number_input("Your portfolio value ($)", value=10000, step=1000)
                        position_value = portfolio_value * (position_size / 100)
                        st.write(f"- Position size: ${position_value:,.2f}")
                        if entry > 0:
                            units = position_value / entry
                            st.write(f"- Units to buy: {units:.4f} {crypto_symbol}")

                        st.markdown("**Time Horizon:**")
                        st.write(f"- {recommendation.get('time_horizon', 'Not specified')}")

                        st.markdown("**Key Risks to Monitor:**")
                        key_risks = recommendation.get('key_risks', [])
                        for risk in key_risks:
                            st.write(f"- {risk}")

                        st.markdown("**Invalidation Criteria:**")
                        st.write(recommendation.get('invalidation', 'Not specified'))
                        st.caption("If this condition occurs, exit the position immediately.")

                    # Important disclaimer
                    st.error("""
                    ⚠️ **IMPORTANT DISCLAIMER**

                    This is AI-generated advice for informational and educational purposes only.
                    - NOT financial advice
                    - Past performance does not guarantee future results
                    - Cryptocurrency is highly volatile and risky
                    - Only invest what you can afford to lose
                    - Always do your own research (DYOR)
                    - Consult a licensed financial advisor before investing

                    The AI model may make mistakes or provide incorrect analysis.
                    """)

                    # Mark analysis as complete (prevents re-fetching on Q&A reruns)
                    st.session_state.analysis_complete = True

                    # Interactive Q&A Section
                    st.markdown("---")
                    st.subheader("💬 Ask Follow-up Questions")
                    st.caption("Ask the AI to explain or clarify any aspect of the recommendation")

                    # Create unique key for this analysis
                    analysis_key = f"{crypto_symbol}_{market_data['current_price']:.0f}"

                    # Initialize conversation history in session state
                    if 'conversation_history' not in st.session_state:
                        st.session_state.conversation_history = {}

                    if 'current_analysis_key' not in st.session_state:
                        st.session_state.current_analysis_key = None

                    # Check if this is a new analysis
                    if st.session_state.current_analysis_key != analysis_key:
                        st.session_state.current_analysis_key = analysis_key
                        st.session_state.conversation_history[analysis_key] = []

                        # Store the recommendation context
                        st.session_state.recommendation_context = {
                            'symbol': crypto_symbol,
                            'recommendation': recommendation,
                            'market_data': market_data,
                            'sentiment_score': sentiment_score,
                            'news_summary': news_summary,
                            'risk_factors': risk_factors,
                            'model': advisor_model
                        }

                    # Get current conversation history
                    current_history = st.session_state.conversation_history.get(analysis_key, [])

                    # Display conversation history
                    if current_history:
                        st.markdown("**Previous Q&A:**")
                        for qa in current_history:
                            with st.chat_message("user"):
                                st.write(qa['question'])
                            with st.chat_message("assistant"):
                                st.write(qa['answer'])

                    # Question input form to prevent rerun on button click
                    with st.form(key="qa_form", clear_on_submit=True):
                        user_question = st.text_area(
                            "Your question:",
                            placeholder="e.g., Why is the stop loss at this level? What if the price drops 20%? Should I buy now or wait?",
                            height=80,
                            key="question_input"
                        )

                        col1, col2 = st.columns([1, 5])
                        with col1:
                            ask_button = st.form_submit_button("Ask AI", type="primary")
                        with col2:
                            clear_button = st.form_submit_button("Clear History")

                    # Handle clear history
                    if clear_button:
                        st.session_state.conversation_history[analysis_key] = []
                        st.success("Conversation history cleared!")

                    # Handle question submission
                    if ask_button and user_question:
                        with st.spinner("Thinking..."):
                            try:
                                # Build context for the question
                                context = st.session_state.recommendation_context
                                rec = context['recommendation']

                                # Build conversation context
                                conversation_context = f"""You are a cryptocurrency trading advisor. You previously provided this trading recommendation:

CRYPTOCURRENCY: {context['symbol']}
CURRENT PRICE: ${context['market_data']['current_price']:,.2f}

YOUR RECOMMENDATION: {rec.get('recommendation', 'N/A')}
CONFIDENCE: {rec.get('confidence', 0)}%
REASONING: {rec.get('reasoning', 'N/A')}

ENTRY PRICE: ${rec.get('entry_price', 0):,.2f}
STOP LOSS: {rec.get('stop_loss_pct', 0):.1f}% (${rec.get('stop_loss_price', 0):,.2f})
TAKE PROFIT 1: ${rec.get('take_profit_1', 0):,.2f}
TAKE PROFIT 2: ${rec.get('take_profit_2', 0):,.2f}
POSITION SIZE: {rec.get('position_size', 0):.1f}%
TIME HORIZON: {rec.get('time_horizon', 'N/A')}

MARKET CONDITIONS:
- 24h Change: {context['market_data'].get('price_change_percentage_24h', 0):.2f}%
- 7d Change: {context['market_data'].get('price_change_percentage_7d', 0):.2f}%
- 30d Change: {context['market_data'].get('price_change_percentage_30d', 0):.2f}%
- News Sentiment: {context['sentiment_score']:.1f}/10

RISK FACTORS: {', '.join(context['risk_factors']) if context['risk_factors'] else 'None identified'}
"""

                                # Add previous Q&A to context
                                if current_history:
                                    conversation_context += "\n\nPREVIOUS QUESTIONS AND ANSWERS:\n"
                                    for qa in current_history[-3:]:  # Last 3 Q&As
                                        conversation_context += f"\nQ: {qa['question']}\nA: {qa['answer']}\n"

                                conversation_context += f"\n\nNEW QUESTION: {user_question}\n\nProvide a clear, concise answer. If the question is about risk management, be conservative. If it's about entry timing, consider both immediate and patient approaches."

                                # Get answer from LLM
                                response = advisor.client.chat.completions.create(
                                    model=context['model'],
                                    messages=[
                                        {
                                            "role": "system",
                                            "content": "You are a helpful cryptocurrency trading advisor. Answer questions about your previous recommendation clearly and concisely. Be honest about uncertainties and always emphasize risk management."
                                        },
                                        {
                                            "role": "user",
                                            "content": conversation_context
                                        }
                                    ],
                                    temperature=0.5,
                                    max_tokens=500
                                )

                                answer = response.choices[0].message.content.strip()

                                # Store in conversation history with correct key
                                if analysis_key not in st.session_state.conversation_history:
                                    st.session_state.conversation_history[analysis_key] = []

                                st.session_state.conversation_history[analysis_key].append({
                                    'question': user_question,
                                    'answer': answer
                                })

                                # Display the new Q&A immediately
                                with st.chat_message("user"):
                                    st.write(user_question)
                                with st.chat_message("assistant"):
                                    st.write(answer)

                            except Exception as e:
                                st.error(f"Error getting answer: {e}")
            else:
                if not os.getenv('OPENAI_API_KEY'):
                    st.warning("Set OPENAI_API_KEY to get AI trading recommendations")
                elif not market_data:
                    st.warning("Click 'Run Complete Analysis' above to get trading recommendations")
                else:
                    st.warning("Complete the analysis above to get trading recommendations")

            # Investment considerations
            st.markdown("---")
            st.info(f"""
            **Key Takeaways for {crypto_symbol}:**

            - Current price is {distance_from_ath:.1f}% from all-time high
            - {pct_change:+.1f}% price change over the last {period.lower()}
            - {len(articles)} recent news articles covering this crypto
            - Market cap: ${market_data['market_cap']/1e9:.2f}B

            *This is for informational purposes only. Always do your own research (DYOR) before investing.*
            """)

# ============================================================
# PAGE 5: DEFI POSITIONS
# ============================================================
elif page == "💎 DeFi Positions":
    st.markdown('<p class="main-header">DeFi Positions</p>', unsafe_allow_html=True)
    st.markdown("**Track staking, liquidity pools, and yield farming**")

    tab1, tab2 = st.tabs(["📊 DeFi Protocols", "💰 My Positions"])

    with tab1:
        if st.button("Fetch DeFi Protocol TVLs"):
            with st.spinner("Fetching DeFi data..."):
                defi = clients['defi']
                protocols_df = defi.get_defi_protocols_tvl()

                if not protocols_df.empty:
                    st.subheader("Top DeFi Protocols by TVL")

                    # Format for display
                    display_df = protocols_df.copy()
                    display_df['tvl'] = display_df['tvl'].apply(lambda x: f"${x/1e9:.2f}B")
                    display_df['change_1d'] = display_df['change_1d'].apply(lambda x: f"{x:+.2f}%")
                    display_df['change_7d'] = display_df['change_7d'].apply(lambda x: f"{x:+.2f}%")

                    st.dataframe(display_df, use_container_width=True)

        st.markdown("---")
        st.subheader("Current Staking Yields")
        yields_df = clients['defi'].get_staking_yields()
        st.dataframe(yields_df, use_container_width=True)

    with tab2:
        st.info("Upload a CSV with your DeFi positions to track yields")

        if st.button("Create DeFi Positions Template"):
            defi = clients['defi']
            defi.create_sample_defi_csv("data/defi_positions_template.csv")
            st.success("Template created at data/defi_positions_template.csv")

        uploaded_file = st.file_uploader("Upload DeFi positions CSV", type=['csv'])

        if uploaded_file:
            defi = clients['defi']
            temp_path = f"data/temp_{uploaded_file.name}"
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())

            positions_df = defi.parse_defi_positions_csv(temp_path)

            if not positions_df.empty:
                st.subheader("Your DeFi Positions")

                # Summary
                total_principal = positions_df['amount'].sum()
                total_yield = positions_df['accrued_yield'].sum()
                total_value = positions_df['current_value'].sum()

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Principal", f"${total_principal:,.2f}")
                with col2:
                    st.metric("Accrued Yield", f"${total_yield:,.2f}")
                with col3:
                    st.metric("Current Value", f"${total_value:,.2f}")

                st.dataframe(positions_df, use_container_width=True)

# ============================================================
# PAGE 6: PERFORMANCE TRACKING
# ============================================================
elif page == "📈 Performance Tracking":
    st.markdown('<p class="main-header">Performance Tracking</p>', unsafe_allow_html=True)
    st.markdown("**Track and analyze your trading recommendations**")

    # How to Use Section
    with st.expander("📖 How to Use Performance Tracking - READ THIS FIRST!", expanded=False):
        st.markdown("""
        ## 🎯 What is Performance Tracking?

        This feature lets you **save LLM recommendations, track your trades, and measure actual performance**.
        Think of it as your trading journal + performance analyzer combined!

        ---

        ## 🚀 Quick Start Guide

        ### **Step 1: Save a Recommendation**
        1. Go to **"🔍 Analyze Individual Crypto"** page
        2. Enter a crypto (e.g., "bitcoin" or "BTC")
        3. Click **"Run Complete Analysis"**
        4. After the AI generates a recommendation, click **"💾 Save Recommendation"** button
        5. You'll see: "✅ Recommendation saved! ID: BTC_20250117_143022"

        ### **Step 2: Enter Your Trade** (when you actually buy/sell)
        1. Come to **"📈 Performance Tracking"** page
        2. Go to **"📋 All Recommendations"** tab
        3. Select your saved recommendation from the dropdown
        4. Click **"✅ Enter Trade"** button
        5. Enter the **actual price** you bought/sold at (may differ from recommended price)
        6. Click **"Confirm Entry"**
        7. Status changes from PENDING → ENTERED

        ### **Step 3: Close Your Trade** (when you exit)
        1. When you exit the position (hit TP, stop loss, or manual exit)
        2. Go to **"📋 All Recommendations"** tab
        3. Select the recommendation
        4. Click **"🚪 Close Trade"** button
        5. Enter **exit price** and select **exit reason**:
           - **TP1** = Hit Take Profit 1
           - **TP2** = Hit Take Profit 2
           - **STOP_LOSS** = Hit stop loss
           - **MANUAL** = You closed manually
        6. Click **"Confirm Close"**
        7. **Profit/Loss automatically calculated!** 🎉

        ### **Step 4: View Your Performance**
        1. Go to **"📊 Dashboard"** tab
        2. See your statistics:
           - **Win Rate** - % of profitable trades
           - **Total Return** - Overall profit/loss
           - **Profit Factor** - How much you make per dollar lost
           - **Sharpe Ratio** - Risk-adjusted returns
           - **Equity Curve** - Visual portfolio growth
        3. Set your "Initial Capital" to see realistic portfolio growth

        ---

        ## 💡 Example Workflow

        **Scenario: Bitcoin Analysis**

        1. **Analyze BTC** → AI recommends: "BUY at $95,000, Stop Loss: $92,000, TP1: $99,000"
        2. **Save recommendation** → Saved as `BTC_20250117_120000`
        3. **You buy BTC** at $95,200 (slightly higher than recommended)
           - Mark as "✅ Entered" with actual price: $95,200
        4. **BTC rises** to $99,100
           - Mark as "🚪 Closed" with exit: $99,100, reason: TP1
        5. **System calculates**: Entry $95,200 → Exit $99,100 = **+4.1% profit** ✅
        6. **View dashboard**: Win rate: 100%, Total return: +4.1%, Equity curve goes up!

        ---

        ## 📊 Understanding Your Metrics

        ### **Basic Metrics:**
        - **Win Rate**: % of trades that were profitable
          - 🟢 Excellent: >60% | 🟡 Good: 50-60% | 🔴 Needs work: <50%
        - **Total Return**: Sum of all closed trade returns
        - **Average Return**: Average profit/loss per trade

        ### **Advanced Metrics:**
        - **Profit Factor**: Gross profit ÷ Gross loss
          - 🟢 Excellent: >2.0 (you make $2+ for every $1 lost)
          - 🟡 Profitable: 1.0-2.0
          - 🔴 Losing: <1.0
        - **Sharpe Ratio**: Measures returns vs risk (volatility)
          - 🟢 Good: >1.0 | 🟡 Positive: 0-1.0 | 🔴 Negative: <0
        - **Max Drawdown**: Worst losing streak from peak to trough
          - 🟢 Low risk: <10% | 🟡 Moderate: 10-20% | 🔴 High: >20%
        - **Expectancy**: Expected profit/loss per trade
          - Positive = Good system | Negative = Losing system

        ### **Equity Curve:**
        - Shows your portfolio value over time
        - Upward = Profitable | Downward = Losing
        - Smooth = Consistent | Choppy = Inconsistent

        ---

        ## ✅ Best Practices

        1. **Always save recommendations** - Even if you don't trade them, it's good to track
        2. **Enter actual prices** - Use the real price you bought/sold at, not the recommended price
        3. **Be honest with exits** - Mark if you hit stop loss vs take profit
        4. **Review your stats regularly** - Learn what works and what doesn't
        5. **Track at least 20 trades** - Need enough data for meaningful statistics
        6. **Compare vs buy-and-hold** - Are you beating just holding Bitcoin?

        ---

        ## 🎯 Tips for Success

        - **Paper trade first** - Save recommendations, track "paper trades" before using real money
        - **Focus on win rate AND profit factor** - You can have 40% win rate but still be profitable if your wins are bigger than losses
        - **Watch max drawdown** - If it's too high, reduce position sizes
        - **Use the reasoning** - Review why the AI made the call, learn from wins AND losses
        - **Set realistic goals**:
          - Win rate: 55-60% is excellent
          - Profit factor: >2.0 is great
          - Sharpe ratio: >1.0 is good

        ---

        ## ⚠️ Important Notes

        - **This tracks recommendations, not automatic trading** - You still execute trades manually
        - **Data stored locally** in `data/recommendations.json` - Don't delete this file!
        - **P&L is calculated in %** - Based on entry/exit prices
        - **No account for fees** - Remember to factor in exchange fees when analyzing performance
        - **Historical data** - Can't backtest past recommendations (yet), only track new ones

        ---

        ## 🆘 Troubleshooting

        **Q: I don't see my saved recommendation**
        - A: Make sure you clicked "💾 Save Recommendation" after the AI analysis
        - Check the "📋 All Recommendations" tab

        **Q: Can't enter a trade**
        - A: Recommendation must be in PENDING status
        - If already entered, you'll see it in "💰 Active Trades" tab

        **Q: Metrics show 0%**
        - A: You need to close at least one trade first
        - Metrics only calculate from closed trades

        **Q: Want to delete a bad recommendation?**
        - A: Go to "📋 All Recommendations", select it, click "🗑️ Delete", confirm

        ---

        Ready to start tracking? Close this and use the tabs below! 🚀
        """)

    from src.backtesting.recommendation_tracker import RecommendationTracker
    from src.backtesting.performance_calculator import PerformanceCalculator

    tracker = RecommendationTracker()

    # Quick stats banner
    stats = tracker.get_statistics()
    if stats['total_recommendations'] == 0:
        st.info("👋 **Welcome to Performance Tracking!** You haven't saved any recommendations yet. Go to 'Analyze Individual Crypto', run an analysis, and click the '💾 Save Recommendation' button to get started!")

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📋 All Recommendations", "💰 Active Trades", "✅ Closed Trades"])

    with tab1:
        # Performance Dashboard
        st.subheader("📊 Performance Dashboard")

        # Get statistics
        stats = tracker.get_statistics()
        closed_trades_df = tracker.get_closed_trades()

        # Performance metrics row
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total Recommendations", stats['total_recommendations'])
            st.caption(f"📝 {stats['pending']} pending")

        with col2:
            st.metric("Active Trades", stats['active'])

        with col3:
            st.metric("Closed Trades", stats['closed'])

        with col4:
            win_rate = stats['win_rate']
            st.metric("Win Rate", f"{win_rate:.1f}%")
            if win_rate >= 60:
                st.caption("🟢 Excellent")
            elif win_rate >= 50:
                st.caption("🟡 Good")
            else:
                st.caption("🔴 Needs improvement")

        with col5:
            total_return = stats['total_return']
            st.metric("Total Return", f"{total_return:.2f}%")
            if total_return > 0:
                st.caption("🟢 Profitable")
            else:
                st.caption("🔴 In loss")

        if not closed_trades_df.empty:
            st.markdown("---")

            # Calculate advanced metrics
            initial_capital = st.number_input("Initial Capital ($)", value=10000, step=1000, key="perf_initial_capital")
            perf_metrics = PerformanceCalculator.calculate_comprehensive_metrics(closed_trades_df, initial_capital)

            # Advanced metrics
            st.subheader("📈 Advanced Metrics")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Profit Factor", f"{perf_metrics['profit_factor']:.2f}")
                st.caption("Gross Profit / Gross Loss")
                if perf_metrics['profit_factor'] > 2:
                    st.caption("🟢 Excellent (>2.0)")
                elif perf_metrics['profit_factor'] > 1:
                    st.caption("🟡 Profitable (>1.0)")
                else:
                    st.caption("🔴 Losing (<1.0)")

            with col2:
                st.metric("Sharpe Ratio", f"{perf_metrics['sharpe_ratio']:.2f}")
                st.caption("Risk-adjusted returns")
                if perf_metrics['sharpe_ratio'] > 1:
                    st.caption("🟢 Good (>1.0)")
                elif perf_metrics['sharpe_ratio'] > 0:
                    st.caption("🟡 Positive")
                else:
                    st.caption("🔴 Negative")

            with col3:
                st.metric("Max Drawdown", f"{perf_metrics['max_drawdown_pct']:.2f}%")
                st.caption("Largest peak-to-trough decline")
                if abs(perf_metrics['max_drawdown_pct']) < 10:
                    st.caption("🟢 Low risk")
                elif abs(perf_metrics['max_drawdown_pct']) < 20:
                    st.caption("🟡 Moderate risk")
                else:
                    st.caption("🔴 High risk")

            with col4:
                st.metric("Expectancy", f"{perf_metrics['expectancy']:.2f}%")
                st.caption("Expected return per trade")
                if perf_metrics['expectancy'] > 1:
                    st.caption("🟢 Strong edge")
                elif perf_metrics['expectancy'] > 0:
                    st.caption("🟡 Positive edge")
                else:
                    st.caption("🔴 No edge")

            # Win/Loss metrics
            st.markdown("---")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Average Win", f"{perf_metrics['avg_win']:.2f}%")

            with col2:
                st.metric("Average Loss", f"{perf_metrics['avg_loss']:.2f}%")

            with col3:
                st.metric("Win/Loss Ratio", f"{perf_metrics['win_loss_ratio']:.2f}")
                st.caption("Avg Win / Avg Loss")

            # Equity Curve
            st.markdown("---")
            st.subheader("💹 Equity Curve")

            equity_df = PerformanceCalculator.build_equity_curve(closed_trades_df, initial_capital)

            if not equity_df.empty:
                fig_equity = go.Figure()

                fig_equity.add_trace(go.Scatter(
                    x=equity_df['timestamp'],
                    y=equity_df['equity'],
                    mode='lines',
                    name='Portfolio Value',
                    line=dict(color='#00c853', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(0, 200, 83, 0.1)'
                ))

                # Add initial capital line
                fig_equity.add_hline(
                    y=initial_capital,
                    line_dash="dash",
                    line_color="gray",
                    annotation_text=f"Initial Capital: ${initial_capital:,.0f}"
                )

                fig_equity.update_layout(
                    title=f'Portfolio Growth (${initial_capital:,.0f} → ${perf_metrics["final_capital"]:,.0f})',
                    xaxis_title='Date',
                    yaxis_title='Portfolio Value ($)',
                    template='plotly_white',
                    height=400
                )

                st.plotly_chart(fig_equity, use_container_width=True)

                # Performance summary
                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Final Capital",
                        f"${perf_metrics['final_capital']:,.2f}",
                        delta=f"${perf_metrics['total_profit']:,.2f}"
                    )

                with col2:
                    st.metric(
                        "Total Return",
                        f"{perf_metrics['total_return_pct']:.2f}%",
                        delta=f"{perf_metrics['total_return_pct']:.2f}%"
                    )

            # Trade distribution
            st.markdown("---")
            st.subheader("📊 Trade Distribution")

            col1, col2 = st.columns(2)

            with col1:
                # Win/Loss pie chart
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['Wins', 'Losses', 'Breakeven'],
                    values=[
                        len(closed_trades_df[closed_trades_df['outcome'] == 'WIN']),
                        len(closed_trades_df[closed_trades_df['outcome'] == 'LOSS']),
                        len(closed_trades_df[closed_trades_df['outcome'] == 'BREAKEVEN'])
                    ],
                    marker=dict(colors=['#00c853', '#d32f2f', '#ffa726']),
                    hole=0.4
                )])
                fig_pie.update_layout(title='Win/Loss Distribution', height=300)
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                # Return distribution histogram
                fig_hist = go.Figure(data=[go.Histogram(
                    x=closed_trades_df['profit_loss_pct'],
                    nbinsx=20,
                    marker=dict(
                        color=closed_trades_df['profit_loss_pct'],
                        colorscale='RdYlGn',
                        showscale=True
                    )
                )])
                fig_hist.update_layout(
                    title='Return Distribution',
                    xaxis_title='Return (%)',
                    yaxis_title='Number of Trades',
                    height=300
                )
                st.plotly_chart(fig_hist, use_container_width=True)

        else:
            st.info("💡 No closed trades yet. Save some recommendations and track their performance!")

    with tab2:
        # All Recommendations
        st.subheader("📋 All Recommendations")

        all_recs = tracker.get_all_recommendations()

        if not all_recs.empty:
            # Display as table
            display_df = all_recs[[
                'timestamp', 'crypto_symbol', 'recommendation', 'entry_price',
                'current_price_at_recommendation', 'confidence', 'status'
            ]].copy()

            display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')

            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # View/Edit recommendation
            st.markdown("---")
            st.subheader("🔍 View Recommendation Details")

            rec_ids = all_recs['id'].tolist()
            selected_rec_id = st.selectbox("Select Recommendation", rec_ids, key="view_rec_select")

            if selected_rec_id:
                rec = tracker.get_recommendation_by_id(selected_rec_id)

                if rec:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Crypto:** {rec['crypto_symbol']}")
                        st.write(f"**Recommendation:** {rec['recommendation']}")
                        st.write(f"**Status:** {rec['status']}")
                        st.write(f"**Confidence:** {rec['confidence']}%")
                        st.write(f"**Entry Price:** ${rec['entry_price']:,.2f}")
                        st.write(f"**Stop Loss:** ${rec['stop_loss_price']:,.2f}")
                        st.write(f"**Take Profit 1:** ${rec['take_profit_1']:,.2f}")

                    with col2:
                        st.write(f"**Timestamp:** {rec['timestamp']}")
                        st.write(f"**Model:** {rec['model_used']}")
                        st.write(f"**Position Size:** {rec['position_size_pct']}%")
                        if rec['entered']:
                            st.write(f"**Entry Date:** {rec['entry_date']}")
                            st.write(f"**Actual Entry:** ${rec['actual_entry_price']:,.2f}")
                        if rec['status'] == 'CLOSED':
                            st.write(f"**Exit Price:** ${rec['exit_price']:,.2f}")
                            st.write(f"**P&L:** {rec['profit_loss_pct']:.2f}%")
                            st.write(f"**Outcome:** {rec['outcome']}")

                    st.markdown("**Reasoning:**")
                    st.write(rec['reasoning'])

                    # Action buttons based on status
                    st.markdown("---")

                    # PENDING status - Show Enter Trade form
                    if rec['status'] == 'PENDING':
                        st.subheader("✅ Enter This Trade")
                        with st.form(key=f"enter_form_{selected_rec_id}"):
                            actual_entry = st.number_input(
                                "Actual Entry Price ($)",
                                value=float(rec['entry_price']),
                                step=0.01,
                                help="Enter the actual price you bought/sold at"
                            )
                            notes = st.text_input("Notes (optional)", placeholder="e.g., Entered on Binance")

                            col1, col2 = st.columns([1, 1])
                            with col1:
                                submitted = st.form_submit_button("✅ Confirm Entry", type="primary")
                                if submitted:
                                    tracker.enter_trade(selected_rec_id, actual_entry, notes)
                                    st.success("✅ Trade entered successfully!")
                                    st.rerun()

                            with col2:
                                if st.form_submit_button("❌ Cancel Recommendation"):
                                    tracker.cancel_recommendation(selected_rec_id, "Cancelled by user")
                                    st.success("Recommendation cancelled")
                                    st.rerun()

                    # ENTERED status - Show Close Trade form
                    elif rec['status'] == 'ENTERED':
                        st.subheader("🚪 Close This Trade")
                        with st.form(key=f"close_form_{selected_rec_id}"):
                            exit_price = st.number_input(
                                "Exit Price ($)",
                                value=float(rec['actual_entry_price']),
                                step=0.01,
                                help="Enter the price you sold/closed at"
                            )
                            exit_reason = st.selectbox(
                                "Exit Reason",
                                ["TP1", "TP2", "STOP_LOSS", "MANUAL"],
                                help="Why did you exit? TP1=Take Profit 1, TP2=Take Profit 2, STOP_LOSS=Hit stop loss, MANUAL=Manual exit"
                            )
                            notes = st.text_input("Notes (optional)", placeholder="e.g., Exited due to news")

                            submitted = st.form_submit_button("🚪 Confirm Close", type="primary")
                            if submitted:
                                tracker.close_trade(selected_rec_id, exit_price, exit_reason, notes)
                                st.success("✅ Trade closed successfully!")
                                st.rerun()

                    # CLOSED or CANCELLED status - Show Delete option
                    else:
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            if st.button("🗑️ Delete This Recommendation", key="delete_rec_btn"):
                                tracker.delete_recommendation(selected_rec_id)
                                st.success("Recommendation deleted!")
                                st.rerun()
                        with col2:
                            st.caption(f"Status: {rec['status']}")

        else:
            st.info("💡 No recommendations saved yet. Analyze a crypto and save the recommendation!")

    with tab3:
        # Active Trades
        st.subheader("💰 Active Trades")

        active_trades = tracker.get_active_trades()

        if not active_trades.empty:
            for _, trade in active_trades.iterrows():
                with st.expander(f"{trade['crypto_symbol']} - Entered at ${trade['actual_entry_price']:,.2f}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Entry Date:** {trade['entry_date']}")
                        st.write(f"**Entry Price:** ${trade['actual_entry_price']:,.2f}")
                        st.write(f"**Stop Loss:** ${trade['stop_loss_price']:,.2f}")
                        st.write(f"**Take Profit 1:** ${trade['take_profit_1']:,.2f}")

                    with col2:
                        st.write(f"**Recommendation:** {trade['recommendation']}")
                        st.write(f"**Position Size:** {trade['position_size_pct']}%")
                        st.write(f"**Confidence:** {trade['confidence']}%")

                    if st.button(f"Close {trade['crypto_symbol']}", key=f"close_{trade['id']}"):
                        st.info("Use the 'All Recommendations' tab to close this trade")
        else:
            st.info("💡 No active trades. Enter some recommendations to start tracking!")

    with tab4:
        # Closed Trades
        st.subheader("✅ Closed Trades")

        closed_trades = tracker.get_closed_trades()

        if not closed_trades.empty:
            # Sort by exit date
            closed_trades = closed_trades.sort_values('exit_date', ascending=False)

            for _, trade in closed_trades.iterrows():
                outcome_color = "🟢" if trade['outcome'] == 'WIN' else "🔴" if trade['outcome'] == 'LOSS' else "⚪"
                pnl = trade['profit_loss_pct']

                with st.expander(f"{outcome_color} {trade['crypto_symbol']} - {pnl:+.2f}% | {trade['exit_reason']}"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write("**Entry:**")
                        st.write(f"Date: {trade['entry_date']}")
                        st.write(f"Price: ${trade['actual_entry_price']:,.2f}")

                    with col2:
                        st.write("**Exit:**")
                        st.write(f"Date: {trade['exit_date']}")
                        st.write(f"Price: ${trade['exit_price']:,.2f}")
                        st.write(f"Reason: {trade['exit_reason']}")

                    with col3:
                        st.write("**Performance:**")
                        st.write(f"P&L: {pnl:+.2f}%")
                        st.write(f"Outcome: {trade['outcome']}")
                        st.write(f"Confidence: {trade['confidence']}%")

                    if trade['notes']:
                        st.caption(f"Notes: {trade['notes']}")
        else:
            st.info("💡 No closed trades yet. Close some active trades to see performance!")

# ============================================================
# PAGE 7: ALERTS
# ============================================================
elif page == "🚨 Alerts":
    st.markdown('<p class="main-header">Portfolio Alerts</p>', unsafe_allow_html=True)

    if st.button("Generate Alerts", type="primary"):
        with st.spinner("Checking for alerts..."):
            alert_system = clients['alerts']
            all_alerts = []

            try:
                # Portfolio alerts
                tracker = CryptoPortfolioTracker()
                portfolio_df = tracker.update_portfolio()
                summary = tracker.get_portfolio_summary()

                if not portfolio_df.empty:
                    thresholds = alert_system.get_default_thresholds()

                    # Price alerts
                    price_alerts = alert_system.check_price_alerts(portfolio_df, thresholds)
                    all_alerts.extend(price_alerts)

                    # Portfolio alerts
                    portfolio_alerts = alert_system.check_portfolio_alerts(summary, thresholds)
                    all_alerts.extend(portfolio_alerts)

                if all_alerts:
                    st.warning(f"Found {len(all_alerts)} alert(s)")

                    # Display alerts by severity
                    for severity in ['HIGH', 'MEDIUM', 'LOW']:
                        severity_alerts = [a for a in all_alerts if a['severity'] == severity]
                        if severity_alerts:
                            if severity == 'HIGH':
                                st.error(f"**{severity} PRIORITY**")
                            elif severity == 'MEDIUM':
                                st.warning(f"**{severity} PRIORITY**")
                            else:
                                st.info(f"**{severity} PRIORITY**")

                            for alert in severity_alerts:
                                st.write(f"- {alert['message']}")
                            st.markdown("---")
                else:
                    st.success("No alerts at this time!")

            except Exception as e:
                st.error(f"Error generating alerts: {e}")

# ============================================================
# PAGE 7: SETTINGS
# ============================================================
elif page == "⚙️ Settings":
    st.markdown('<p class="main-header">Settings</p>', unsafe_allow_html=True)

    st.subheader("API Configuration")

    # OpenAI API Key
    openai_key = os.getenv('OPENAI_API_KEY', '')
    st.text_input("OpenAI API Key", value="*" * 20 if openai_key else "",
                 disabled=True, help="Set via OPENAI_API_KEY environment variable")

    if openai_key:
        st.success("✅ OpenAI API key configured")
    else:
        st.warning("⚠️ OpenAI API key not set - sentiment analysis will be disabled")

    st.markdown("---")

    # CoinGecko API Key
    coingecko_key = os.getenv('COINGECKO_API_KEY', '')
    st.text_input("CoinGecko API Key", value="*" * 20 if coingecko_key else "",
                 disabled=True, help="Set via COINGECKO_API_KEY environment variable")

    if coingecko_key:
        st.success("✅ CoinGecko API key configured")
    else:
        st.error("❌ CoinGecko API key not set - Price data will NOT work!")
        st.info("Get a FREE API key from: https://www.coingecko.com/en/api")
        st.code("# Add to your .env file:\nCOINGECKO_API_KEY=CG-your-key-here", language="bash")

    st.markdown("---")
    st.subheader("Alert Thresholds")

    alert_system = clients['alerts']
    default_thresholds = alert_system.get_default_thresholds()

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Bitcoin (BTC)**")
        btc_drop = st.slider("Price drop alert (%)", 5, 20, default_thresholds['BTC']['drop_pct'])
        btc_spike = st.slider("Price spike alert (%)", 5, 30, default_thresholds['BTC']['spike_pct'])

    with col2:
        st.write("**Ethereum (ETH)**")
        eth_drop = st.slider("Price drop alert (%)", 5, 25, default_thresholds['ETH']['drop_pct'])
        eth_spike = st.slider("Price spike alert (%)", 5, 35, default_thresholds['ETH']['spike_pct'])

    st.markdown("---")
    st.subheader("About")
    st.info("""
    **Crypto Portfolio Monitor**

    Track Bitcoin and Ethereum holdings with:
    - Real-time price data from CoinGecko
    - AI-powered news sentiment analysis
    - DeFi position tracking
    - Automated alerts
    - Fear & Greed Index

    Built with Streamlit, OpenAI GPT-4, and CoinGecko API
    """)
