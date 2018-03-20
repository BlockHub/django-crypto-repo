from binance_app.models import Ticker


class TickerHandler:
    def __init__(self, market, save=True):
        self.market = market
        self.save = save

    def __call__(self, msg):
        """
        :param msg:
            {
                'e': '24hrTicker',
                'E': 1521537885137,
                's': 'XLMBTC',
                'p': '0.00000062',
                'P': '2.266',
                'w': '0.00002798',
                'x': '0.00002739',
                'c': '0.00002798',
                'Q': '149.00000000',
                'b': '0.00002791',
                'B': '1258.00000000',
                'a': '0.00002797',
                'A': '255.00000000',
                'o': '0.00002736',
                'h': '0.00002988',
                'l': '0.00002640',
                'v': '83828520.00000000',
                'q': '2345.89922247',
                'O': 1521451485135,
                'C': 1521537885135,
                'F': 6636438,
                'L': 6688790,
                'n': 52353
            }
        :return:
        models.Ticker()
        """
        tkr = self.__cast_ticker(msg)
        if self.save:
            tkr.save()
        return tkr

    def __cast_ticker(self, msg):
        return Ticker.objects.create(
            market=self.market,
            event_time=msg['E'],
            price_change=msg['p'],
            price_change_percent=msg['P'],
            weighted_average_price=msg['w'],
            prev_close_price=msg['x'],
            close_trades_quantity=msg['c'],
            best_bid_price=msg['Q'],
            best_bid_quantity=msg['B'],
            best_ask_price=msg['a'],
            best_ask_quantity=msg['A'],
            open_price=msg['o'],
            high_price=msg['h'],
            low_price=msg['l'],
            total_base_traded_volume=msg['v'],
            total_quote_traded_volume=msg['q'],
        )


class OrderBookHandler:
    def __init__(self, market, save=True):
        self.market = market
        self.save = save



