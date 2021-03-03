from datetime import datetime
import re

def check_json_links(jsonLinks, flag=0):
    """Check if url gives any 10-K urls.  If url gives urls we can use,
    the flag will be returned with a value of 1 which we can then use
    to initiate further code.
    """
    if len(jsonLinks) > 0:
        flag = 1
        text = 'There were {} links found for the given CIK.'.format( len(jsonLinks) )
        print(text)
        print('Flag set to', flag)
        return flag
    else:
        print('No links were found for the given CIK.')
        print('Flag stays', flag)
        return flag


def get_10k_year_from_url(url):
    """From a link like this,
    <https://www.sec.gov/Archives/edgar/data/2488/000162828021001185/index.json>
    the function flips the url around (for consistency between links) 
    and takes off the first 17 characters <001185/index.json>.  Then it
    flips the url back around and takes the last two characters <21>.  
    Finally, it adds '20' to the <21> in order to return '2021', as 
    desired.
    """
    url = url[::-1] # Reverse the url.
    # Remove everything up to the two digits of the year
    url = url.replace(url[0:17], '') 
    url = url[::-1] # Reverse the url back.
    twoDigitYear = url[-2:]
    cikYear = '20' + twoDigitYear
    return cikYear


def get_10k_table_number(tableUrl):
    """Function to extract the table number from a table url. For example,
    'https://www.sec.gov/Archives/edgar/data/2488/000162828021001185/R2.htm'
    is a table url. The function will reverse the url, remove the first four
    characters. reverse the url back, then extract the last two characters
    (R2), which is the table number. We can then use this table number as part
    of a unique table name for the sql table.
    """
    tableUrl = tableUrl[::-1] # Reverse the url.
    tableUrl = tableUrl.replace(tableUrl[0:4], '') 
    tableUrl = tableUrl[::-1] # Reverse the url back.
    tableNumber = tableUrl[-2:]
    # Check if table is actually two digits.
    if re.match('\d{2}', tableNumber):
        tableNumber = tableUrl[-3:]
    else:
        pass
    # Check if table is actually three digits.
    if re.match('\d{3}', tableNumber):
        tableNumber = tableUrl[-4:]
    else:
        pass
    return tableNumber


def make_timestamp():
    """Create a timestamp to insert into each dataframe."""
    now = datetime.now()
    dtString = now.strftime("%Y-%m-%d %H:%M:%S")
    return dtString