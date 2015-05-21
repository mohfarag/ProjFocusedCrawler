
from webpage import Webpage
import sys,codecs

if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout, 'strict')

class Crawler:
    #def __init__(self,priorityQueue,scorer,options):
    def __init__(self,crawlParams):
        self.visited = []
        self.pagesCount = 0
        self.priorityQueue = crawlParams['priorityQueue']
        self.scorer = crawlParams['scorer']
        self.pageScoreThreshold = crawlParams['pageScoreThreshold']
        self.urlScoreThreshold = crawlParams['urlScoreThreshold']
        self.pagesLimit = crawlParams['num_pages']
        self.mode = crawlParams['mode']
        self.restricted = crawlParams['restricted']
        self.combineScore = crawlParams['combineScore']
        #self.pages = []
    
    def crawl(self):
        self.harvestRatioData = []
        self.relevantPages = []
        
        while self.pagesCount <  self.pagesLimit and not self.priorityQueue.isempty():
        
            work_url = self.priorityQueue.pop()
            self.visited.append(work_url)
            page = Webpage(work_url,self.pagesCount)
            if page.text =='' :
                continue
            page_score = 0.0
            if self.combineScore:
                if len(page.text) > 0:
                    page_score = self.scorer.calculate_score(page.text,'W')
                else:
                    continue
                page.estimatedScore = page_score
                if self.restricted:
                    if page_score < self.pageScoreThreshold:
                        continue
                
            #print -1 * work_url[0],",", str(page_score),",",work_url[1],",", work_url[3]
            print -1 * work_url[0],",",work_url[1],",", work_url[3]
            self.pagesCount += 1
            
            page.getUrls()
            self.relevantPages.append(page)
            for link in page.outgoingUrls:
                url = link.address
                if url != None and url != '':
                    url = url.strip()
                    if url.find('?')!= -1:                            
                        url = url.split('?')[0]
                    if url.find('#') != -1:
                        url = url.split('#')[0]
                    
                    if url.endswith(("comment","comment/","feed","comments","feed/","comments/",".rss","video","video/","link","gif","jpeg","mp4","wav","jpg","mp3","png","share.php","sharer.php","login.php","print","print/","button/","share","email","submit","post",".pdf") ):    
                        continue
                    if not self.exists(url,1):
                        #tot_score = 0.0
                        if url.startswith('http') and not self.exists(url,2):                            
                            if self.mode == 1:
                                url_score = self.scorer.calculate_score(link.getAllText(),'U')
                                if self.combineScore:
                                    tot_score= 0.5 *page_score + 0.5 *url_score
                                else:
                                    tot_score = url_score
                                #if tot_score >= self.urlScoreThreshold:
                                self.priorityQueue.push(((-1 * tot_score),url,page.pageId,link.getAllText()))
                            #else:
                            #    self.priorityQueue.push(((-1 * page_score),url,page.pageId,link.getAllText()))
            #else:
            #    self.pages.append((page,0))
                                    
        print self.priorityQueue.isempty()
        #print '\n'.join([str(-1*s[0]) +"," +s[1] for s in self.priorityQueue.queue])
                
    def exists(self,url,s):
        if s == 1:
            urlList = [v for p,v,k,l in self.visited]
        elif s == 2:
            urlList = [v for p,v,k,l in self.priorityQueue.queue]
        return url in urlList
