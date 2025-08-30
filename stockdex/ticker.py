from stockdex.config import VALID_SECURITY_TYPES
from stockdex.digrin_interface import DigrinInterface
from stockdex.finviz_interface import FinvizInterface
from stockdex.justetf_interface import JustETF
from stockdex.macrotrends_interface import MacrotrendsInterface
from stockdex.sankey_charts import SankeyCharts
from stockdex.yahoo_api_interface import YahooAPI
from stockdex.yahoo_web_interface import YahooWeb


class Ticker(
    YahooAPI,
    JustETF,
    DigrinInterface,
    YahooWeb,
    MacrotrendsInterface,
    SankeyCharts,
    FinvizInterface,
):
    """
    Class for the Ticker
    """

    def __init__(
        self,
        ticker: str = "",
        isin: str = "",
        security_type: VALID_SECURITY_TYPES = "stock",
    ) -> None:
        """
        Initialize the Ticker class

        Args:
        ticker (str): The ticker of the stock
        isin (str): The ISIN of the etf
        security_type (str): The security type of the ticker
            default is "stock"
        """

        self.ticker = ticker
        self.isin = isin
        self.security_type = security_type if security_type else "stock"

        if not ticker and not isin:
            raise Exception("Please provide either a ticker or an ISIN")

        super().__init__(ticker=ticker, isin=isin, security_type=security_type)
