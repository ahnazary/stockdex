"""
Moduel for the Ticker class
"""

from stockdex.config import VALID_DATA_SOURCES
from stockdex.digrin_interface import Digrin_Interface
from stockdex.exceptions import WrongDataSource
from stockdex.justetf_interface import JustETF
from stockdex.yahoo_api_interface import YahooAPI
from stockdex.yahoo_web_interface import YahooWeb


class TickerFactory:
    def __init__(
        self, ticker="", isin="", security_type="stock", data_source="yahoo_api"
    ):
        self.ticker_name = ticker
        self.isin = isin
        self.security_type = security_type
        self.data_source = data_source
        self.base_class = self._select_base_class(data_source)
        self._ticker_instance = self._create_ticker()

    def _select_base_class(self, data_source):
        if data_source == "yahoo_web":
            return YahooWeb
        elif data_source == "yahoo_api":
            return YahooAPI
        # TODO: Implement NASDAQInterface when website is stable
        # elif data_source == "nasdaq":
        #     return NASDAQInterface
        elif data_source == "justetf":
            return JustETF
        elif data_source == "digrin":
            return Digrin_Interface
        else:
            raise ValueError(f"Unsupported data source: {data_source}")

    def _create_ticker(self):
        class Ticker(self.base_class):
            def __init__(self, ticker, isin, security_type, data_source):
                super().__init__(ticker, isin, security_type)
                self.ticker = ticker
                self.isin = isin
                self.security_type = security_type

        return Ticker(self.ticker_name, self.isin, self.security_type, self.data_source)

    def get_ticker(self):
        return self._ticker_instance

    @property
    def ticker(self):
        return self._ticker_instance

    @ticker.setter
    def ticker(self, value):
        self._ticker_instance = value

    @property
    def data_source(self):
        return self._data_source

    @data_source.setter
    def data_source(self, value):
        if value not in VALID_DATA_SOURCES.__args__:
            raise WrongDataSource(given_source=value)
        self._data_source = value
