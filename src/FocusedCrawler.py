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
from ProbEventModel import ProbEventModel
from evaluate import Evaluate
from eventUtils import train_SaveClassifier, readFileLines
import os

def baseFC(crawlParams):
    seedURLs = crawlParams['seedURLs']
    t = [(-1,p,-1,"") for p in seedURLs]
    priorityQueue = PriorityQueue(t)
    
    crawlParams["priorityQueue"]=priorityQueue
    mytfidf = TFIDF()
    
    mytfidf.buildModel(crawlParams['model'],crawlParams['No_Keywords'])
    #mytfidf.buildModel(crawlParams['seedURLs'],crawlParams['No_Keywords'])
    crawlParams['scorer']=mytfidf
    
    #crawler = Crawler(priorityQueue,scorer,options)
    crawler = Crawler(crawlParams)
    crawler.crawl()

    '''
    f = open("base-logData.txt","w")
    furl = open("base-Output-URLs.txt","w")
    for p in crawler.relevantPages:
        f.write(str(p.pageId) + "," + str(p.pageUrl[2]) + "\n")
        furl.write(p.pageUrl[1].encode("utf-8")+","+str(p.estimatedScore)+"\n")
        ftext = open("base-webpages/"+str(p.pageId) + ".txt", "w")
        ftext.write(p.text.encode("utf-8"))
        ftext.close()
    f.close()
    furl.close()
    bres = evaluator.evaluateFC(crawler.relevantPages)
    writeEvaluation(bres,"base-evaluateData.txt")    
    print sum(bres)
    print len(bres)
    '''
    return crawler.relevantPages
    #return crawler.relevantPages

def eventFC(crawlParams):
    
    seedURLs = crawlParams["seedURLs"] 
    t = [(-3,p,-1,"") for p in seedURLs]
    priorityQueue = PriorityQueue(t)
    
    crawlParams["priorityQueue"]=priorityQueue
    
    #eventModel = EventModel(crawlParams['No_Keywords'],2)
    eventModel = EventModel(5,2)
    
    #eventModel.buildEventModel(crawlParams['seedURLs'])
    eventModel.buildEventModel(20, crawlParams['model'])
    
    
    crawlParams['scorer']=eventModel
    crawler = Crawler(crawlParams)
    
    crawler.crawl()
    
    
    #return crawler.pages
    '''
    f = open("event-logData.txt","w")
    furl = open("event-Output-URLs.txt","w")
    for p in crawler.relevantPages:
        f.write(str(p.pageId) + "," + str(p.pageUrl[2]) + "\n")
        furl.write(p.pageUrl[1].encode('utf-8')+","+str(p.estimatedScore)+"\n")
        ftext = open("event-webpages/"+str(p.pageId) + ".txt", "w")
        ftext.write(p.text.encode("utf-8"))
        ftext.close()
    f.close()
    furl.close()
    
    eres = evaluator.evaluateFC(crawler.relevantPages)
    writeEvaluation(eres,"event-evaluateData.txt")    
    print sum(eres)
    print len(eres)
    '''
    return crawler.relevantPages

def probEventFC(crawlParams):
    
    seedURLs = crawlParams["seedURLs"] 
    t = [(-1000,p,-1,"") for p in seedURLs]
    priorityQueue = PriorityQueue(t)
    
    crawlParams["priorityQueue"]=priorityQueue
    
    #eventModel = EventModel(crawlParams['No_Keywords'],2)
    probEvtModel = ProbEventModel()
    
    #eventModel.buildEventModel(crawlParams['seedURLs'])
    probEvtModel.buildProbEventModel(crawlParams['model'],crawlParams['No_Keywords'])
    
    
    crawlParams['scorer']=probEvtModel
    crawler = Crawler(crawlParams)
    
    crawler.crawl()
    
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

#def startCrawl(v,seedsFile,evaluator,modelFile,ct):
def startCrawl(seedsFile,evaluator,modelFile,ct):

    #switchFC = 1
    #number of keywords to represent event/topic
    num = 10
    pagesLimit = 300
    
    pageScoreThreshold =0.7
    urlScoreThreshold = 0
    #mode = 0 # no URL scoring
    mode = 1 # URL scoring
    crawlParams = {"num_pages": pagesLimit,"pageScoreThreshold":pageScoreThreshold,"urlScoreThreshold":urlScoreThreshold ,"mode":mode}
    crawlParams['No_Keywords']=num
    seedURLs = getSeedURLs(seedsFile)
    crawlParams['seedURLs'] = seedURLs
    modelURLs = readFileLines(modelFile)
    crawlParams['model']=modelURLs
    crawlParams['restricted'] = 0
    crawlParams['combineScore'] = 0
    
    #crawlParams['t'] = t
    if ct =='b':
        #baseRelevantPages =baseFC(crawlParams)
        logDataFilename="base-webpages/base-logData.txt"
        outputURLsFilename="base-webpages/base-Output-URLs.txt"
        pagesDir="base-webpages/"
        evalFilename="base-webpages/base-evaluateData.txt"
        
        rp = baseFC(crawlParams)
        '''
        #f = open("base-webpages/"+str(v)+"/"+"base-logData.txt","w")
        #furl = open("base-webpages/"+str(v)+"/"+"base-Output-URLs.txt","w")
        f = open("base-webpages/base-logData.txt","w")
        furl = open("base-webpages/base-Output-URLs.txt","w")
        for p in rp:
            f.write(str(p.pageId) + "," + str(p.pageUrl[2]) + "\n")
            #furl.write(p.pageUrl[1].encode("utf-8")+","+str(p.estimatedScore)+"\n")
            furl.write(p.pageUrl[1].encode("utf-8")+"\n")
            ftext = open("base-webpages/"+str(p.pageId) + ".txt", "w")
            ftext.write(p.text.encode("utf-8"))
            ftext.close()
        f.close()
        furl.close()
        
        res = evaluator.evaluateFC(rp)
        writeEvaluation(res,"base-webpages/base-evaluateData.txt")    
        print sum(res)
        print len(res)
        '''
    elif ct =='p':
        logDataFilename="prob-webpages/prob-logData.txt"
        outputURLsFilename="prob-webpages/prob-Output-URLs.txt"
        pagesDir="prob-webpages/"
        evalFilename="prob-webpages/prob-evaluateData.txt"
        rp = probEventFC(crawlParams)
        '''
        #f = open("base-webpages/"+str(v)+"/"+"base-logData.txt","w")
        #furl = open("base-webpages/"+str(v)+"/"+"base-Output-URLs.txt","w")
        f = open("prob-webpages/prob-logData.txt","w")
        furl = open("prob-webpages/prob-Output-URLs.txt","w")
        for p in rp:
            f.write(str(p.pageId) + "," + str(p.pageUrl[2]) + "\n")
            #furl.write(p.pageUrl[1].encode("utf-8")+","+str(p.estimatedScore)+"\n")
            furl.write(p.pageUrl[1].encode("utf-8")+"\n")
            ftext = open("prob-webpages/"+str(p.pageId) + ".txt", "w")
            ftext.write(p.text.encode("utf-8"))
            ftext.close()
        f.close()
        furl.close()
        
        res = evaluator.evaluateFC(rp)
        writeEvaluation(res,"prob-webpages/prob-evaluateData.txt")    
        print sum(res)
        print len(res)
        '''
    elif ct =='e': 
        #eventRelevantPages = eventFC(crawlParams)
        logDataFilename="event-webpages/event-logData.txt"
        outputURLsFilename="event-webpages/event-Output-URLs.txt"
        pagesDir="event-webpages/"
        evalFilename="event-webpages/event-evaluateData.txt"
        rp = eventFC(crawlParams)
        '''
        f = open(logDataFilename,"w")
        furl = open(outputURLsFilename,"w")
        for p in rp:
            f.write(str(p.pageId) + "," + str(p.pageUrl[2]) + "\n")
            #furl.write(p.pageUrl[1].encode('utf-8')+","+str(p.estimatedScore)+"\n")
            furl.write(p.pageUrl[1].encode('utf-8')+"\n")
            ftext = open(pagesDir+str(p.pageId) + ".txt", "w")
            ftext.write(p.text.encode("utf-8"))
            ftext.close()
        f.close()
        furl.close()
        res = evaluator.evaluateFC(rp)
        writeEvaluation(res,evalFilename)    
        print sum(res)
        print len(res)
        '''
    f = open(logDataFilename,"w")
    furl = open(outputURLsFilename,"w")
    
    for p in rp:
        f.write(str(p.pageId) + "," + str(p.pageUrl[2]) + "\n")
        #furl.write(p.pageUrl[1].encode("utf-8")+","+str(p.estimatedScore)+"\n")
        furl.write(p.pageUrl[1].encode("utf-8")+"\n")
        ftext = open(pagesDir+str(p.pageId) + ".txt", "w")
        ftext.write(p.text.encode("utf-8"))
        ftext.close()
    f.close()
    furl.close()
    
    res = evaluator.evaluateFC(rp)
    writeEvaluation(res,evalFilename)    
    print sum(res)
    print len(res)


if __name__ == "__main__":
    
    seedsFiles=['Output-boatCapsized.txt','Output-nepalEarthquake.txt','seeds_459.txt','seeds_474.txt','seedsURLs_z_534.txt','seedsURLs_z_501.txt','seedsURLs_z_540.txt']
    
    posFiles = ['Output-boatCapsized.txt','Output-nepalEarthquake.txt','pos-FSU.txt','pos-Hagupit.txt','pos-AirAsia.txt','pos-sydneyseige.txt','pos-Charlie.txt']
    #negFolder = 'neg'
    negFiles = ['neg-FSU.txt','neg-Hagupit.txt','neg-AirAsia.txt','neg-sydneyseige.txt','neg-Charlie.txt']
    
    evaluator = Evaluate()
    #for i in range(3):
    noK = 10
    th = 0.2
    i=0
    posFile = posFiles[i]
    negFile = negFiles[i]
    #modelFile = modelFile +"-"+str(i)+".txt"
    #classifierFileName = 'classifier'+posFile.split(".")[0].split('-')[1]+".p"
    vsmClassifierFileName = 'classifierVSM-'+posFile.split(".")[0].split('-')[1]+".p"
    #evaluator.buildClassifier(posFile,negFolder,classifierFileName)
    #evaluator.buildClassifier(posFile,negFile,classifierFileName)
    evaluator.buildVSMClassifier(posFile, vsmClassifierFileName,th,noK)

    #v = 0

    #inputFile = seedsFiles[i].split('.')[0]+"_"+str(v)+".txt"
    inputFile = seedsFiles[i]
    
    '''
    event = 'Charlie'
    posFile = 'pos_'+event+'.txt'
    classifierFileName = 'classifier_'+event+'.p'
    evaluator.buildClassifier(posFile,negFolder,classifierFileName)
    inputFile = 'seedURLs_'+event+'.txt'
    modelFile = 'modelURLs_'+ event + '.txt'
    '''
    crawlType = 'e'
    modelFile = inputFile
    #startCrawl(v,inputFile,evaluator,modelFile,crawlType)
    startCrawl(inputFile,evaluator,modelFile,crawlType)
    
