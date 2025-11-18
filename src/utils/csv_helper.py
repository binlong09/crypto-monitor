"""
CSV Helper Utilities
Helper functions for working with CSV files
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional


def validate_holdings_csv(csv_path: str) -> tuple[bool, str]:
    """
    Validate holdings CSV format

    Returns:
        (is_valid, error_message)
    """
    try:
        df = pd.read_csv(csv_path)

        # Check required columns
        required = ['symbol', 'amount']
        missing = [col for col in required if col not in df.columns]

        if missing:
            return False, f"Missing required columns: {', '.join(missing)}"

        # Check data types
        if not pd.api.types.is_numeric_dtype(df['amount']):
            return False, "Column 'amount' must be numeric"

        # Check for valid symbols
        valid_symbols = ['BTC', 'ETH']
        invalid = [s for s in df['symbol'].str.upper() if s not in valid_symbols]

        if invalid:
            return False, f"Invalid symbols (only BTC and ETH supported): {', '.join(set(invalid))}"

        return True, "Valid"

    except Exception as e:
        return False, f"Error reading CSV: {str(e)}"


def validate_defi_csv(csv_path: str) -> tuple[bool, str]:
    """
    Validate DeFi positions CSV format

    Returns:
        (is_valid, error_message)
    """
    try:
        df = pd.read_csv(csv_path)

        # Check required columns
        required = ['protocol', 'asset', 'amount', 'apr', 'start_date']
        missing = [col for col in required if col not in df.columns]

        if missing:
            return False, f"Missing required columns: {', '.join(missing)}"

        # Check data types
        if not pd.api.types.is_numeric_dtype(df['amount']):
            return False, "Column 'amount' must be numeric"

        if not pd.api.types.is_numeric_dtype(df['apr']):
            return False, "Column 'apr' must be numeric"

        # Validate dates
        try:
            pd.to_datetime(df['start_date'])
        except:
            return False, "Column 'start_date' must be valid dates (YYYY-MM-DD)"

        return True, "Valid"

    except Exception as e:
        return False, f"Error reading CSV: {str(e)}"


def export_portfolio_snapshot(portfolio_df: pd.DataFrame, output_path: str):
    """Export portfolio snapshot to CSV"""
    portfolio_df.to_csv(output_path, index=False)
    print(f"Portfolio snapshot exported to: {output_path}")


def get_latest_csv(directory: str, pattern: str = "*.csv") -> Optional[str]:
    """
    Get the most recently modified CSV file in a directory

    Args:
        directory: Directory path
        pattern: File pattern (default: *.csv)

    Returns:
        Path to latest CSV or None
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return None

    csv_files = list(dir_path.glob(pattern))
    if not csv_files:
        return None

    latest = max(csv_files, key=lambda p: p.stat().st_mtime)
    return str(latest)
