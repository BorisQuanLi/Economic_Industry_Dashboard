import pandas as pd

class DataProcessor:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def calculate_sector_metrics(self, sector: str) -> dict:
        sector_data = self.data[self.data['sector'] == sector]
        return {
            'avg_revenue': sector_data['revenue'].mean(),
            'total_market_cap': sector_data['market_cap'].sum(),
            'profit_margin': (sector_data['profit'] / sector_data['revenue'] * 100).mean()
        }

    def clean_data(self) -> pd.DataFrame:
        return self.data[
            (self.data['revenue'] > 0) & 
            (self.data['profit'].notna()) &
            (self.data['market_cap'] > 0)
        ]

    def aggregate_by_quarter(self, sector: str) -> pd.DataFrame:
        sector_data = self.data[self.data['sector'] == sector]
        return sector_data.groupby(pd.Grouper(key='date', freq='Q')).agg({
            'revenue': 'sum'
        }).reset_index()
