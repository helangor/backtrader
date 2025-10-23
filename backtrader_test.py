from __future__ import (absolute_import, division, print_function,unicode_literals)
import backtrader as bt
import pandas as pd
import backtrader.analyzers as btanalyzers
from get_data import GetData
from strategiat.sma_cross import SMACross

if __name__ == '__main__':
    
    # Datan saaminen ja alkuparametrit
    data_loader = GetData('BTC-USD', '2022-01-01', '1d')
    df = data_loader.load()
    aloitus_rahat = 10000
    maperiods = [10, 20, 50, 100, 150, 200]
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

        cerebro.addstrategy(SMACross, pfast=5, pslow=period, printlog=False)
        cerebro.run()

        voitto_ratio = ((cerebro.broker.getvalue() / aloitus_rahat) - 1) * 100
        result_list.append((period, voitto_ratio, cerebro.broker.getvalue(),cerebro.runstrats[0][0].sellcount, cerebro.runstrats[0][0].buycount))
        #cerebro.plot()

    par_df = pd.DataFrame(result_list, columns = ['maperiod', 'return', 'rahaa','sellcount', 'buycount'])
    print(par_df)
