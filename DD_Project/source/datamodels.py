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
    insider_data_df: pd.DataFrame
