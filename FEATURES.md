# Crypto Monitor Dashboard Features

## Dashboard Pages

### 1. 🏠 Portfolio Overview
- Upload holdings CSV (symbol, amount, cost_basis, purchase_date)
- Real-time portfolio value from CoinGecko
- 24h change tracking
- P&L calculation with cost basis
- Portfolio allocation pie chart
- Holdings table with weights

### 2. 📊 Market Data
- Select BTC or ETH
- Current price with 24h change
- Market cap and volume
- 24h high/low
- 7d and 30d price changes
- ATH/ATL prices
- Circulating/max supply metrics
- Historical price charts (7, 30, 90, 365 days)
- Crypto Fear & Greed Index

### 3. 📰 News & Sentiment
- Fetch news from 4 sources (CoinTelegraph, CoinDesk, Decrypt, TheBlock)
- AI-powered sentiment analysis (GPT-4o-mini)
- Overall sentiment scoring
- Bullish/Bearish/Neutral classification
- Critical event detection:
  - Hack/security alerts
  - Regulation news
  - Adoption announcements
  - Technical updates
- Sentiment distribution chart
- Article-by-article analysis with explanations

### 4. 🔍 Analyze Individual Crypto (NEW!)
**Comprehensive deep-dive analysis for BTC or ETH with:**

#### Market Overview
- Current price, 24h high/low
- 24h, 7d, 30d price changes
- Market cap and volume
- Supply metrics (circulating, total, max)

#### All-Time Stats
- All-time high (ATH) with date
- All-time low (ATL) with date
- Distance from ATH/ATL percentages
- Visual indicators for market position

#### Price History
- Interactive price charts
- Period selection: 7, 30, 90, 365 days
- Period high/low/average
- Volatility (standard deviation)
- Percentage change over period

#### Recent News & Sentiment
- 48 hours of news articles
- AI sentiment analysis (if API key set)
- Top 5 articles with scores
- Sentiment breakdown (bullish/bearish/neutral)
- Critical event flags
- Source and publication timestamps

#### On-Chain & Social Metrics
- Twitter followers
- Reddit subscribers and active users
- GitHub stars, forks, subscribers
- Recent commit activity
- Pull requests merged
- Development activity indicators

#### Risk Assessment
- Automated risk factor detection:
  - High volatility warnings
  - Significant price declines
  - Negative sentiment alerts
  - Critical news events
- Visual risk indicators
- Investment considerations summary

#### Key Takeaways
- Distance from ATH
- Period performance summary
- News coverage statistics
- Market cap summary
- DYOR disclaimer

### 5. 💎 DeFi Positions
- Top DeFi protocols by TVL (from DeFiLlama)
- Current staking yields
- Upload DeFi positions CSV
- Automatic yield calculations
- Track multiple protocols:
  - ETH 2.0 staking
  - Lido (liquid staking)
  - Aave (lending)
  - Uniswap (liquidity pools)
  - Curve (stablecoins)

### 6. 🚨 Alerts
- Price drop/spike alerts per crypto
- Portfolio-wide movement alerts
- Critical news detection
- Sentiment-based warnings
- Severity levels (HIGH/MEDIUM/LOW)
- Customizable thresholds in Settings

### 7. ⚙️ Settings
- API configuration status
- Alert threshold customization:
  - BTC drop/spike percentages
  - ETH drop/spike percentages
  - Portfolio-wide thresholds
- About information

---

## Data Sources

- **CoinGecko API** - Free tier, ~50 calls/min
- **Alternative.me** - Fear & Greed Index
- **DeFiLlama API** - DeFi protocol data
- **RSS Feeds** - Crypto news (4 sources)
- **OpenAI GPT-4o-mini** - Sentiment analysis

---

## CSV Formats

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
```

---

## Requirements

- Python 3.8+
- OpenAI API key (for sentiment analysis)
- Internet connection (for API calls)

---

## Quick Start

```bash
cd crypto_monitor
pip install -r requirements.txt
export OPENAI_API_KEY='your-key'
streamlit run dashboard.py
```

Open `http://localhost:8501` in your browser.

---

## Key Features of "Analyze Individual Crypto"

The new analysis page provides a one-stop comprehensive view:

1. **All metrics in one place** - No need to switch between pages
2. **Historical context** - See how current prices relate to ATH/ATL
3. **Sentiment integration** - Combines price action with news sentiment
4. **Risk assessment** - Automated detection of concerning patterns
5. **Social signals** - GitHub and social media activity
6. **Investment summary** - Quick key takeaways for decision making

Perfect for:
- Quick daily check-ins on BTC or ETH
- Pre-investment research
- Risk monitoring
- Understanding market context
- Combining technical and sentiment analysis

---

## What Makes This Different from Stock App

Crypto-specific features:
- Fear & Greed Index (crypto sentiment indicator)
- On-chain metrics (GitHub activity, development stats)
- DeFi protocol tracking
- Crypto news sources
- Supply metrics (max supply, inflation rate)
- 24/7 market tracking
- Higher volatility thresholds
- Social metrics (Twitter, Reddit)
