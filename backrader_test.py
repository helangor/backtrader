from __future__ import (absolute_import, division, print_function,unicode_literals)
import backtrader as bt
import yfinance as yf
import pandas as pd
import os
import os.path 

class TestStrategy(bt.Strategy):
    params = (
        ('maperiod',15), # Tuple of tuples containing any variable settings required by the strategy.
        ('printlog',False), # Stop printing the log of the trading strategy
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        print(f'Moving Average Period: {self.params.maperiod}')
        # Add SimpleMovingAverage indicator for use in the trading strategy
        self.sma = bt.indicators.SimpleMovingAverage( 
            self.datas[0], period=self.params.maperiod)

        # Indicators for the plotting show
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
                                            subplot=True)
        bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=10)
        bt.indicators.ATR(self.datas[0], plot=False)

    def notify_order(self, order):
        # 1. If order is submitted/accepted, do nothing 
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 2. If order is buy/sell executed, report price executed
        if order.status in [order.Completed]: 
            if order.isbuy():

                
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

            self.bar_executed = len(self) #when was trade executed
        # 3. If order is canceled/margin/rejected, report order canceled
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

    def next(self):
        # Log the closing prices of the series from the reference

        if self.order: # check if order is pending, if so, then break out
            return
                
        # since there is no order pending, are we in the market?    


        if not self.position: # not in the market
            if self.dataclose[0] > self.sma[0]:
                self.order = self.buy()           
        else: # in the market
            if self.dataclose[0] < self.sma[0]:
                self.order = self.sell()

class GetData:
    def __init__(self, ticker, start, interval):
        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.csv_file = f'{ticker}.csv'

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


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    data_loader = GetData('BTC-USD', '2022-01-01', '1d')
    df = data_loader.load()
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)

    # Prosentti on prosentti käteisestä joka sijoitetaan. Jos 95% ja komissio 6% niin 101% eli ei ole rahaa ostaa.
    cerebro.addsizer(bt.sizers.PercentSizer, percents=95) 

    aloitus_rahat = 10000
    cerebro.broker.set_cash(aloitus_rahat)
    # Set the commission - 1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.02)
    # Komissio + prosentti = kokonaiskulu. Jos menee yli 100% niin ei ole rahaa ostaa.

    maperiods = [1, 5]

    cerebro.optstrategy(TestStrategy, maperiod=maperiods)

    #cerebro.addstrategy(TestStrategy, maperiod=maperiod)
    cerebro.run()

    # Eli haluan tietää lopullisen arvon suhteessa alkupääomaan.
    final_value = cerebro.broker.getvalue()
    voitto_ratio = ((final_value / aloitus_rahat) - 1) * 100
    print('Monta prosenttia muuttui: %.2f %%' % voitto_ratio)
    # Plot the result
    #cerebro.plot()