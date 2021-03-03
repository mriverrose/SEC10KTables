from json_links import JsonLinks
from edgar_functions import (
    check_json_links,
    make_timestamp,
    get_10k_year_from_url,
    get_10k_table_number, 
)
from statement_functions import (
    create_statement_data, 
    create_statement_dataframe,
)
from statement_urls import StatementUrls

"""To avoid this error:
<urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: 
unable to get local issuer certificate (_ssl.c:1056)>
use the following two lines of code.
"""
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


"""Change CIK below:"""
cik = '2488' # AMD CIK
#cik = '320193' # Apple
#cik = '50863' # Intel 
#cik = '0001652044' # Alphabet Inc. CIK
#cik = '0' # Junk CIK to test null results.
#cik = '20' # CIK to test no table results.
#cik = '12345678910' # Invalid CIK
#cik = 789019 # Microsoft CIK to test integer type.


cik = str(cik) # Make sure CIK is string type.
J = JsonLinks(cik)
cik = J.fullCik # Comment out to remove leading zeros.
jsonUrls = J.get_json_htm_links()

# If links are found, flag will be set to 1. 
flag = check_json_links(jsonUrls) 

jsonUrlData = [] # List of dictionaries containing json url and table urls.

### Flag logic to get the statement urls and print results. ###
if flag == 1:
    # Make dictionaries of json urls along with their table urls.
    for i in range( len(jsonUrls) ):
        url = jsonUrls[i]
        t = {} # Dictionary to hold the index.json url and all the table urls.

        try:
            try:
                # Create object, s, that has all the statement-type table urls.
                s = StatementUrls(url).get_statement_urls() 
                text = "*{0}* 'Statement' tables found for url: {1}.".format(len(s), url)
                print(text)
                t['json_url'] = url
                t['table_urls'] = s
                jsonUrlData.append(t)
                #print(s) # Print out list of table urls for each index.json
            except AttributeError:
                print('Encountered:  <AttributeError> url: ', url)
                pass
        except UnboundLocalError:
            print("Encountered:  <UnboundLocalError>  url: ", url)

else:
    print('No urls found.')
### End flag logic. ###

text  = "\nFor CIK={0}, we have {1} index.json links.\nOf these {1} index.json links, {2} have xml summaries with statement-type table urls associated with them that we are able to parse.\n".format(cik, len(jsonUrls), len(jsonUrlData))
print(text)
#print(jsonUrlData)
if len(jsonUrlData) == 0:
    print("Since there are 0 xml summaries with statement-type table urls, we have no tables to parse.")
else:
    pass

### Create the .csv files. ###
for j in range( len(jsonUrlData) ):

    if jsonUrlData != []:
        print("Non-empty jsonUrlData, making dataframes for all associated table links.")
        data = create_statement_data(jsonUrlData[j]['table_urls'][:]) 
        #print(data)

        for i in range( len(jsonUrlData[j]['table_urls'][:]) ):
            # Create a dataframe that matches a single 10-K statement table.
            df = create_statement_dataframe(data, i) 
            year10k = get_10k_year_from_url(jsonUrlData[j]['json_url'])
            jsonUrl = jsonUrlData[j]['json_url']
            tableUrl = jsonUrlData[j]['table_urls'][i]
            tableNumber = get_10k_table_number(tableUrl)
            tableTitle = cik + "_" + year10k + "_" + tableNumber
            print('Table written as:', tableTitle + '.csv\n')

            # Additional data we can add to the dataframe.
            df['cik'] = cik
            df['timestamp'] = make_timestamp()
            df['table_url'] = tableUrl
            df['json_url'] = jsonUrl
            
            # When characters in index display incorrectly, correct it here:
            df.index = df.index.map(lambda x: x.replace('—', '--')) 

            pathOut = './data/' 
            # Create .csv file and dump in local data folder.
            df.to_csv(pathOut + tableTitle + ".csv")
            

    else: 
        print('Empty jsonUrlData. Error occurred in create .csv files loop.')
        pass
### End create .csv files. ###