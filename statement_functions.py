from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests


# Display entire pandas dataframe in the interpreter window:
#pd.set_option('display.max_colwidth', -1) 


def create_statement_data(statementUrl):
    """Once we have valid table_urls from our StatementUrls function, 
    we pass those urls into this function to yield a list of 
    dictionaries that separate the table's contents by headers, 
    sections, and data.

    `statementUrl`: LIST
    A list of urls that link to statement-type tables in a 10-K.
    """
    # Assume we want all statements in a single data list.
    statementsData = []

    # Loop through each statementUrl
    for statement in statementUrl:
    
        # Define dictionary that will store the different parts of the statement.
        statementData = {}
        statementData['headers'] = []
        statementData['sections'] = []
        statementData['data'] = []
    
        # Request the statement file content
        content = requests.get(statement).content
        reportSoup = BeautifulSoup(content, 'lxml')
    
        """Find all the rows, figure out what type of row, parse elements
        and store in the statement file list.
        """
        for index, row in enumerate(reportSoup.table.find_all('tr')):
        
            # Get all the elements
            columns = row.find_all('td')
        
            # If regular row and not a section or a table header.
            if (len(row.find_all('th')) == 0 and len(row.find_all('strong')) == 0):
                regularRow = [ele.text.strip() for ele in columns]
                statementData['data'].append(regularRow)
            
            # If regular row and section but not a table header.
            elif (len(row.find_all('th')) == 0 and len(row.find_all('strong')) != 0):
                sectionRow = columns[0].text.strip()
                statementData['sections'].append(sectionRow)
            
            # If not either of those, it must be header.
            elif (len(row.find_all('th')) != 0):
                headRow = [ele.text.strip() for ele in row.find_all('th')]
                statementData['headers'].append(headRow)
            
            else:
                print('Error encountered parsing table elements.')
            
        # Append it to the master list, statementsData.
        statementsData.append(statementData)
    
    return statementsData


def create_statement_dataframe(statementsData, statementNumber=0):
    """Once we have a list of dictionaries representing all the 10-K 
    statement-type tables (built by create_statement_data()), we pass
    the list to this function.  This function attempts to transform a
    given dictionary into a dataframe that can then be easily 
    manipulated. 
    
    `statementsData`: LIST (of dictionaries).
    The output of create_statement_data(), a list
    of dictionaries for the statement-type tables in a 10-K.

    `statementNumber`: INT
    Number of the dictionary from the list that
    holds the statement-type table urls.
    """
    
    # Grab the proper components
    statementHeader = statementsData[statementNumber]['headers']
    data = statementsData[statementNumber]['data']

    
    ### Logic to make sure correct headers are being used. ###
    print('Tabel Title:', statementsData[statementNumber]['headers'][0][0])
    print('Length of header list:', len(statementHeader) )
    # Get title of the dataframe index
    title = statementsData[statementNumber]['headers'][0][0]
    
    if len(statementHeader) == 2:
        statementHeader = statementsData[statementNumber]['headers'][1]
        print('Column headers that will be used:')
        print(statementHeader)
        widthStatementHeader = len(statementHeader)
        print('Number of statement headers:', widthStatementHeader)
    elif len(statementHeader) == 1:
        statementHeader = statementsData[statementNumber]['headers'][0][1:]
        print('Column headers that will be used:')
        print(statementHeader)
        widthStatementHeader = len(statementHeader)
        print('Number of statement headers:', widthStatementHeader)
    else:
        print('Length of statementHeader is:', len(statementHeader))
        print('Need more case logic for this length mismatch.')
        pass
    ### End logic. ###
    
    
    ### Logic removing rows that are a different length than the first one. ###
    dfWidth = len(data[0])
    print('Number of dataframe columns:', dfWidth)
    numRows = len(data[:])
    newData = []
    for i in range(numRows):
        if dfWidth == len(data[i]):
            #print('Keeping this row:', data[i])
            newData.append(data[i])
        else: 
            #print('Removing this row:', data[i])
            pass
    print('Number of rows that were in dataframe:', numRows)
    print('Number of rows in dataframe now:', len(newData[:]))
    df = pd.DataFrame(newData)
    ### End logic.

    # Define the index column, rename it, and make sure to drop the old
    #  column once we reindex.
    df.index = df[0]
    df.index.name = title
    df = df.drop(0, axis=1)

    # Get rid of the '$', '(', ')', '%', and convert the '' to np.NaNs.
    df = df.replace('\[[0-9]\]','', regex=True)\
           .replace('[\$,)]','', regex=True )\
           .replace( '', np.NaN, regex=True)\
           .replace( '[(]','-', regex=True)\
           .replace('\%','', regex=True)

    ### Logic to remove column(s) of all NaN values. ###
    # If the number of headers + 1 is equal to the number of columns in 
    #  the dataframe, that's what we want:
    if dfWidth == (widthStatementHeader + 1):
        pass
    elif dfWidth >= (widthStatementHeader + 2):
        # Look for columns with all NaN values to delete, since that's 
        #  most likely the problem.
        print('Removing NaN column(s)')
        df = df.dropna(axis=1, how='all')
    else:
        print('Number of dataframe columns:', dfWidth)
        print('Number of headers:', widthStatementHeader)
        print('Error encountered with number of headers and number of columns.')
        print('Please add more logic to create_statement_dataframe().')
        pass
    ### Logic end.

    # Everything is a string, let's convert all the data to a float.
    # Specifying error='ignore' will churn out the table with headers still intact.
    # errors='raise' (default) will cause a table failure if data not a float.
    df = df.astype(float, errors='ignore') 
    df.columns = statementHeader
    return df  