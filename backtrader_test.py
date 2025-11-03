from __future__ import (absolute_import, division, print_function,unicode_literals)
import pandas as pd
from CerebroManager import CerebroManager
from strategiat.SMACross import SMACrossLoop
from strategiat.SingleBuy import SingleBuy


if __name__ == '__main__':
    result_list = []

    SMACrossLoop()
    CerebroManager().run(SingleBuy, 'SingleBuy', result_list)

    par_df = pd.DataFrame(result_list, columns=['strategia', 'return', 'rahaa', 'sellcount', 'buycount'])
    par_df = par_df.sort_values(by='return', ascending=False)
    print(par_df)


