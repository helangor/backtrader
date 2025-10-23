from __future__ import (absolute_import, division, print_function,unicode_literals)
import backtrader as bt
import yfinance as yf
import pandas as pd
import os
import os.path 
import backtrader.analyzers as btanalyzers

class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
        ('printlog', False),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.sellcount = 0
        self.buycount = 0

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buycount += 1
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                    order.executed.value,
                    order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.sellcount += 1
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                        (order.executed.price,
                        order.executed.value,
                        order.executed.comm))

            self.bar_executed = len(self)

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        
    def laske_kulmakerroin(self, p1, p2):
        # TODO: tarkista mikä olisi riittävän korkea kulmakerroin
        return (p2/p1)

    def next(self):
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        
        #sma muuttaa suuntaa
        sma_muuttuu_nousevaksi = self.sma[0] > self.sma[-1] and self.sma[-1] <= self.sma[-2]
        if (sma_muuttuu_nousevaksi):
            print("SMA nousee")
            print(self.laske_kulmakerroin(self.sma[0], self.sma[-1]))
            print(self.sma[0], self.sma[-1], self.sma[-2])
        sma_muuttuu_laskevaksi = self.sma[0] < self.sma[-1] and self.sma[-1] >= self.sma[-2]

        # Positio tarkoittaa, että meillä on osakkeita hallussa
        if not self.position:
            if sma_muuttuu_nousevaksi:
                self.order = self.buy()
        if self.position:
            if sma_muuttuu_laskevaksi:
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
    
    # Datan saaminen ja alkuparametrit
    data_loader = GetData('BTC-USD', '2022-01-01', '1d')
    df = data_loader.load()
    aloitus_rahat = 10000
    maperiods = [200]
    sizer = 98
    commission = 0.02
    result_list = []

    for period in maperiods:             
        data = bt.feeds.PandasData(dataname=df)
        cerebro = bt.Cerebro()
        cerebro.adddata(data)

        # Prosentti on prosentti käteisestä joka sijoitetaan. Jos 95% ja komissio 6% niin 101% eli ei ole rahaa ostaa.
        cerebro.addsizer(bt.sizers.PercentSizer, percents=sizer) 


        cerebro.broker.set_cash(aloitus_rahat)
        cerebro.broker.setcommission(commission=commission)
        # Komissio + prosentti = kokonaiskulu. Jos menee yli 100% niin ei ole rahaa ostaa.

        cerebro.addstrategy(TestStrategy, maperiod=period, printlog=False)
        cerebro.run()

        # Eli haluan tietää lopullisen arvon suhteessa alkupääomaan.
        voitto_ratio = ((cerebro.broker.getvalue() / aloitus_rahat) - 1) * 100
        result_list.append((period, voitto_ratio, cerebro.broker.getvalue(),cerebro.runstrats[0][0].sellcount, cerebro.runstrats[0][0].buycount))
        # Plot the result
        cerebro.plot()
        # Create a Cerebro entity
        # Create a Data Feed
    par_df = pd.DataFrame(result_list, columns = ['maperiod', 'return', 'rahaa','sellcount', 'buycount'])
    print(par_df)
