import yfinance as yf
import os
import os.path 
import pandas as pd

class GetData:
    def __init__(self, ticker, start, interval):
        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.data_folder = 'datas'
        os.makedirs(self.data_folder, exist_ok=True)
        self.csv_file = os.path.join(self.data_folder, f'{ticker}.csv')

    def load(self):
        if os.path.exists(self.csv_file):
            df = pd.read_csv(self.csv_file, index_col=0, parse_dates=True)
        else:
            df = yf.download(self.ticker, start=self.start, interval=self.interval)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
            df.index = df.index.tz_localize(None)
            df.to_csv(self.csv_file)
        return df
