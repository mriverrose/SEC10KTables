# Overview
The aim of this project is to create a script that can take a company's CIK number and produce a series of `.csv` files that correspond to a statement-type table from a company's 10-K (usually 5-10 of this type exist per 10-K), where the 10-Ks are from as many years as possible. Company 10-Ks that are no more than five or six years old include XML summaries that allow us to find all the tables in a 10-K (usually around 100) which we can then scrape and format using a corresponding link. 

The primary components of the code are broken out into three files: 
1. `json_links.py` to create the `index.json` links that we will try to find a `FilingSummary.xml` link for.
2. `statement_urls.py` to create a list of links to each statement-type table of a 10-K.
3. `statement_functions.py` to first make a list of dictionaries that capture the data from a table and to second make a dataframe from each dictionary (which can then be written as a `.csv` file).

We also make use of `edgar_functions.py` to do little, helpful tasks.

We bring together the primary components of the code in the `main.py` file: We set the CIK (just after our imports) we want to make tables for and execute the script from a Python interpreter. By the nature of 10-Ks, there is a chance something will format incorrectly while creating one of the tables. If the error keeps the code from writing the intended `.csv` files, hopefully it is clear enough how tweaks can be made to the code to fix the issue. 

The strategy and much of the code that parses 10-K data comes from [Alex Reed](https://github.com/areed1192), specifically his notebook [Web Scraping SEC - 10K Landing Page](https://github.com/areed1192/sigma_coding_youtube/blob/master/python/python-finance/sec-web-scraping/Web%20Scraping%20SEC%20-%2010K%20Landing%20Page%20-%20Single.ipynb). Read Mr. Reed's notebook to learn more about the process of transforming a 10-K table into a dataframe. 

If you would like a more in-depth demonstration of how this code works and to see the process of how we can go from the code Mr. Reed wrote to building classes and functions around it, go through the `JupyterNotebookWalkthrough`.
