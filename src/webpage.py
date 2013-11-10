from bs4 import BeautifulSoup,Comment
from url import Url
from urllib import FancyURLopener
import urllib2
import nltk
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
        anchor= ""
        links = self.soup.find_all('a')
        for link in links:
            if link.string:
                anchor = link.string
            elif link.text:
                anchor = link.text
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
            if url[1].find("\n") != -1:
                pageUrl = url[1][:-1]
            req = urllib2.Request(url[1], None, headers)
            page = urllib2.urlopen(req).read()        
        except urllib2.HTTPError:
            self.text = ""
            return
        except urllib2.URLError,e:           
            self.text = ""
            return
        except ValueError:
            self.text = ""
            return
        
        self.soup = BeautifulSoup(page)
        '''scripts = soup.findAll('script')
        for s in scripts:
            s.extract()'''
        self.outgoingUrls=[]
        '''
        links = soup.find_all('a')
        for link in links:
            u = Url(link.string,link.get('href'),"")
            self.outgoingUrls.append(u)
        '''
        self.title = ""
        if self.soup.title:
            self.title = self.soup.title.string
        #self.html = str(soup)
        #self.text = nltk.clean_html(str(soup))
        comments = self.soup.findAll(text=lambda text:isinstance(text,Comment))
        [comment.extract() for comment in comments]
        text_nodes = self.soup.findAll(text=True)
        visible_text = filter(visible, text_nodes)
        self.text = ''.join(visible_text)

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head']:
        return False
    return True