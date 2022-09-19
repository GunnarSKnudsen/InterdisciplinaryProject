from dataclasses import dataclass
import pandas as pd

@dataclass
class Company:
    company_type: str
    isin: str
    name: str
    ticker: str
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    return_index_df: pd.DataFrame

@dataclass
class Trade:
    FilingDate: pd.Timestamp
    TradeDate: pd.Timestamp
    Ticker: str
    InsiderName: str
    Title: str
    TradeType: str
    Price: str
    Qty: str
    Owned: str
    delta_Own: str
    Value: str