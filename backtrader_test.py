from __future__ import (absolute_import, division, print_function,unicode_literals)
import backtrader as bt
import pandas as pd
import backtrader.analyzers as btanalyzers
from get_data import GetData
from strategiat.single_buy import SingleBuy
from strategiat.sma_cross import SMACross

def init_new_cerebro():
    data = bt.feeds.PandasData(dataname=df)
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    # Prosentti on prosentti käteisestä joka sijoitetaan. Jos 95% ja komissio 6% niin 101% eli ei ole rahaa ostaa.
    cerebro.addsizer(bt.sizers.PercentSizer, percents=sizer) 
    cerebro.broker.set_cash(aloitus_rahat)
    cerebro.broker.setcommission(commission=commission)
    return cerebro

def calculate_return(initial_cash, final_cash):
    return ((final_cash / initial_cash) - 1) * 100

def single_buy_test():
    cerebro.addstrategy(SingleBuy)
    cerebro.run()
    final_value = cerebro.broker.getvalue()
    sell_count = cerebro.runstrats[0][0].sellcount
    buy_count = cerebro.runstrats[0][0].buycount
    return final_value, sell_count, buy_count

if __name__ == '__main__':
    
    # Datan saaminen ja alkuparametrit
    data_loader = GetData('^GSPC', '2018-01-01', '1d')
    df = data_loader.load()
    aloitus_rahat = 10000
    pslows = [50, 100, 150, 200, 250]
    psfasts = [10, 15, 20]
    sizer = 98
    commission = 0.02
    run_iterations = True
    
    result_list = []
    iteration_count = 0
    total_iterations = len(psfasts) * len(pslows)
    
    if run_iterations:
        for psfast in psfasts:
            for pslow in pslows:             
                iteration_count += 1
                print(f"Running iteration {iteration_count} of {total_iterations}")
                cerebro = init_new_cerebro()
                cerebro.addstrategy(SMACross, pfast=psfast, pslow=pslow, printlog=False)
                cerebro.run()
                final_value = cerebro.broker.getvalue()
                result_list.append((f"{psfast}/{pslow}", calculate_return(aloitus_rahat, final_value), final_value, cerebro.runstrats[0][0].sellcount, cerebro.runstrats[0][0].buycount))

    # Strategia jossa tehdään vain yksi osto heti
    cerebro = init_new_cerebro()
    final_value, sell_count, buy_count = single_buy_test()
    result_list.append(('SingleBuy', calculate_return(aloitus_rahat, final_value), final_value, sell_count, buy_count))
    cerebro.plot()

    par_df = pd.DataFrame(result_list, columns=['strategia', 'return', 'rahaa', 'sellcount', 'buycount'])
    # Sort by 'return'
    par_df = par_df.sort_values(by='return', ascending=False)
    print(par_df)
