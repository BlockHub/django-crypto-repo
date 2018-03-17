from common.exceptions import NotImplemented

not_implemented = NotImplemented('Method has not been implemented')


class AbstractObserverBot:

    def create_markets(self):
        raise not_implemented

    def update_markets(self):
        raise not_implemented

    def run(self):
        raise not_implemented