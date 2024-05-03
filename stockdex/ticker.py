"""
Moduel for the Ticker class
"""

from stockdex.config import VALID_DATA_SOURCES, VALID_SECURITY_TYPES
from stockdex.digrin_interface import Digrin_Interface
from stockdex.exceptions import WrongDataSource
from stockdex.justetf_interface import JustETF
from stockdex.nasdaq_interface import NASDAQInterface
from stockdex.yahoo_api_interface import YahooAPI
from stockdex.yahoo_web_interface import YahooWeb

# # def ticker_factory(data_source_class):
# # #YahooAPI, JustETF, NASDAQInterface, Digrin_Interface, YahooWeb
# #     class TickerFactory(data_source):
# #         pass


# class Ticker:
#     """
#     Class for the Ticker
#     """

#     def __init__(
#         self,
#         ticker: str = "",
#         isin: str = "",
#         security_type: VALID_SECURITY_TYPES = "stock",
#         data_source: VALID_DATA_SOURCES = "yahoo_api",
#     ) -> None:
#         """
#         Initialize the Ticker class

#         Args:
#         ticker (str): The ticker of the stock
#         isin (str): The ISIN of the etf
#         security_type (str): The security type of the ticker
#             default is "stock"
#         """
#         self.ticker = ticker
#         self.isin = isin
#         self.security_type = security_type
#         self.data_source = data_source

#     # @property
#     # def data_source(self):
#     #     return self._data_source

#     # @data_source.setter
#     # def data_source(self, value):
#     #     if value not in VALID_DATA_SOURCES.__args__:
#     #         raise WrongDataSource(given_source=value)
#     #     self._data_source = value


# def build_ticker(
#     data_source: VALID_DATA_SOURCES = "yahoo_api",
# ):

#     if data_source == "yahoo_web":
#         base_class = YahooWeb
#     elif data_source == "yahoo_api":
#         base_class = YahooAPI
#     elif data_source == "nasdaq":
#         base_class = NASDAQInterface
#     elif data_source == "justetf":
#         base_class = JustETF
#     elif data_source == "digrin":
#         base_class = Digrin_Interface
#     else:
#         raise WrongDataSource(given_source=data_source)

#     class Ticker(base_class):
#         """
#         Class for the Ticker
#         """

#         def __init__(
#             self,
#             ticker: str = "",
#             isin: str = "",
#             security_type: VALID_SECURITY_TYPES = "stock",
#             data_source: VALID_DATA_SOURCES = "yahoo_api",
#         ) -> None:
#             """
#             Initialize the Ticker class

#             Args:
#             ticker (str): The ticker of the stock
#             isin (str): The ISIN of the etf
#             security_type (str): The security type of the ticker
#                 default is "stock"
#             """
#             self.ticker = ticker
#             self.isin = isin
#             self.security_type = security_type
#             self.data_source = data_source

#     return Ticker


class TickerFactory:
    def __init__(
        self, ticker="", isin="", security_type="stock", data_source="yahoo_api"
    ):
        self.ticker = ticker
        self.isin = isin
        self.security_type = security_type
        self.data_source = data_source
        self.base_class = self._select_base_class(data_source)
        self.ticker_instance = self._create_ticker()

    def _select_base_class(self, data_source):
        if data_source == "yahoo_web":
            return YahooWeb
        elif data_source == "yahoo_api":
            return YahooAPI
        elif data_source == "nasdaq":
            return NASDAQInterface
        elif data_source == "justetf":
            return JustETF
        elif data_source == "digrin":
            return Digrin_Interface
        else:
            raise ValueError(f"Unsupported data source: {data_source}")

    def _create_ticker(self):
        class Ticker(self.base_class):
            def __init__(self, ticker, isin, security_type, data_source):
                super().__init__()
                self.ticker = ticker
                self.isin = isin
                self.security_type = security_type
                self.data_source = data_source

        return Ticker(self.ticker, self.isin, self.security_type, self.data_source)

    def get_ticker(self):
        return self.ticker_instance

    @property
    def ticker(self):
        return self.ticker_instance

    @ticker.setter
    def ticker(self, value):
        self.ticker_instance = value
