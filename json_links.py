from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
import time


class JsonLinks:
    """JsonLinks class takes a CIK and form-type (defaults to 10-K)
    and returns a list of links that can (possibly) be used to extract 
    10-K tables and write them as CSVs or push them to a database.
    """
    def __init__(self, cik, formType='10-K'):
        self.cik = cik
        self.fullCik = self._add_zeros_to_cik()
        self.formType = formType
        

    def _add_zeros_to_cik(self):
        """Class method to ensure CIK 10 is characters.  Not strictly
        necessary but will ensure chosen CIK is valid and of a 
        consistent length.
        """
        L = len(self.cik)
        if L == 1:
            self.cik = '000000000' + self.cik
            return self.cik
        elif L == 2:
            self.cik = '00000000' + self.cik
            return self.cik
        elif L == 3:
            self.cik = '0000000' + self.cik
            return self.cik
        elif L == 4:
            self.cik = '000000' + self.cik
            return self.cik
        elif L == 5:
            self.cik = '00000' + self.cik
            return self.cik
        elif L == 6:
            self.cik = '0000' + self.cik
            return self.cik
        elif L == 7:
            self.cik = '000' + self.cik
            return self.cik
        elif L == 8:
            self.cik = '00' + self.cik
            return self.cik
        elif L == 9:
            self.cik = '0' + self.cik
            return self.cik
        elif L == 10:
            self.cik = self.cik
            return self.cik
        else:
            print('\n***Error encountered: invalid CIK.***\n')
    
    
    def build_cik_search_url(self):
        """Create the url we need to use to check if a CIK has any 10-K
        reports listed.  From these 10-Ks, we will eventually figure 
        out if any of them have .xml summaries.
        """
        url0 = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK='
        url1 = '&type=' 
        url2 = '&dateb=&owner=include&count=100&search_text='
        url = url0 + self.fullCik + url1 + self.formType + url2
        return url
    

    def get_soup(self):
        """Get the BeautifulSoup of the url we built in the
        build_cik_search_url().
        """
        urlClient = urlopen(self.build_cik_search_url())
        time.sleep(0.2)
        webPage = urlClient.read()
        urlClient.close()
        soupData = BeautifulSoup(webPage, 'html.parser')
        return soupData
    

    def get_10k_a_tags(self):
        """Find all <a> tags within the 10-K BeautifulSoup that have an
        id of 'documentsbutton'.
        """
        aTags = self.get_soup().find_all('a', id='documentsbutton')
        return aTags
    

    def get_10k_link_endings(self):
        """Create a list of all the links within the <a> tags found in 
        get_10k_a_tags().
        """
        linkEndings = []
        for aTag in self.get_10k_a_tags():
            linkEndings.append(aTag.get('href'))
        return linkEndings
    

    def add_base_url(self):
        """Patch together the SEC-portion of the link and the link 
        endings from get_10k_link_endings().
        """
        links = []
        baseUrl = r'https://www.sec.gov'
        for link in self.get_10k_link_endings():
            link = baseUrl + link
            links.append(link)
        return links
    

### Separate .htm and .html files.
    def _get_htm_links(self):
        """Class-method to make a list of all .htm links."""
        htmLinks = []
        for link in self.add_base_url():
            if link.endswith('.htm'):
                htmLinks.append(link)
            else:
                pass
        return htmLinks

    def _get_html_links(self):
        """Class-method to make a list of all .html links."""
        htmlLinks = []
        for link in self.add_base_url():
            if link.endswith('.html'):
                htmlLinks.append(link)
            else:
                pass
        return htmlLinks
### End separate.    


### Turn .htm and .html links into .json links.
    def get_json_htm_links(self):
        """All the .htm 10-K links are turned into links ending with 
        .json instead.  This involves removing the CIK, the date, and
        the incremental number of the document for that year, along 
        with removing 'index.htm'.  We parse through the .json to look 
        for .xml summaries.  The .xml summaries are what provide us 
        with all the links to a 10-K's tables.
        """
        jsonLinks = []
        for link in self._get_htm_links():
            # Reverse the link to access part we delete, in consistent manner.
            link = link[::-1]
            # Remove CIK, date, and document filing number. 
            link = link.replace(link[9:30], '')
            # Flip link back to way it was, this time without -numbers-
            link = link[::-1] 
            # Replace the index.htm ending with the index.json ending.
            # Note including 'index' is superfluous but easier to read.
            link = link.replace('index.htm', 'index.json')
            # Add the formatted link to our list of json links.
            jsonLinks.append(link)
        return jsonLinks
    
    def get_json_html_links(self):
        """The .html 10-K links all seem to be from 20+ years ago and
        have not yet provided any .xml summaries with them.  This 
        function is not used anywhere within this project and will
        probably be removed.
        The function does the same thing as get_json_htm_links().
        """
        jsonLinks = []
        for link in self._get_html_links():
            # Reverse the link to access part we delete in uniform manner.
            link = link[::-1] 
            # Remove the -index.html
            link = link.replace(link[0:11], '') 
            link = link.replace('-', '')
            # Flip link back to way it was, this time without -numbers-
            link = link[::-1] 
            link = link + '/index.json'
            jsonLinks.append(link)
        return jsonLinks
### End .json links.

if __name__ == "__main__":
    JsonLinks()