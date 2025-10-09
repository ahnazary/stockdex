Plots and figures
=================

Each data source has functions with the `plot_<data_srource>_<function_name>` pattern to plot the data extracted from that source in plotly figures.

.. tip::
   Each plot function has a field called `show_plot`. Default value is `True` which will show the plot when the function is called. If set to `False`, it will return the plotly figure object without showing the plot.

The following plotting functions are documented here:

.. toctree::
   :maxdepth: 1

   readme_files/plots_and_figures/macrotrends_plots
   readme_files/plots_and_figures/yahoo_api_plots
   readme_files/plots_and_figures/digrin_plots
   readme_files/plots_and_figures/sankey_charts
   readme_files/plots_and_figures/building_dash_apps
