import urllib2
from bs4 import BeautifulSoup
from webpage import Webpage

class Crawler:
    def __init__(self,priorityQueue,scorer,pagesLimit):
        self.visited = []        
        #self.relevantPages=[]
        self.relevantPagesCount = len(priorityQueue.queue)
        self.totalPagesCount = len(priorityQueue.queue)
        self.pagesCount = 0
        self.priorityQueue = priorityQueue
        self.scorer = scorer
        self.pagesLimit = pagesLimit
    
    def crawl(self):
        #start crawling
        #myopener = MyOpener()
        while self.pagesCount <  self.pagesLimit and not self.priorityQueue.isempty():
            work_url = self.priorityQueue.pop()
            self.visited.append(work_url)
            print ("%s, %s") % (-1 * work_url[0], work_url[1])
            #page = urllib2.urlopen(work_url)
            '''page = myopener.open(work_url)
            self.pagesCount += 1
            soup = BeautifulSoup(page)
            links = soup.find_all('a')'''
            page = Webpage(work_url[1])
            self.pagesCount += 1
            for link in page.outgoingUrls:
                url = link.address
                if url != None and url != '':
                    if url.find('?')!= -1:
                        url = url.split('?')[0]
                    if not self.exists(url,self.visited):
                        if url.startswith('http:') and url.find('#') == -1 and not self.exists(url,self.priorityQueue.queue):                            
                            url_score = self.scorer.calculate_score(link.getAllText())
                            self.totalPagesCount +=1
                            if url_score > 0.1:
                                self.priorityQueue.push(((-1 * url_score),url))
                                self.relevantPagesCount += 1
                
    def exists(self,url,alist):
        urlList = [v for p,v in alist]
        return url in urlList
