from bs4 import BeautifulSoup,Comment
from url import Url
from urllib import FancyURLopener
import nltk
class MyOpener(FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'

class Webpage:
    '''
    def __init__(self):
        self.pageUrl = ""
        self.html = ""
        self.title = ""
        self.text = ""
        self.outgoingUrls=[]
    '''
    def __init__(self,url,page_id):
        self.Id = page_id
        self.pageUrl = url
        myopener = MyOpener()
        page = myopener.open(url.address)
        soup = BeautifulSoup(page)
        '''scripts = soup.findAll('script')
        for s in scripts:
            s.extract()'''
        self.outgoingUrls=[]
        links = soup.find_all('a')
        for link in links:
            u = Url(link.get('href'),link.string,"",self.Id,0.0)
            self.outgoingUrls.append(u)
        self.title = ""
        if soup.title:
            self.title = soup.title.string
        #self.html = str(soup)
        #self.text = nltk.clean_html(str(soup))
        comments = soup.findAll(text=lambda text:isinstance(text,Comment))
        [comment.extract() for comment in comments]
        text_nodes = soup.findAll(text=True)
        visible_text = filter(visible, text_nodes)
        self.text = ''.join(visible_text)

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head']:
        return False
    return True