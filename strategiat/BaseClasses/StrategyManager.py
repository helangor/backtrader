from pandas import DataFrame
import backtrader as bt

from strategiat.BaseClasses.BaseStrategy import BaseStrategy

#TODO: Tämä handlaa crebro:n ja strategian ajamisen, palauttaa result_list

class StrategyManager:
    def __init__(self, data: DataFrame, aloitus_rahat: float, sizer: int, commission: float):
        """
        Configures the strategy with the required parameters.
        """
        self.data: DataFrame | None = bt.feeds.PandasData(dataname=data)
        self.aloitus_rahat: float = aloitus_rahat
        self.sizer: int = sizer
        self.commission: float = commission
        self.cerebro: bt.Cerebro | None = bt.Cerebro()

    def init_new_cerebro(self):
        self.cerebro.adddata(self.data)
        # Prosentti on prosentti käteisestä joka sijoitetaan. Jos 95% ja komissio 6% niin 101% eli ei ole rahaa ostaa.
        self.cerebro.addsizer(bt.sizers.PercentSizer, percents=self.sizer)
        self.cerebro.broker.set_cash(self.aloitus_rahat)
        self.cerebro.broker.setcommission(commission=self.commission)

    # Palauttaa result_list
    def run(self, strategy_class: BaseStrategy):
        self.cerebro.addstrategy(strategy_class)
        self.cerebro.run()
        final_value = self.cerebro.broker.getvalue()
        sell_count = 1 #self.cerebro.runstrats[0][0].sellcount
        buy_count = 1 #self.cerebro.runstrats[0][0].buycount
        return final_value, sell_count, buy_count