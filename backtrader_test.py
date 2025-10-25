from __future__ import (absolute_import, division, print_function,unicode_literals)
import backtrader as bt
import pandas as pd
import backtrader.analyzers as btanalyzers
from get_data import GetData
from strategiat.BaseClasses import StrategyManager
from strategiat.SingleBuyInterfaceTesti import SingleBuyStrategy
from strategiat.sma_cross import SMACross

def calculate_return(initial_cash, final_cash):
    return ((final_cash / initial_cash) - 1) * 100

if __name__ == '__main__':
    
    # Datan saaminen ja alkuparametrit
    data_loader = GetData('^GSPC', '2018-01-01', '1d')
    df = data_loader.load()
    aloitus_rahat = 10000
    sizer = 98
    commission = 0.02
    result_list = []

    # Strategia jossa käydään läpi eri pituuksia nopealle ja hitaalle liukuvalle keskiarvolle
    # Ottaa sisään data, aloitus_rahat, sizer, commission
    # Palauttaa result_list
    """run_iterations = False
    pslows = [50, 100, 150, 200, 250]
    psfasts = [10, 15, 20]
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
"""
    # TODO: Tässä vain kerron luokan 
    strategy_manager = StrategyManager.StrategyManager(df, aloitus_rahat, sizer, commission)
    final_value, sell_count, buy_count = strategy_manager.run(SingleBuyStrategy)
    result_list.append(('SingleBuy', calculate_return(aloitus_rahat, final_value), final_value, sell_count, buy_count))
    
    
    #cerebro.plot()

    par_df = pd.DataFrame(result_list, columns=['strategia', 'return', 'rahaa', 'sellcount', 'buycount'])
    # Sort by 'return'
    par_df = par_df.sort_values(by='return', ascending=False)
    print(par_df)
