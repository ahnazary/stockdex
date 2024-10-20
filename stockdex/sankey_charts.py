"""
Module to draw sankey charts
"""

from typing import Literal

import pandas as pd
import plotly.graph_objects as go

from stockdex.ticker_base import TickerBase


class SankeyCharts(TickerBase):
    def __init__(self, ticker: str) -> None:
        self.ticker = ticker

    def _build_main_df(self, ticker: str, frequency: str = "annual") -> pd.DataFrame:
        self.ticker = ticker
        yahoo_cash_flow = self.yahoo_api_cash_flow(format="raw", frequency=frequency)
        yahoo_balance_sheet = self.yahoo_api_balance_sheet(
            format="raw", frequency=frequency
        )
        yahoo_income_statement = self.yahoo_api_income_statement(
            format="raw", frequency=frequency
        )
        yahoo_financials = self.yahoo_api_financials(format="raw", frequency=frequency)
        # concatenate all the dataframes
        self.data = pd.concat(
            [
                yahoo_cash_flow,
                yahoo_balance_sheet,
                yahoo_income_statement,
                yahoo_financials,
            ],
            axis=1,
        )
        return self.data

    def plot_sankey_chart(
        self, frequency: Literal["annual", "quarterly"] = "annual", period_ago: int = 0
    ) -> None:
        """
        Main function to plot the sankey chart

        Args:
        ----------
        frequency: str
            The frequency of the data to be used. It can be either "annual" or "quarterly".
            Default is "annual"

        period_ago: int
            The period to go back. Default is 0. if a non zero value, e.g. 3 is provided,
            the data for 3 periods ago will be used (annual or quarterly based on the frequency)

        Returns:
        ----------
        None
        """

        # Helper function to safely retrieve sum from columns or return 0 if the column is missing
        def get_value(df, column_name):
            value = (
                df[column_name].iloc[df.shape[0] - period_ago - 1]
                if column_name in df.columns
                else 0
            )

            if isinstance(value, pd.Series):
                value = value.iloc[0]

            return value

        df = self._build_main_df(self.ticker, frequency)

        nodes = [
            "Total Revenue",  # 0 (TotalRevenue)
            "Cost of Revenue",  # 1 (CostOfRevenue)
            "Gross Profit",  # 2 (GrossProfit)
            "Operating Expenses",  # 3 (OperatingExpense)
            "Operating Income",  # 4 (OperatingIncome)
            "Net Income",  # 5 (NetIncomeCommonStockholders)
            "Tax",  # 6 (TaxProvision)
            "Other",  # 7 (OtherIncomeExpense)
            "R&D",  # 8 (ResearchAndDevelopment)
            "SG&A",  # 9 (SellingGeneralAndAdministration)
        ]

        source, value, target = [], [], []

        # Total Revenue -> Cost of Revenue
        source.append(0)
        target.append(1)
        value.append(get_value(df, f"{frequency}CostOfRevenue"))

        # Total Revenue -> Gross Profit (derived after Cost of Revenue)
        gross_profit = get_value(df, f"{frequency}TotalRevenue") - get_value(
            df, f"{frequency}CostOfRevenue"
        )
        source.append(0)
        target.append(2)
        value.append(gross_profit)

        # Gross Profit -> Operating Expenses
        source.append(2)
        target.append(3)
        value.append(get_value(df, f"{frequency}OperatingExpense"))

        # Operating Expenses -> R&D
        source.append(3)
        target.append(8)
        value.append(get_value(df, f"{frequency}ResearchAndDevelopment"))

        # Operating Expenses -> SG&A
        source.append(3)
        target.append(9)
        value.append(get_value(df, f"{frequency}SellingGeneralAndAdministration"))

        # Gross Profit -> Operating Income
        source.append(2)
        target.append(4)
        value.append(get_value(df, f"{frequency}OperatingIncome"))

        # Operating Income -> Net Income
        source.append(4)
        target.append(5)
        value.append(get_value(df, f"{frequency}NetIncomeCommonStockholders"))

        # Operating Income -> Other Income/Expense
        source.append(4)
        target.append(7)
        value.append(get_value(df, f"{frequency}OtherIncomeExpense"))

        # Operating Income -> Tax Provision
        source.append(4)
        target.append(6)
        value.append(get_value(df, f"{frequency}TaxProvision"))

        # if element is value is of type series, get iloc 0
        value = [v if not isinstance(v, pd.Series) else v.iloc[0] for v in value]

        # convert to float
        value = [float(v) for v in value]
        value_human = pd.Series(value).apply(self._human_format)

        node_values = [
            self._human_format(get_value(df, f"{frequency}TotalRevenue")),
            self._human_format(get_value(df, f"{frequency}CostOfRevenue")),
            self._human_format(gross_profit),
            self._human_format(get_value(df, f"{frequency}OperatingExpense")),
            self._human_format(get_value(df, f"{frequency}OperatingIncome")),
            self._human_format(
                get_value(df, f"{frequency}NetIncomeCommonStockholders")
            ),
            self._human_format(get_value(df, f"{frequency}TaxProvision")),
            self._human_format(get_value(df, f"{frequency}OtherIncomeExpense")),
            self._human_format(get_value(df, f"{frequency}ResearchAndDevelopment")),
            self._human_format(
                get_value(df, f"{frequency}SellingGeneralAndAdministration")
            ),
        ]

        fig = go.Figure(
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=nodes,
                    # add total revenue as  the first element to value_human
                    customdata=node_values,
                    hovertemplate="%{customdata}",
                    x=[None, 0.35, None, None, None, 0.7, 0.7, None, None, None],
                    y=[None, 0.35, None, None, None, None, None, None, None, None],
                ),
                link=dict(
                    arrowlen=40,
                    source=source,
                    target=target,
                    value=value,
                    customdata=value_human,
                    hovertemplate="%{customdata}",
                ),
            )
        )

        fig.update_layout(
            title_text=f"{self.ticker} Income Statement ({frequency} data) reported at: {df.index[df.shape[0] - period_ago - 1]}",  # noqa E501
            font_size=10,
        )
        fig.show()

    def _human_format(self, num) -> str:
        """
        Helper function to convert a number to human readable format

        Args:
        ----------
        num: float
            The number to be converted

        Returns:
        ----------
        str: The human readable format of the number
        """
        num = float("{:.3g}".format(num))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return "{}{}".format(
            "{:f}".format(num).rstrip("0").rstrip("."),
            ["", " Thousand", " Million", " Billion", " Trillion"][magnitude],
        )
