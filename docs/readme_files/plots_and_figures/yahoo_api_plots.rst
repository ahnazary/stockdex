Yahoo API Plots
===============


Income statement chart
------------------------

    def plot_yahoo_api_income_statement(
        self,
        frequency: Literal["annual", "quarterly"] = "annual",
        period1: datetime = five_years_ago,
        period2: datetime = today,
        group_by: Literal["timeframe", "field"] = "timeframe",
        fields_to_include: list = [
            "TotalRevenue",
            "EBITDA",
            "TotalExpenses",
            "NetIncomeCommonStockholders",
            "NetIncome",
        ],
        show_plot: bool = True,
    ) -> Union[px.line, px.bar]:
        """
        Plots the income statement for the stock using matplotlib grouped bar chart

        Parameters
        ----------------
        frequency: str
            The frequency of the data to retrieve
            valid values are "annual", "quarterly"

        period1: datetime
            The start date of the data to retrieve

        period2: datetime
            The end date of the data to retrieve

        group_by: str
            The group by parameter

        fields_to_include: list
            The fields to include in the chart in the x-axis

        show_plot : bool
            If the plot should be shown or not.
            If dash is used, this should be set to False
            Default is True (show the plot)

        Returns:
        ----------------
        Union[px.line, px.bar]: The plotly figure
        """


.. code-block: python
    from stockdex.ticker import Ticker

    ticker = Ticker(ticker="AAPL")
    result = ticker.plot_yahoo_api_income_statement()