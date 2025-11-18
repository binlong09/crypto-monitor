# Quick Start Guide

Get up and running with Crypto Portfolio Monitor in 5 minutes!

---

## Step 1: Install Dependencies (1 min)

```bash
cd crypto_monitor
pip install -r requirements.txt
```

Or using a virtual environment:

```bash
cd crypto_monitor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 2: Set API Key (1 min)

Create a `.env` file in the crypto_monitor directory:

```bash
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

**Important:** Replace `sk-your-key-here` with your actual API key.

Get your OpenAI API key from: https://platform.openai.com/api-keys

The app will automatically load the API key from the `.env` file.

---

## Step 3: Create Your Holdings File (2 min)

Create `data/my_holdings.csv`:

```csv
symbol,amount,cost_basis,purchase_date
BTC,0.1,45000,2024-01-15
ETH,2.5,2500,2024-02-01
```

Or use the app to generate a template:
1. Run the dashboard
2. Click "Create Sample CSV"
3. Edit `data/sample_holdings.csv`

---

## Step 4: Run the Dashboard (1 min)

```bash
streamlit run dashboard.py
```

The dashboard will open at `http://localhost:8501`

---

## First Time Using the Dashboard

### Upload Your Holdings
1. Go to "Portfolio Overview"
2. Upload your `my_holdings.csv`
3. Click "Update Portfolio"

### Check Market Data
1. Go to "Market Data"
2. Select BTC or ETH
3. Click "Fetch Market Data"
4. View price, charts, and Fear & Greed Index

### Analyze News Sentiment
1. Go to "News & Sentiment"
2. Select BTC or ETH
3. Click "Fetch & Analyze News"
4. View AI-powered sentiment analysis

### Set Up Alerts
1. Go to "Settings"
2. Customize alert thresholds
3. Go to "Alerts" page
4. Click "Generate Alerts"

---

## Optional: DeFi Position Tracking

Create `data/my_defi_positions.csv`:

```csv
protocol,asset,amount,apr,start_date
Ethereum 2.0,ETH,5.0,3.5,2024-01-15
Lido,stETH,2.0,3.3,2024-02-01
```

Then:
1. Go to "DeFi Positions"
2. Upload your positions CSV
3. View yield calculations

---

## Tips for Best Experience

1. **Update Regularly**: Click "Update Portfolio" daily to track performance
2. **Check News**: Run sentiment analysis when market moves significantly
3. **Monitor Alerts**: Check alerts page for important notifications
4. **Fear & Greed**: Use as a contrarian indicator
5. **Cost Basis**: Enter accurate purchase prices for P&L tracking

---

## Troubleshooting

### "OpenAI API key not found"
- Make sure you've set OPENAI_API_KEY environment variable
- Or create a `.env` file with your key

### "No holdings data available"
- Create and upload a holdings CSV file
- Make sure it has the correct format

### "Error fetching data from CoinGecko"
- Check your internet connection
- CoinGecko free tier has rate limits - wait a moment and try again

### "Module not found"
- Run `pip install -r requirements.txt` again
- Make sure you're in the crypto_monitor directory

---

## Next Steps

- Explore all dashboard pages
- Customize alert thresholds in Settings
- Set up DeFi position tracking
- Check the README.md for detailed documentation

---

**Happy tracking!** 🚀
