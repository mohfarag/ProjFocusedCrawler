
from webpage import Webpage
import sys,codecs

if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout, 'strict')

class Crawler:
    #def __init__(self,priorityQueue,scorer,options):
    def __init__(self,crawlParams):
        self.visited = []
        #self.relevantPages=[]
        #self.relevantPagesCount = len(priorityQueue.queue)
        self.relevantPagesCount = 0
        #self.totalPagesCount = len(priorityQueue.queue)
        self.pagesCount = 0
        self.priorityQueue = crawlParams['priorityQueue']
        self.scorer = crawlParams['scorer']
        self.pageScoreThreshold = crawlParams['pageScoreThreshold']
        self.urlScoreThreshold = crawlParams['urlScoreThreshold']
        self.pagesLimit = crawlParams['num_pages']
        self.mode = crawlParams['mode']
        self.pages = []
    
    def crawl(self):
        #start crawling
        #myopener = MyOpener()
        self.harvestRatioData = []
        self.relevantPages = []
        
        while self.pagesCount <  self.pagesLimit and not self.priorityQueue.isempty():
        #while self.relevantPagesCount <  self.pagesLimit and not self.priorityQueue.isempty():
            #print self.pagesCount
            work_url = self.priorityQueue.pop()
            self.visited.append(work_url)
            #print ("%s, %s") % (-1 * work_url[0], work_url[1])
            #page = urllib2.urlopen(work_url)
            
            #print len(self.priorityQueue.queue)
            page = Webpage(work_url,self.pagesCount)
            #print work_url[1]
            #print "length:", len(page.text)
            if page.text == "Error":
                continue
            if len(page.text) > 0:
                page_score = self.scorer.calculate_score(page.text)
            else:
                continue
                #page_score = 0
            #print "page Score", page_score
            #print "URL:", work_url[1]
            #print ("%s,"+ str(page_score)+", %s" +", %s") % (-1 * work_url[0], work_url[1], work_url[3])
            #self.pages.append(page)
            print -1 * work_url[0],",", str(page_score),",",work_url[1],",", work_url[3]
            self.pagesCount += 1
            #if (page_score >= self.pageScoreThreshold):
            page.getUrls()
            #self.relevantPagesCount += 1
            #self.pages.append((page,1))
            self.relevantPages.append(page)
            #self.harvestRatioData.append((self.relevantPagesCount,self.pagesCount))
            #print ("%s,"+ str(page_score)+", %s") % (-1 * work_url[0], work_url[1])
            for link in page.outgoingUrls:
                url = link.address
                if url != None and url != '':
                    if url.find('?')!= -1:                            
                        url = url.split('?')[0]
                    if url.find('#') != -1:
                        url = url.split('#')[0]
                    
                    if url.endswith(("comment",".rss","video","video/","link","gif","jpeg","mp4","wav","jpg","mp3","png","share.php","sharer.php","login.php","print","print/","button/","share","email","submit","post",".pdf") ):
                    #if url.endswith("share") or url.endswith("email") or url.endswith(("print","print/")) or url.endswith("submit")or url.endswith("post"):
                        url = ""
                    if not self.exists(url,self.visited):
                        if url.startswith('http') and not self.exists(url,self.priorityQueue.queue):                            
                            if self.mode == 1:
                                url_score = self.scorer.calculate_score(link.getAllText())
                                tot_score = url_score
                                if tot_score >= self.urlScoreThreshold:
                                    self.priorityQueue.push(((-1 * tot_score),url,page.pageId,link.getAllText()))
                            else:
                                self.priorityQueue.push(((-1 * page_score),url,page.pageId,link.getAllText()))
            #else:
            #    self.pages.append((page,0))
                                    
        print self.priorityQueue.isempty()
                
    def exists(self,url,alist):
        urlList = [v for p,v,k,l in alist]
        return url in urlList
