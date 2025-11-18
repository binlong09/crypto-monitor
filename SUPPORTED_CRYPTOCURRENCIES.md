# Supported Cryptocurrencies

## ✅ Analyze ANY Cryptocurrency!

You can now analyze **any cryptocurrency** available on CoinGecko (10,000+ coins)!

## How to Use

### Option 1: Use Common Symbols (Easiest)
Just type the ticker symbol you know:
- `BTC` → Bitcoin
- `ETH` → Ethereum
- `ADA` → Cardano
- `SOL` → Solana
- `XRP` → Ripple
- `DOGE` → Dogecoin
- `MATIC` → Polygon
- `LINK` → Chainlink
- `DOT` → Polkadot
- `AVAX` → Avalanche
- `UNI` → Uniswap
- `ATOM` → Cosmos
- `LTC` → Litecoin
- And 20+ more built-in mappings!

### Option 2: Use CoinGecko ID
For cryptocurrencies not in the pre-mapped list, use the CoinGecko ID (usually lowercase name):

Examples:
- `bitcoin` → Bitcoin
- `ethereum` → Ethereum
- `binancecoin` → Binance Coin
- `tether` → Tether (USDT)
- `shiba-inu` → Shiba Inu
- `pepe` → Pepe
- `aptos` → Aptos
- `arbitrum` → Arbitrum

## Finding CoinGecko IDs

### Method 1: CoinGecko Website
1. Go to https://www.coingecko.com/
2. Search for your cryptocurrency
3. Look at the URL - the ID is in the URL
   - Example: `https://www.coingecko.com/en/coins/bitcoin` → ID is `bitcoin`
   - Example: `https://www.coingecko.com/en/coins/shiba-inu` → ID is `shiba-inu`

### Method 2: CoinGecko API List
- Full list available at: https://api.coingecko.com/api/v3/coins/list
- Shows all 10,000+ supported coins with their IDs

### Method 3: Trial and Error
Most coins use their common name in lowercase:
- Bitcoin → `bitcoin` ✅
- Cardano → `cardano` ✅
- Polkadot → `polkadot` ✅
- Avalanche → `avalanche-2` ❌ (has a suffix)
- Polygon → `matic-network` ❌ (uses old name)

## Pre-Mapped Symbols

These symbols are automatically converted to CoinGecko IDs:

| Symbol | Name | CoinGecko ID |
|--------|------|--------------|
| BTC | Bitcoin | bitcoin |
| ETH | Ethereum | ethereum |
| ADA | Cardano | cardano |
| SOL | Solana | solana |
| XRP | Ripple | ripple |
| DOT | Polkadot | polkadot |
| DOGE | Dogecoin | dogecoin |
| MATIC | Polygon | matic-network |
| AVAX | Avalanche | avalanche-2 |
| LINK | Chainlink | chainlink |
| UNI | Uniswap | uniswap |
| ATOM | Cosmos | cosmos |
| LTC | Litecoin | litecoin |
| BCH | Bitcoin Cash | bitcoin-cash |
| ALGO | Algorand | algorand |
| XLM | Stellar | stellar |
| VET | VeChain | vechain |
| ICP | Internet Computer | internet-computer |
| FIL | Filecoin | filecoin |
| AAVE | Aave | aave |

## Examples

### In "Analyze Individual Crypto" Page:
```
Enter Cryptocurrency to Analyze: SOL
→ Analyzes Solana ✅

Enter Cryptocurrency to Analyze: bitcoin
→ Analyzes Bitcoin ✅

Enter Cryptocurrency to Analyze: shiba-inu
→ Analyzes Shiba Inu ✅
```

### In "Market Data" Page:
```
Enter Cryptocurrency: LINK
→ Shows Chainlink data ✅

Enter Cryptocurrency: pepe
→ Shows Pepe data ✅
```

### In "News & Sentiment" Page:
```
Enter Cryptocurrency Symbol: ADA
→ Searches Cardano news ✅

Enter Cryptocurrency Symbol: DOGE
→ Searches Dogecoin news ✅
```

## Common Issues

### ❌ "Could not fetch historical data"
**Causes:**
1. Invalid CoinGecko ID
2. Newly listed coin (not enough historical data)
3. API rate limiting

**Solutions:**
- Double-check the CoinGecko ID at https://www.coingecko.com/
- Try a more established cryptocurrency
- Wait a minute and try again

### ❌ Technical indicators showing "Insufficient data"
**Cause:** Cryptocurrency doesn't have enough historical data (needs 30+ days)

**Solution:** Choose "30 Days" or longer time period

## Tips

1. **Use symbols for speed**: Just type `BTC` instead of `bitcoin`
2. **Check the ID confirmation**: The app shows which CoinGecko ID it's using below the input
3. **Start with popular coins**: They have more historical data and better news coverage
4. **Case doesn't matter**: `btc`, `BTC`, `Bitcoin` all work for Bitcoin

## Limitations

- Some very new or obscure coins may not have:
  - Sufficient historical data for technical indicators
  - News articles for sentiment analysis
  - Complete market data
- Free CoinGecko API tier has rate limits (10,000 calls/month)

## Popular Cryptocurrencies to Try

**DeFi:**
- `uniswap` (UNI)
- `aave` (AAVE)
- `curve-dao-token` (CRV)
- `maker` (MKR)

**Layer 1:**
- `solana` (SOL)
- `cardano` (ADA)
- `avalanche-2` (AVAX)
- `polkadot` (DOT)
- `cosmos` (ATOM)

**Layer 2:**
- `matic-network` (MATIC/Polygon)
- `arbitrum` (ARB)
- `optimism` (OP)

**Memecoins:**
- `dogecoin` (DOGE)
- `shiba-inu` (SHIB)
- `pepe` (PEPE)

**Stablecoins:**
- `tether` (USDT)
- `usd-coin` (USDC)
- `dai` (DAI)

## Summary

✅ You can analyze **ANY** cryptocurrency on CoinGecko (10,000+ coins)
✅ Use common symbols (BTC, ETH, SOL) for convenience
✅ Use CoinGecko IDs for any other crypto
✅ Find IDs at https://www.coingecko.com/
✅ App shows which ID it's using for confirmation
