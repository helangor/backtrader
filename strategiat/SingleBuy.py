from strategiat.BaseStrategy import BaseStrategy

class SingleBuy(BaseStrategy):   
    def next(self):
        if not self.position:
            self.order = self.buy()