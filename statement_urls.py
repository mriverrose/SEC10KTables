from bs4 import BeautifulSoup
import requests


class StatementUrls:
    """StatementUrls takes an <index.json> url (created with the 
    JsonLinks class) and produces a list of table urls (R[0-100].htm)
    that can then be used to extract the data from financial statements 
    on EDGAR.
    """
    def __init__(self,url):
        self.url = url
        self.baseUrl = 'https://www.sec.gov'

    
    def get_xml_link(self):
        """If an index.json link has a FilingSummary.xml, make it into
        a usable link, otherwise pass.
        """
        content = requests.get(self.url).json()
        for file in content['directory']['item']:
            if file['name'] == 'FilingSummary.xml':
                xmlSummary = (
                    self.baseUrl 
                    + content['directory']['name'] 
                    + '/' 
                    + file['name']
                )
            else:
                pass
        return xmlSummary
        

    def get_master_reports(self):
        """Make a list of dictionaries that include the name, category and 
        url of every table in the 10-K.
        """
        baseUrl = self.get_xml_link().replace('FilingSummary.xml', '')

        content = requests.get(self.get_xml_link()).content
        soupData = BeautifulSoup(content, 'lxml')
        reports = soupData.find('myreports') # Xml tag enclosing all table reports.
        
        masterReports = [] # Create list to hold dictionaries of report tables.

        # Avoid last one (causes error)
        for report in reports.find_all('report')[:-1]: 
            # Create dictionary to store the parts we need
            reportDictionary = {}
            reportDictionary['nameShort'] = report.shortname.text
            reportDictionary['nameLong'] = report.longname.text
            reportDictionary['position'] = report.position.text
            reportDictionary['category'] = report.menucategory.text
            reportDictionary['url'] = baseUrl + report.htmlfilename.text    
            # Append the dictionary to the master list
            masterReports.append(reportDictionary)           
        return masterReports
    
    
    def get_statement_reports(self):
        """Pull out all dictionaries that have
            'category': 'Statements'

        Note that there are usually 50-100 items in these reports, with
        the vast majority containing superfluous information.  Thus, we
        are only pulling 'statements' from the reports in the current
        configuration.
        """
        statementsDictionary = []
        for reportDictionary in self.get_master_reports():
            if reportDictionary['category'].lower().find('statements') != -1:
                #print('-'*100)
                #print(reportDictionary['nameShort'])
                #print(reportDictionary['url'])
                statementsDictionary.append(reportDictionary)           
            else:
                pass
        return statementsDictionary
    
    
    def get_statement_urls(self):
        statementUrls = []
        for statement in self.get_statement_reports():
            statementUrls.append(statement['url'])
        return statementUrls

if __name__ == "__main__":
    StatementUrls()