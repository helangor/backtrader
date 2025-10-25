from strategiat.BaseClasses.BaseStrategy import BaseStrategy

class SingleBuyStrategy(BaseStrategy):   
    def next(self):
        if not self.position:
            self.order = self.buy()