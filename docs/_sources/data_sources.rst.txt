Data Sources
=============

You can use the following sources to extract financial data in the form of pandas dataframes.
Each data source has its own section with details on how to use with examples of the output dataframes.

.. note::
   Each function is prefixed with the source of the data. For example functions with `yahoo_api_<function_name>` get data from Yahoo Finance API and functions with `finviz_<function_name>` pattern get data from Finviz.

.. toctree::
   :maxdepth: 1

   readme_files/raw_dataframes/yahoo_api_doc
   readme_files/raw_dataframes/yahoo_web_doc
   readme_files/raw_dataframes/finviz_doc
   readme_files/raw_dataframes/digrin_doc
   readme_files/raw_dataframes/macrotrends_doc
   readme_files/raw_dataframes/jsutetf_doc