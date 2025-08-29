from stockdex.config import VALID_SECURITY_TYPES
from stockdex.digrin_interface import DigrinInterface
from stockdex.justetf_interface import JustETF
from stockdex.macrotrends_interface import MacrotrendsInterface
from stockdex.sankey_charts import SankeyCharts
from stockdex.yahoo_api_interface import YahooAPI
from stockdex.yahoo_web_interface import YahooWeb
from stockdex.finviz_interface import FinvizInterface


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
        if not ticker and not isin:
            raise Exception("Please provide either a ticker or an ISIN")

        # Call parent class constructors to ensure all attributes are initialized
        super().__init__(ticker=ticker, isin=isin, security_type=security_type)

        self.ticker = ticker
        self.isin = isin
        self.security_type = security_type if security_type else "stock"

        # Tickers have a name. And in the case of macrotrends, the url
        # will NOT work properly - ie return quarterly data - if the
        # mnemonic is not in the url. It will just return annual even
        # if the url parm is quarterly. The solution is to add a mnemonic
        # that can be stapled into the url alongside the symbol. 
        #
        # But if nobody needs or wants to use the mnemonic, no harm no foul.
        
        # Add mnemonic private attribute with default None
        self._mnemonic = None

        # Noticed the issue of repeated http calls when attributes are 
        # referenced on the object more than once. The fix is to cache
        # statements if you can and check the cache before making the 
        # call to the url.
        # Initialize cache attributes explicitly
        # (in case super().__init__ doesn't properly initialize them)
        if not hasattr(self, '_income_stmt_cache'):
            self._income_stmt_cache = {}
        if not hasattr(self, '_balance_sheet_cache'):
            self._balance_sheet_cache = {}
        if not hasattr(self, '_cashflow_stmt_cache'):
            self._cashflow_stmt_cache = {}

    @property
    def mnemonic(self) -> str:
        """Get or set the Macrotrends mnemonic string for this ticker."""
        return self._mnemonic

    @mnemonic.setter
    def mnemonic(self, value: str) -> None:
        self._mnemonic = value

