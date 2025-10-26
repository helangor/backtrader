from __future__ import (absolute_import, division, print_function,unicode_literals)
import pandas as pd
from CerebroManager import CerebroManager
from strategiat.SMACross import SMACross
from strategiat.SingleBuy import SingleBuy

if __name__ == '__main__':
    result_list = []

    pslows = [40]
    psfasts = [10, 12]
    iteration_count = 0
    total_iterations = len(psfasts) * len(pslows)
    for psfast in psfasts:
        for pslow in pslows:
            iteration_count += 1
            print(f"Running iteration {iteration_count} of {total_iterations}")
            cerebro = CerebroManager()
            cerebro.run(SMACross, f'SMACross: {psfast}/{pslow}', result_list, pfast=psfast, pslow=pslow)
            cerebro.plot()
    CerebroManager().run(SingleBuy, 'SingleBuy', result_list)

    par_df = pd.DataFrame(result_list, columns=['strategia', 'return', 'rahaa', 'sellcount', 'buycount'])
    par_df = par_df.sort_values(by='return', ascending=False)
    print(par_df)
