from __future__ import (absolute_import, division, print_function,unicode_literals)
import backtrader as bt
import pandas as pd
import backtrader.analyzers as btanalyzers
from get_data import GetData
from strategiat.sma_cross import SMACross

if __name__ == '__main__':
    
    # Datan saaminen ja alkuparametrit
    data_loader = GetData('BTC-USD', '2018-01-01', '1d')
    df = data_loader.load()
    aloitus_rahat = 10000
    pslows = [50, 100, 150, 200, 250]
    psfasts = [2, 5, 10, 15, 20]
    sizer = 98
    commission = 0.02
    result_list = []

    for psfast in psfasts:
        for pslow in pslows:             
            data = bt.feeds.PandasData(dataname=df)
            cerebro = bt.Cerebro()
            cerebro.adddata(data)

            # Prosentti on prosentti käteisestä joka sijoitetaan. Jos 95% ja komissio 6% niin 101% eli ei ole rahaa ostaa.
            cerebro.addsizer(bt.sizers.PercentSizer, percents=sizer) 
            cerebro.broker.set_cash(aloitus_rahat)
            cerebro.broker.setcommission(commission=commission)
            cerebro.addstrategy(SMACross, pfast=psfast, pslow=pslow, printlog=False)
            cerebro.run()

            voitto_ratio = ((cerebro.broker.getvalue() / aloitus_rahat) - 1) * 100
            result_list.append((pslow, psfast, voitto_ratio, cerebro.broker.getvalue(),cerebro.runstrats[0][0].sellcount, cerebro.runstrats[0][0].buycount))
            #cerebro.plot()

    par_df = pd.DataFrame(result_list, columns=['pslow', 'psfast', 'return', 'rahaa', 'sellcount', 'buycount'])

    # Sort by 'return'
    par_df = par_df.sort_values(by='return', ascending=False)
    print(par_df)
