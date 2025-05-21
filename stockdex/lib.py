from typing import List, Union

import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html

from stockdex.exceptions import WrongSecurityType


def get_user_agent():
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"  # noqa E501


def check_security_type(security_type: str, valid_types: Union[str, list]) -> None:
    """
    Check if the security type is valid
    """
    if isinstance(valid_types, str):
        valid_types = [valid_types]

    if security_type not in valid_types:
        raise WrongSecurityType(valid_types=valid_types, given_type=security_type)


def plot_dataframe(
    dataframe: pd.DataFrame,
    title: str,
    barmode: str = "group",
    logaritmic: bool = False,
    template: str = "plotly",
    y_axis_title: str = "Amount",
    x_axis_title: str = "Date",
    draw_line_chart: bool = False,
    show_plot: bool = True,
) -> None:
    """
    Plot a DataFrame using Plotly Express

    Parameters
    ----------
    dataframe : pd.DataFrame
        The DataFrame to plot

    title : str
        The title of the plot

    barmode : str
        The barmode of the plot
        default: "group"

    logaritmic : bool
        If the y-axis should be logaritmic
        default: False

    template : str
        The template of the plot.
        One of plotly, plotly_white, plotly_dark, ggplot2, seaborn, simple_white, none
        default: "plotly"#

    y_axis_title : str
        The title of the y-axis
        default: "Amount"

    x_axis_title : str
        The title of the x-axis
        default: "Date"

    draw_line_chart : bool
        If the plot should be a line chart and not bar. For charts that have too many data points,
        it is recommended to use line charts instead of bar charts as it is easier to read.
        default: False (bar chart)

    show_plot : bool
        If the plot should be shown. Setting this to False will only return the plot object.
        Can be used to save the plot to a file or construct complex dashboards with multiple plots.
        default: True
    """
    if draw_line_chart:
        fig = px.line(
            dataframe,
            title=title,
            template=template,
        )
    else:
        fig = px.bar(
            dataframe, title=title, barmode=barmode, log_y=logaritmic, template=template
        )

    fig.update_layout(
        yaxis_title=y_axis_title,
        xaxis_title=x_axis_title,
        legend_title_text="",
    )

    # make marker line width wider
    fig.update_traces(marker_line_width=1.5)
    fig.update_traces(hovertemplate="<b>%{y}</b>")

    # make bar width wider
    fig.update_traces(marker_line_width=1.5)

    if show_plot:
        fig.show()

    return fig


def plot_multiple_categories(
    ticker: str,
    figures: List[Union[px.bar, px.line]],
    app_port: int = 8050,
) -> None:
    """
    Plot multiple categories in a single Dash app.

    Parameters
    ----------
    figures : List[Union[px.bar, px.line]]
        A list of Plotly Express bar or line objects

    app_port : int
        The port to run the Dash app on
        default: 8050
    """

    # Initialize the Dash app
    app = dash.Dash(__name__)

    # Create a list of Graph components, one for each figure in the list
    graphs = []
    for i, fig in enumerate(figures):
        graphs.append(
            html.Div(
                dcc.Graph(id=f"figure-{i}", figure=fig),
                style={"width": "48%", "display": "inline-block", "padding": "10px"},
            )
        )

    # Define the layout of the app
    app.layout = html.Div(
        children=[
            html.H1(
                children=f"Multiple Category Dashboard for {ticker}",
                style={"text-align": "center"},
            ),
            # Create a container for the list of figures
            html.Div(children=graphs),
        ]
    )

    # Start Dash app in a separate threa
    print(f"Starting Dash app on port {app_port}")
    app.run_server(debug=True, use_reloader=False, port=app_port)
