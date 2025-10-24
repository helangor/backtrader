import backtrader as bt

# Tämän tarkoituksena nähdä tuotto pelkällä yhdellä ostolla alussa ilman myyntejä
class SingleBuy(bt.Strategy):   
    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.sellcount = 0
        self.buycount = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buycount += 1
            else:  # Sell
                self.sellcount += 1
            self.bar_executed = len(self)

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        
    def next(self):
        if not self.position:
            self.order = self.buy()