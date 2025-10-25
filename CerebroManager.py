from pandas import DataFrame
import backtrader as bt
from strategiat.BaseStrategy import BaseStrategy

def calculate_return(initial_cash, final_cash):
    return ((final_cash / initial_cash) - 1) * 100


#TODO: Tänne parametrit ja konffit backtrader_test.py:stä

class CerebroManager:
    def __init__(self, data: DataFrame, aloitus_rahat: float, sizer: int, commission: float):
        self.cerebro: bt.Cerebro | None = bt.Cerebro()
        self.aloitus_rahat = aloitus_rahat
        self.cerebro.adddata(bt.feeds.PandasData(dataname=data))
        self.cerebro.addsizer(bt.sizers.PercentSizer, percents=sizer)
        self.cerebro.broker.set_cash(aloitus_rahat)
        self.cerebro.broker.setcommission(commission=commission)

    def run(self, strategy_class: BaseStrategy):
        self.cerebro.addstrategy(strategy_class)
        self.cerebro.run()
        final_value = self.cerebro.broker.getvalue()
        sell_count = self.cerebro.runstrats[0][0].sellcount
        buy_count = self.cerebro.runstrats[0][0].buycount
        return [strategy_class.__name__, calculate_return(self.aloitus_rahat, final_value), final_value, sell_count, buy_count]