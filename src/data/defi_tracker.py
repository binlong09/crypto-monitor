"""
DeFi Protocol Tracker
Track staking, liquidity pools, and yield farming positions
"""

import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import time


class DeFiTracker:
    """Track DeFi protocol positions and yields"""

    def __init__(self):
        self.session = requests.Session()

    def get_eth_staking_info(self) -> Optional[Dict]:
        """
        Get Ethereum staking information

        Returns basic ETH 2.0 staking metrics
        """
        try:
            # Get ETH staking APR from various sources
            # Using CoinGecko for ETH data
            response = requests.get(
                'https://api.coingecko.com/api/v3/coins/ethereum',
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            market_data = data.get('market_data', {})

            return {
                'asset': 'ETH',
                'protocol': 'Ethereum 2.0 Staking',
                'estimated_apr': 3.5,  # Approximate current ETH staking APR
                'staked_amount': None,  # User must input manually
                'current_price': market_data.get('current_price', {}).get('usd', 0),
                'last_updated': datetime.now()
            }
        except Exception as e:
            print(f"Error fetching ETH staking info: {e}")
            return None

    def get_defi_protocols_tvl(self) -> pd.DataFrame:
        """
        Get Total Value Locked (TVL) for major DeFi protocols

        Uses DeFiLlama API (free, no auth required)
        """
        try:
            response = requests.get('https://api.llama.fi/protocols', timeout=10)
            response.raise_for_status()
            data = response.json()

            # Filter for major protocols
            protocols = []
            for protocol in data[:20]:  # Top 20 protocols
                protocols.append({
                    'name': protocol.get('name'),
                    'symbol': protocol.get('symbol', '').upper(),
                    'tvl': protocol.get('tvl', 0),
                    'chain': protocol.get('chain', 'Multi-chain'),
                    'category': protocol.get('category', 'Unknown'),
                    'change_1d': protocol.get('change_1d', 0),
                    'change_7d': protocol.get('change_7d', 0),
                })

            df = pd.DataFrame(protocols)
            return df.sort_values('tvl', ascending=False)

        except Exception as e:
            print(f"Error fetching DeFi protocols: {e}")
            return pd.DataFrame()

    def get_protocol_info(self, protocol_slug: str) -> Optional[Dict]:
        """
        Get detailed information about a specific DeFi protocol

        Args:
            protocol_slug: Protocol identifier (e.g., 'uniswap', 'aave')
        """
        try:
            response = requests.get(
                f'https://api.llama.fi/protocol/{protocol_slug}',
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            return {
                'name': data.get('name'),
                'symbol': data.get('symbol', '').upper(),
                'tvl': data.get('tvl', 0),
                'chain': data.get('chain', 'Multi-chain'),
                'category': data.get('category'),
                'description': data.get('description', ''),
                'url': data.get('url', ''),
                'twitter': data.get('twitter'),
                'audit_links': data.get('audit_links', []),
                'chains': data.get('chains', []),
                'chainTvls': data.get('chainTvls', {}),
                'change_1h': data.get('change_1h', 0),
                'change_1d': data.get('change_1d', 0),
                'change_7d': data.get('change_7d', 0),
            }
        except Exception as e:
            print(f"Error fetching protocol info for {protocol_slug}: {e}")
            return None

    def calculate_yield_position(
        self,
        protocol: str,
        asset: str,
        amount: float,
        apr: float,
        days_held: int = 30
    ) -> Dict:
        """
        Calculate yield farming position value

        Args:
            protocol: Name of DeFi protocol
            asset: Asset symbol (e.g., 'ETH', 'BTC')
            amount: Amount of asset deposited
            apr: Annual Percentage Rate (as decimal, e.g., 0.05 for 5%)
            days_held: Number of days position has been held

        Returns:
            Dict with yield calculation details
        """
        daily_rate = apr / 365
        accrued_yield = amount * daily_rate * days_held

        return {
            'protocol': protocol,
            'asset': asset,
            'principal': amount,
            'apr': apr * 100,  # Convert to percentage
            'days_held': days_held,
            'accrued_yield': accrued_yield,
            'total_value': amount + accrued_yield,
            'daily_yield': amount * daily_rate,
            'projected_annual_yield': amount * apr
        }

    def get_staking_yields(self) -> pd.DataFrame:
        """
        Get current staking/yield farming rates for popular protocols

        Note: Rates are approximate and should be verified on actual protocols
        """
        # This is a simplified version - in production, you'd fetch real-time rates
        # from various DeFi protocol APIs
        yields = [
            {
                'protocol': 'Ethereum 2.0',
                'asset': 'ETH',
                'type': 'Staking',
                'apr': 3.5,
                'risk': 'Low',
                'liquidity': 'Locked'
            },
            {
                'protocol': 'Lido',
                'asset': 'stETH',
                'type': 'Liquid Staking',
                'apr': 3.3,
                'risk': 'Low-Medium',
                'liquidity': 'Liquid'
            },
            {
                'protocol': 'Aave',
                'asset': 'ETH',
                'type': 'Lending',
                'apr': 1.5,
                'risk': 'Low-Medium',
                'liquidity': 'Liquid'
            },
            {
                'protocol': 'Uniswap V3',
                'asset': 'ETH-USDC',
                'type': 'Liquidity Pool',
                'apr': 8.5,
                'risk': 'Medium',
                'liquidity': 'Liquid'
            },
            {
                'protocol': 'Curve',
                'asset': 'Stablecoins',
                'type': 'Liquidity Pool',
                'apr': 4.2,
                'risk': 'Low-Medium',
                'liquidity': 'Liquid'
            }
        ]

        return pd.DataFrame(yields)

    def parse_defi_positions_csv(self, csv_path: str) -> pd.DataFrame:
        """
        Parse DeFi positions from CSV file

        Expected CSV format:
        protocol,asset,amount,apr,start_date
        Ethereum 2.0,ETH,5.5,3.5,2024-01-15
        Lido,stETH,2.3,3.3,2024-02-20

        Returns:
            DataFrame with position details and calculated yields
        """
        try:
            df = pd.read_csv(csv_path)

            # Calculate yields for each position
            df['start_date'] = pd.to_datetime(df['start_date'])
            df['days_held'] = (datetime.now() - df['start_date']).dt.days
            df['daily_yield'] = df['amount'] * (df['apr'] / 100 / 365)
            df['accrued_yield'] = df['daily_yield'] * df['days_held']
            df['current_value'] = df['amount'] + df['accrued_yield']

            return df

        except Exception as e:
            print(f"Error parsing DeFi positions CSV: {e}")
            return pd.DataFrame()

    def create_sample_defi_csv(self, output_path: str):
        """Create a sample DeFi positions CSV template"""
        sample_data = pd.DataFrame({
            'protocol': ['Ethereum 2.0', 'Lido', 'Aave'],
            'asset': ['ETH', 'stETH', 'ETH'],
            'amount': [0.0, 0.0, 0.0],
            'apr': [3.5, 3.3, 1.5],
            'start_date': ['2024-01-01', '2024-01-01', '2024-01-01']
        })

        sample_data.to_csv(output_path, index=False)
        print(f"Sample DeFi positions template created at: {output_path}")
