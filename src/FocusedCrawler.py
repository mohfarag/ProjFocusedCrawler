#!/usr/local/bin/python
#import sys
from crawler import Crawler
from priorityQueue import PriorityQueue
#from NBClassifier import NaiveBayesClassifier
from Filter import getSeedURLs

#import numpy as np
#from sklearn import metrics
from TFIDF import TFIDF
from ExtendedPriorityQueue import PubVenPriorityQueue
from EnhancedCrawler import EnhancedCrawler
from eventModel import EventModel
from evaluate import Evaluate
from eventUtils import train_SaveClassifier, readFileLines
import os

def baseFC(crawlParams):
    seedURLs = crawlParams['seedURLs']
    t = [(-1,p,-1,"") for p in seedURLs]
    priorityQueue = PriorityQueue(t)
    
    crawlParams["priorityQueue"]=priorityQueue
    mytfidf = TFIDF()
   
    mytfidf.buildModel(crawlParams['seedURLs'],crawlParams['No_Keywords'])
    crawlParams['scorer']=mytfidf
    
    #crawler = Crawler(priorityQueue,scorer,options)
    crawler = Crawler(crawlParams)
    crawler.crawl()
   
    f = open("base-logData.txt","w")
    furl = open("base-Output-URLs.txt","w")
    for p in crawler.relevantPages:
        f.write(str(p.pageId) + "," + str(p.pageUrl[2]) + "\n")
        furl.write(p.pageUrl[1].encode("utf-8")+"\n")
        ftext = open("base-webpages/"+str(p.pageId) + ".txt", "w")
        ftext.write(p.text.encode("utf-8"))
        ftext.close()
    f.close()
    furl.close()
    
    bres = evaluator.evaluateFC(crawler.relevantPages)
    writeEvaluation(bres,"base-evaluateData.txt")    
    print sum(bres)
    print len(bres)
    
    return crawler.relevantPages
    #return crawler.relevantPages

def eventFC(crawlParams):
    
    seedURLs = crawlParams["seedURLs"] 
    t = [(-3,p,-1,"") for p in seedURLs]
    priorityQueue = PriorityQueue(t)
    
    crawlParams["priorityQueue"]=priorityQueue
    
    eventModel = EventModel()
    #eventModel = EventModel(crawlParams['No_Keywords'])
    eventModel.buildEventModel(crawlParams['seedURLs'])
    
    
    crawlParams['scorer']=eventModel
    crawler = Crawler(crawlParams)
    crawler.crawl()
    #print crawler.relevantPagesCount
    #print crawler.pagesCount
    
#     f = open("event-harverstRatioData.txt","w")
#     for r,p in crawler.harvestRatioData:
#         f.write(str(r) + "," + str(p) + "\n")
#     f.close()
    
    f = open("event-logData.txt","w")
    furl = open("event-Output-URLs.txt","w")
    for p in crawler.relevantPages:
        f.write(str(p.pageId) + "," + str(p.pageUrl[2]) + "\n")
        furl.write(p.pageUrl[1]+"\n")
        ftext = open("event-webpages/"+str(p.pageId) + ".txt", "w")
        ftext.write(p.text.encode("utf-8"))
        ftext.close()
    f.close()
    furl.close()
    #return crawler.pages
    eres = evaluator.evaluateFC(crawler.relevantPages)
    writeEvaluation(eres,"event-evaluateData.txt")    
    print sum(eres)
    print len(eres)
    return crawler.relevantPages
    
def intelligentFC(scorer,options):
    seedUrls = ["http://www.cnn.com/2013/09/27/world/africa/kenya-mall-attack/index.html",
                "http://www.youtube.com/watch?v=oU9Oop892BQ",
                "http://ifrc.org/en/news-and-media/press-releases/africa/kenya/kenya-red-cross-society-continues-to-provide-vital-support-to-victims-and-families-of-the-westgate-shopping-mall-attack/"               
                ]
    #keywords = ['demonstrations','protest','elections','egypt','revolution','uprising','arab','spring','tunisia','libya','military']
    
    t = [(-1,p,-1) for p in seedUrls]
    priorityQueue = PubVenPriorityQueue(t[:1],[t[1]],t[2:])
   
    crawler = EnhancedCrawler(priorityQueue,scorer,options)
    crawler.crawl()
    print crawler.relevantPagesCount
    print crawler.pagesCount
    
    f = open("harverstRatioDataPub.txt","w")
    for r,p in crawler.harvestRatioData:
        f.write(str(r) + "," + str(p) + "\n")
    f.close()
    
    f = open("logDataPub.txt","w")
    for p in crawler.relevantPages:
        f.write(str(p.pageId) + "," + str(p.pageUrl[2]) + "\n")
    f.close()

def writeEvaluation(res,filename):
    f = open(filename,"w")
    #for p,e in zip(relevantPages,res):
    rel = 0
    tot = 0
    for r in res:
        rel = rel + r
        tot = tot + 1 
        f.write(str(rel) + "," + str(tot) + "\n")
    f.close()

def startCrawl(seedsFile,evaluator):

    #switchFC = 1
    #number of keywords to represent event/topic
    num = 20
    pagesLimit = 500
    
    pageScoreThreshold =0.7
    urlScoreThreshold = 0
    #mode = 0 # no URL scoring
    mode = 1 # URL scoring
    crawlParams = {"num_pages": pagesLimit,"pageScoreThreshold":pageScoreThreshold,"urlScoreThreshold":urlScoreThreshold ,"mode":mode}
    crawlParams['No_Keywords']=num
    seedURLs = getSeedURLs(seedsFile)
    crawlParams['seedURLs'] = seedURLs
    
    
    #crawlParams['t'] = t
    
    #baseRelevantPages =baseFC(crawlParams) 
    eventRelevantPages = eventFC(crawlParams)



if __name__ == "__main__":
    
    seedsFiles=['seeds_459.txt','seeds_474.txt','seeds_478.txt']
    posFiles = ['pos-FSU.txt','pos-Hagupit.txt','pos-LAFire.txt']
    negFolder = 'neg'
    
    #i=0
    evaluator = Evaluate()
    #for i in range(3):
    i=1
    posFile = posFiles[i]
    classifierFileName = 'classifier'+posFile.split(".")[0].split('-')[1]+".p"
    
    evaluator.buildClassifier(posFile,negFolder,classifierFileName)



    v = 1

    inputFile = seedsFiles[i].split('.')[0]+"_"+str(v)+".txt"
    
    startCrawl(inputFile,evaluator)
    
