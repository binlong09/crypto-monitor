# 🚀 Crypto Trading Analyzer with AI

**Professional-grade cryptocurrency analysis powered by GPT-4**

Comprehensive technical analysis, market context, sentiment analysis, pattern recognition, and AI-powered trading recommendations with performance tracking.

---

## ✨ Features

### 📊 Technical Analysis (35+ Data Points)
- **22+ Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages, Stochastic, ADX, ATR, OBV
- **Volume Analysis**: Trends, spikes, divergence detection, confirmation scores
- **Pattern Recognition**: Price patterns & chart patterns (Head & Shoulders, Triangles, etc.)
- **Support & Resistance**: Automatic detection of key price levels
- **Interactive Charts**: Plotly visualizations with full indicator overlays

### 🌍 Market Context Analysis
- **Multi-Timeframe**: Analyze across 7-day, 30-day, 90-day simultaneously
- **Timeframe Alignment**: Identify high-conviction trades when all timeframes agree
- **BTC Correlation**: Understand how crypto moves relative to Bitcoin
- **Fear & Greed Index**: Market sentiment with position sizing recommendations
- **Market Regime Detection**: Extreme Fear/Fear/Neutral/Greed/Extreme Greed zones

### 📰 News & Sentiment
- **Real-time News**: Aggregates from CoinTelegraph, CoinDesk, Decrypt, TheBlock
- **AI Sentiment Analysis**: GPT-4 analyzes news impact (-10 to +10 scale)
- **Critical Event Detection**: Flags hacks, regulations, major announcements
- **News Summarization**: AI-generated summaries of developments

### 🤖 AI Trading Recommendations
- **GPT-4 Analysis**: Comprehensive buy/sell/hold recommendations
- **Entry/Exit Prices**: Specific entry points, stop losses, take profit targets
- **Risk/Reward Analysis**: Calculate potential risk vs reward
- **Position Sizing**: Recommended allocation based on confidence & market conditions
- **Detailed Reasoning**: Understand exactly why AI made its recommendation
- **Model Selection**: Choose from GPT-4o, GPT-4o-mini, O1-mini

### 📈 Performance Tracking
- **Save Recommendations**: Track AI suggestions over time
- **Manual Trade Tracking**: Enter and close trades, auto-calculate P&L
- **Advanced Metrics**: Win Rate, Profit Factor, Sharpe Ratio, Max Drawdown, Expectancy
- **Equity Curve**: Visual portfolio growth over time
- **Trade Journal**: Detailed history with outcomes
- **Performance Dashboard**: Win/loss distribution, return histograms

---

## 🚀 Quick Start

### Local Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/crypto_monitor.git
cd crypto_monitor
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

4. **Run the app**
```bash
streamlit run dashboard.py
```

5. **Open in browser** → `http://localhost:8501`

---

## ☁️ Deploy to Streamlit Cloud (FREE!)

### Step 1: Push to GitHub

1. **Initialize Git** (if not already done)
```bash
git init
git add .
git commit -m "Initial commit"
```

2. **Create GitHub repository**
- Go to https://github.com/new
- Create repository (e.g., `crypto-analyzer`)
- Don't initialize with README

3. **Push to GitHub**
```bash
git remote add origin https://github.com/YOUR_USERNAME/crypto-analyzer.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. **Visit** → https://share.streamlit.io
2. **Sign in** with GitHub
3. **Click "New app"**
4. **Select:**
   - Repository: `YOUR_USERNAME/crypto-analyzer`
   - Branch: `main`
   - Main file: `dashboard.py`
5. **Add Secrets** (IMPORTANT!)
   - Click "Advanced settings" → "Secrets"
   - Add:
   ```toml
   OPENAI_API_KEY = "your_openai_api_key_here"
   ```
6. **Click "Deploy!"**
7. **Wait 2-3 minutes** → App will be live!

Your app URL: `https://your-app-name.streamlit.app`

**Note:** On Streamlit Cloud free tier, data (portfolio, recommendations) won't persist across restarts. For production use, connect to external database.

---

## Usage

### Setting Up Your Portfolio

1. Click "Create Sample CSV" in the Portfolio Overview page
2. Edit `data/sample_holdings.csv` with your holdings:
   ```csv
   symbol,amount,cost_basis,purchase_date
   BTC,0.5,45000,2024-01-15
   ETH,5.0,2500,2024-02-01
   ```
3. Upload the CSV or click "Update Portfolio"

### Tracking DeFi Positions

1. Go to "DeFi Positions" page
2. Click "Create DeFi Positions Template"
3. Edit `data/defi_positions_template.csv`:
   ```csv
   protocol,asset,amount,apr,start_date
   Ethereum 2.0,ETH,5.0,3.5,2024-01-15
   Lido,stETH,2.0,3.3,2024-02-01
   ```
4. Upload to see yield calculations

---

## Dashboard Pages

### Portfolio Overview
- Real-time portfolio value
- Holdings breakdown with P&L
- Portfolio allocation chart
- 24h performance tracking

### Market Data
- Current prices for BTC and ETH
- Historical price charts
- Market metrics (market cap, volume, ATH/ATL)
- Fear & Greed Index

### News & Sentiment
- Latest crypto news from multiple sources
- AI-powered sentiment analysis (multiple model options)
- Critical event detection (hacks, regulations, adoption)
- Overall sentiment scoring

### AI Trading Advisor (NEW!)
- **Multiple AI models** (GPT-4o Mini, GPT-4o, GPT-4 Turbo, O1 Mini)
- **Buy/Sell/Hold recommendations** with confidence levels
- **Stop-loss suggestions** based on volatility and support
- **Take-profit targets** with scaling strategies
- **Position sizing** recommendations
- **Risk/reward analysis** for each trade
- **Interactive Q&A** - Ask follow-up questions with full context
- Time horizon and invalidation criteria

### DeFi Positions
- Top DeFi protocols by TVL
- Current staking yields
- Your positions with yield calculations
- Track multiple protocols

### Alerts
- Price drop/spike alerts
- Portfolio-wide alerts
- Critical news alerts
- Customizable thresholds

### Settings
- API configuration
- Alert threshold customization
- About information

---

## Technology Stack

- **Frontend:** Streamlit
- **Data Source:** CoinGecko API (free tier)
- **News:** RSS feeds (CoinTelegraph, CoinDesk, Decrypt, TheBlock)
- **DeFi Data:** DeFiLlama API
- **AI:** OpenAI GPT-4o-mini
- **Visualization:** Plotly

---

## Project Structure

```
crypto_monitor/
├── dashboard.py              # Main Streamlit app
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── data/                    # Data storage
│   ├── portfolio_snapshots.json
│   └── current_holdings.csv
├── src/
│   ├── data/
│   │   ├── coingecko_client.py    # CoinGecko API client
│   │   ├── news_fetcher.py        # News aggregator
│   │   └── defi_tracker.py        # DeFi protocol tracker
│   ├── monitoring/
│   │   ├── portfolio_tracker.py   # Portfolio tracking
│   │   └── alert_system.py        # Alert generation
│   └── llm/
│       └── sentiment_analyzer.py  # AI sentiment analysis
```

---

## Data Sources

### Free APIs Used
- **CoinGecko** - Crypto prices and market data (50 calls/min)
- **Alternative.me** - Fear & Greed Index
- **DeFiLlama** - DeFi protocol TVLs
- **RSS Feeds** - Crypto news articles

### Note on Rate Limits
The app uses free APIs with rate limits. The CoinGecko client includes automatic rate limiting to stay within free tier limits.

---

## Configuration

### Alert Thresholds
Default thresholds can be customized in Settings:
- BTC: 10% drop, 15% spike
- ETH: 12% drop, 18% spike
- Portfolio: 8% drop, 12% spike

### OpenAI API Usage
Sentiment analysis uses GPT-4o-mini for cost efficiency:
- ~$0.15 per 1M input tokens
- ~$0.60 per 1M output tokens
- Typical cost: ~$0.01-0.02 per news scan

---

## CSV File Formats

### Holdings CSV
```csv
symbol,amount,cost_basis,purchase_date
BTC,0.5,45000,2024-01-15
ETH,5.0,2500,2024-02-01
```

### DeFi Positions CSV
```csv
protocol,asset,amount,apr,start_date
Ethereum 2.0,ETH,5.0,3.5,2024-01-15
Lido,stETH,2.0,3.3,2024-02-01
Aave,ETH,1.0,1.5,2024-03-01
```

---

## Features in Detail

### Portfolio Tracking
- Automatic price updates from CoinGecko
- Historical snapshots for performance tracking
- Profit/loss calculation with cost basis
- Portfolio weight allocation
- 24h change tracking

### News Sentiment Analysis
- Aggregates from 4+ major crypto news sources
- AI analysis for each article:
  - Sentiment score (-10 to +10)
  - Bullish/bearish classification
  - Critical event detection
- Overall portfolio sentiment scoring
- Flags for hacks, regulations, adoption, tech updates

### DeFi Integration
- Track ETH 2.0 staking
- Liquid staking (Lido, etc.)
- Lending protocols (Aave, Compound)
- Liquidity pools (Uniswap, Curve)
- Automatic yield calculations
- TVL tracking for top protocols

### Smart Alerts
- Price-based alerts per crypto
- Portfolio-wide movement alerts
- Critical news detection
- Sentiment-based warnings
- Customizable thresholds

---

## Deployment

### Local Development
```bash
streamlit run dashboard.py
```

### Streamlit Cloud (Free)
1. Push to GitHub
2. Go to https://share.streamlit.io
3. Deploy from your repository
4. Add OPENAI_API_KEY in Secrets

---

## Limitations

- **Supported Cryptos:** Only BTC and ETH (easily extendable)
- **API Rate Limits:** CoinGecko free tier has limits
- **Historical Data:** Limited to 365 days on free tier
- **DeFi Tracking:** Manual position entry (no wallet integration)
- **Exchange Integration:** Not available (CSV upload only)

---

## Future Enhancements

Potential additions:
- More cryptocurrencies (top 50+)
- Wallet integration (MetaMask, etc.)
- Exchange API connections
- Technical indicators (RSI, MACD)
- Price alerts via email/SMS
- Automated daily reports
- Multi-wallet tracking
- Tax reporting

---

## Disclaimer

**This tool is for educational and informational purposes only.**

- Not financial advice
- Cryptocurrency investments are high risk
- Use at your own risk
- Always do your own research (DYOR)
- Past performance does not guarantee future results

---

## License

MIT License

---

## Acknowledgments

- **CoinGecko** for free crypto data API
- **OpenAI** for GPT-4 API
- **Streamlit** for the amazing framework
- **DeFiLlama** for DeFi protocol data

---

## Support

For issues or questions:
1. Check the Settings page for configuration
2. Ensure OPENAI_API_KEY is set
3. Verify CSV file formats
4. Check API rate limits

---

**Built for the crypto community**

Track smart. Invest smarter.
