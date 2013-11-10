import urllib2
from bs4 import BeautifulSoup
from webpage import Webpage

class Crawler:
    def __init__(self,priorityQueue,scorer,pagesLimit):
        self.visited = []        
        #self.relevantPages=[]
        #self.relevantPagesCount = len(priorityQueue.queue)
        self.relevantPagesCount = 0
        self.totalPagesCount = len(priorityQueue.queue)
        self.pagesCount = 0
        self.priorityQueue = priorityQueue
        self.scorer = scorer
        self.pagesLimit = pagesLimit
    
    def crawl(self):
        #start crawling
        #myopener = MyOpener()
        self.harvestRatioData = []
        self.relevantPages = []
        self.traceLog = []
        while self.pagesCount <  self.pagesLimit and not self.priorityQueue.isempty():
            work_url = self.priorityQueue.pop()
            self.visited.append(work_url[1].address)
            #print ("%s, %s") % (-1 * work_url[0], work_url[1])
            #page = urllib2.urlopen(work_url)
            '''page = myopener.open(work_url)
            self.pagesCount += 1
            soup = BeautifulSoup(page)
            links = soup.find_all('a')'''
            page = Webpage(work_url[1],self.pagesCount)
            page_score = self.scorer.calculate_score(page.text)
            
            self.pagesCount += 1
            if (page_score > 0.5):
                self.relevantPagesCount += 1
                self.relevantPages.append(page)
                '''
                if page.pageUrl.parentId != -1:
                    self.traceLog[page.pageUrl.parentId] = page
                else:
                    self.traceLog.append(page.Id)
                '''
                self.harvestRatioData.append((self.relevantPagesCount,self.pagesCount))
                print ("%s, %s") % (-1 * work_url[0], work_url[1].address)
                for link in page.outgoingUrls:
                    url = link.address
                    if url != None and url != '':
                        #if url.find('?')!= -1:
                        #    url = url.split('?')[0]
                        if url not in self.visited:
                        #if not self.exists(url,self.visited):
                            if url.startswith('http:') and url.find('#') == -1 and not self.exists(url,self.priorityQueue.queue):                            
                                url_score = self.scorer.calculate_score(link.getAllText())
                                self.totalPagesCount +=1
                                tot_score = url_score
                                #self.priorityQueue.push(((-1 * tot_score),url))
                                self.priorityQueue.push(((-1 * tot_score),link))
                                #if tot_score > 0.2:
                                    #self.priorityQueue.push(((-1 * tot_score),url))
                
    def exists(self,url,alist):
        urlList = [v.address for _,v in alist]
        return url in urlList
