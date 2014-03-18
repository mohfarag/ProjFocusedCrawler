'''
Created on Jan 27, 2013

@author: Mohamed
'''


# the new idea is to have a separate queue for each type of publishing , i.e. news, social, government (organization)

import heapq
from priorityQueue import PriorityQueue
class PubVenPriorityQueue:
    def __init__(self,newsSeedList,socialSeedList,govSeedList):        
        self.turn = 0
        '''
        if newsSeedList is not None:
            self.newsQueue = PriorityQueue(newsSeedList)
        if socialSeedList is not None:
            self.socialQueue = PriorityQueue(socialSeedList)
        if govSeedList is not None:
            self.govQueue = PriorityQueue(govSeedList)
        '''
        self.newsQueue = PriorityQueue(newsSeedList)
        self.socialQueue = PriorityQueue(socialSeedList)
        self.govQueue = PriorityQueue(govSeedList)
        
        heapq.heapify(self.newsQueue.queue)
        heapq.heapify(self.socialQueue.queue)
        heapq.heapify(self.govQueue.queue)


    def pop(self):
        if self.turn == 0:
            if self.newsQueue.isempty():
                self.turn = 1
                return self.pop()
            else:
                return heapq.heappop(self.newsQueue.queue)
        elif self.turn == 1:
            if self.socialQueue.isempty():
                self.turn = 2
                return self.pop()
            else:
                return heapq.heappop(self.socialQueue.queue)
        else:
            if self.govQueue.isempty():
                self.turn = 0
                return self.pop()
            else:
                return heapq.heappop(self.govQueue.queue)

    def push(self,element):
        if self.turn == 0:
            return heapq.heappush(self.newsQueue.queue,element)
        elif self.turn == 1:
            return heapq.heappush(self.socialQueue.queue,element)
        else:
            return heapq.heappush(self.govQueue.queue,element)
    
    def next(self):
        self.turn = (self.turn + 1 ) % 3
        
    def isempty(self):
        if self.govQueue.isempty() and self.newsQueue.isempty() and self.socialQueue.isempty():
            return True
        return False
    
    def exists(self,url):
        urlList = [v for p,v,k in self.newsQueue.queue]
        if url in urlList:
            return True
        else:
            urlList = [v for p,v,k in self.socialQueue.queue]
            if url in urlList:
                return True
            else:
                urlList = [v for p,v,k in self.govQueue.queue]
                return url in urlList
    '''
    def exists(self,url):
        if self.turn == 0:
            urlList = [v for p,v,k in self.newsQueue.queue]
            return url in urlList
        elif self.turn == 1:
            urlList = [v for p,v,k in self.socialQueue.queue]
            return url in urlList
        else:
            urlList = [v for p,v,k in self.govQueue.queue]
            return url in urlList
    '''    
        