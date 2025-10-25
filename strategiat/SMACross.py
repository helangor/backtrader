import backtrader as bt
from strategiat.BaseStrategy import BaseStrategy

class SMACross(BaseStrategy):
    params = dict(
        pfast=10,  # period for the fast moving average
        pslow=30,  # period for the slow moving average
        printlog=False,
    )

    def __init__(self):
        # Call the parent class's __init__ method
        super().__init__()
        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal
        
    def next(self):
        if self.order:
            return

        # Positio tarkoittaa, että meillä on osakkeita hallussa
        if not self.position:
            if self.crossover > 0:  # if fast crosses slow to the upside
                self.buy()  # enter long

        if self.position:
            if self.crossover < 0:  # in the market & cross to the downside
                self.close()  # close long position