import sys
from bs4 import BeautifulSoup,Comment
from url import Url
from urllib import FancyURLopener
import urllib2
import nltk
import requests
class MyOpener(FancyURLopener):
    #version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
    version = 'Mozilla/5.0'

class Webpage:
    '''
    def __init__(self):
        self.pageUrl = ""
        self.html = ""
        self.title = ""
        self.text = ""
        self.outgoingUrls=[]
    '''
    def getUrls(self):
        links = self.soup.find_all('a')
        for link in links:
            anchor =""
            if link.string:
                anchor = link.string
            elif link.text:
                anchor = link.text
            else:
                anchor = ""
            u = Url(anchor,link.get('href'),"")
            self.outgoingUrls.append(u)
    
    def __init__(self,url,pageId):
        self.pageUrl = url
        self.pageId = pageId
        #myopener = MyOpener()
        #page = myopener.open(url[1])
        
        try:
            #headers = { 'User-Agent' : 'Mozilla/5.0'}
            headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 5.1; rv:10.0.1) Gecko/20100101 Firefox/10.0.1'}
#             if url[1].find("\n") != -1:
#                 pageUrl = url[1][:-1]
            req = urllib2.Request(url[1], None, headers)
            page = urllib2.urlopen(req).read()        
        except urllib2.HTTPError:
            print sys.exc_info()[0]
            self.text = "Error"
            return
        except urllib2.URLError:
            print sys.exc_info()[0]           
            self.text = "Error"
            return
        except ValueError:
            print sys.exc_info()[0]
            self.text = "Error"
            return
        except :
            print sys.exc_info()[0]
            self.text = "Error"
            return
        self.soup = BeautifulSoup(page)
        self.outgoingUrls=[]
        self.title = ""
#         if self.soup.title:
#             if self.soup.title.string:
#                 self.title = self.soup.title.string
#             else:
#                 self.title = self.soup.title
        try:
#             if self.soup.html:
#                 if self.soup.html.head:
            if self.soup.html.head.title.string:
                self.title = self.soup.html.head.title.string
        except:
            self.title = ""
        comments = self.soup.findAll(text=lambda text:isinstance(text,Comment))
        [comment.extract() for comment in comments]
        text_nodes = self.soup.findAll(text=True)
        visible_text = filter(visible, text_nodes)
        self.text = ''.join(visible_text)
        self.text = self.title + " " + self.text

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head']:
        return False
    return True