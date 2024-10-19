import platform
from typing import Union

import pandas as pd
import plotly.express as px

from stockdex.exceptions import WrongSecurityType


def get_user_agent():
    os_name = platform.system().lower()
    if "linux" in os_name:
        return "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"  # noqa E501
    elif "darwin" in os_name:
        return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15"  # noqa E501
    elif "windows" in os_name:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"  # noqa E501
    else:
        # Fallback User-Agent
        return """Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"""  # noqa E501


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
        default: "plotly"
    """
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

    fig.show()
