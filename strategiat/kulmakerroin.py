import backtrader as bt
from enum import Enum

class Suunta(Enum):
    NOUSU = "nousu"
    LASKU = "lasku"
    MUUTTUMATON = "muuttumaton"


class Kulmakerroin(bt.Strategy):
    params = (
        ('maperiod', 15),
        ('printlog', False),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.sellcount = 0
        self.buycount = 0

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buycount += 1
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                    order.executed.value,
                    order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.sellcount += 1
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                        (order.executed.price,
                        order.executed.value,
                        order.executed.comm))

            self.bar_executed = len(self)

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        
    def get_suunnanmuutos(self, sma):
        suunta_nyt = self.get_suunta(sma[0], sma[-5])
        suunta_aikaisemmin = self.get_suunta(sma[-5], sma[-10])
        if suunta_nyt != suunta_aikaisemmin:
            return suunta_nyt
        return Suunta.MUUTTUMATON

    def get_suunta(self, arvo_nyt, arvo_aikaisemmin):
        muutos_prosenteissa = (arvo_nyt/arvo_aikaisemmin) * 100
        prosentti_raja = 0.08  # Valitaan sopiva kynnysarvo
        if muutos_prosenteissa > 100 + prosentti_raja:
            return Suunta.NOUSU
        elif muutos_prosenteissa < 100 - prosentti_raja:
            return Suunta.LASKU
        else:
            return Suunta.MUUTTUMATON
        
    def laske_kulmakerroin(self, arvo_nyt, arvo_eilen):
        return (arvo_nyt - arvo_eilen) / 1

    def next(self):
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        suunta = self.get_suunnanmuutos(self.sma)

        # Positio tarkoittaa, että meillä on osakkeita hallussa
        if not self.position:
            if suunta == Suunta.NOUSU:
                self.order = self.buy()
        if self.position:
            if suunta == Suunta.LASKU:
                self.order = self.sell()
