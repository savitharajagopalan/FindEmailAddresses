import requests
import sys
import re

from urllib.request import urlopen

from bs4 import BeautifulSoup


def print_usage():
    print('\n------------------------------------------------------')
    print('Program usages:\n')
    print('           python find_email_addresses.py [site_name] \n')
    print('[site_name] : specify site such as  jana.com')


def get_url(page):
    """
        :param page: html of web page (here: Python home page)
        :return: urls in that page
    """
    start_link = page.find("a href")
    if start_link == -1:
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1: end_quote]
    return url, end_quote


def check_if_valid_url(site_name, prefix_to_site_name):
    valid_site_name = site_name
    valid_url = False
    # Check if the url is valid
    try:
        if site_name.startswith('http://') or site_name.startswith('https://'):
            requests.get(site_name)  # Get the page
            valid_url = True
            # print("Valid url: " + site_name)
        elif site_name.startswith('//'):
            temp_site_name = site_name
            site_name = 'https:' + temp_site_name
            valid_site_name, valid_url = check_if_valid_url(site_name,'')
        elif site_name.startswith('/'):
            temp_site_name = site_name
            site_name = prefix_to_site_name + temp_site_name
            valid_site_name, valid_url = check_if_valid_url(site_name,'')
        else:
            temp_site_name = 'https://'+site_name
            valid_site_name, valid_url = check_if_valid_url(temp_site_name,'')

    except requests.exceptions.MissingSchema as exMissing:
        if site_name.startswith('http://'):
            temp_site_name = site_name
            site_name = temp_site_name.replace('http://', 'https://')
            requests.get(site_name)
            valid_url = True
            valid_site_name = site_name
        elif site_name.startswith('https://'):
            temp_site_name = site_name
            site_name = temp_site_name.replace('https://', 'http://')
            requests.get(site_name)
            valid_url = True
            valid_site_name = site_name


    except Exception as ex1:
        print("Cannot extract information from the url ")
    return valid_site_name, valid_url


def get_emails(doc):
    # print("\n Looking for email addresses in "+ doc)
    return re.findall('[\w.]+@[\w.]+', doc)

class AppUrl(object):

    def check_for_url_validity(self):
        a, self.valid_url = check_if_valid_url(self.site_name,'')
        self.site_name = a

    def work_with_url(self):
        countOfExceptions = 0
        # print("Working with "+self.site_name)
        urlList = []
        uniqueEmailList = []
        urlList.append(self.site_name)
        if self.valid_url:
            associated_email_suffix = self.site_name[self.site_name.index(".")+1:]
            try:
                countOfUrl = 0
                htmlResponse = requests.get(self.site_name)
                # parse html
                page = str(BeautifulSoup(htmlResponse.content,"html.parser"))
                n = len(page)

                while n != 0 :
                    url, n = get_url(page)
                    page = page[n:]
                    if url != None:
                        if url in urlList:
                            countOfUrl += 1
                        else:
                            # print("Checking for validity of "+url)
                            validUrl, validURLdetected = check_if_valid_url(url,self.site_name)
                            if validURLdetected :
                                # print("Valid url " + validUrl)
                                urlList.append(validUrl)
                    else:
                        n = 0

                # print(" Found  ",len(urlList)," unique urls")
                # The application will search all the urls

                for urlSingle in urlList:
                    # print("decoding "+urlSingle)
                    try:
                        content = urlopen(urlSingle).read().decode()
                        if len(content) > 1:
                            allEmails = get_emails(content)
                            for oneEmail in allEmails:
                                if oneEmail.lower().endswith(associated_email_suffix.lower())and oneEmail.lower() not in uniqueEmailList:
                                    uniqueEmailList.append(oneEmail.lower())
                    except Exception as e1:
                        countOfExceptions+=1
                        continue

            except Exception as ex1:
                print("Cannot extract information from the url ")
                # print("Exception: " + ex1.args)


            # print("#. of urls found in page = ", len(urlList))
            print("Found these email addresses:")
            for uEmail in uniqueEmailList:
                print(uEmail)

    def parse_commandline(self):
        argc = len(sys.argv)
        if not (2 == argc):
            print_usage()
            sys.exit()

        self.script_name = sys.argv[0]
        self.site_name = sys.argv[1]

    def init_self(self):
        self.script_name = ''
        self.site_name = ''
        self.valid_url = False

    def main(self):
        self.init_self()
        self.parse_commandline()
        self.check_for_url_validity()
        self.work_with_url()


if __name__ == '__main__':
    thisApp = AppUrl()
    thisApp.main()
