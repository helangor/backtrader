import json
import backtrader as bt
from get_data import GetData
from strategiat.BaseStrategy import BaseStrategy

def calculate_return(initial_cash, final_cash):
    return ((final_cash / initial_cash) - 1) * 100

class CerebroManager:
    def __init__(self):
        # Load configuration
        with open('config/trading_config.json', 'r') as config_file:
            config = json.load(config_file)
        
        # Load data
        data_loader = GetData(config["ticker"], config["start_date"], config["interval"])
        df = data_loader.load()
        
        self.cerebro: bt.Cerebro | None = bt.Cerebro()
        self.aloitus_rahat = config["starting_cash"]
        self.cerebro.adddata(bt.feeds.PandasData(dataname=df))
        self.cerebro.addsizer(bt.sizers.PercentSizer, percents=config["sizer"])
        self.cerebro.broker.set_cash(config["starting_cash"])
        self.cerebro.broker.setcommission(commission=config["commission"])

    def run(self, strategy_class: BaseStrategy, strategy_name, result_list, *args, **kwargs):
        self.cerebro.addstrategy(strategy_class, *args, **kwargs)
        self.cerebro.run()
        final_value = self.cerebro.broker.getvalue()
        sell_count = self.cerebro.runstrats[0][0].sellcount
        buy_count = self.cerebro.runstrats[0][0].buycount
        result_list.append(
            [strategy_name, calculate_return(self.aloitus_rahat, final_value), final_value, sell_count, buy_count]
        )
        
    def plot (self):
        self.cerebro.plot()