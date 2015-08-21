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
    return crawler.relevantPages
    #return crawler.relevantPages

def eventFC(crawlParams):
    
    seedURLs = crawlParams["seedURLs"] 
    t = [(-3,p,-1,"") for p in seedURLs]
    priorityQueue = PriorityQueue(t)
    
    crawlParams["priorityQueue"]=priorityQueue
    
    eventModel = EventModel(crawlParams['No_Keywords'])
    #eventModel = EventModel(5,2)
    
    eventModel.buildEventModel(crawlParams['model'])
    #eventModel.buildEventModel(20, crawlParams['model'])
    crawlParams['scorer']=eventModel
    crawler = Crawler(crawlParams)
    
    crawler.crawl()
    
    return crawler.relevantPages

def probEventFC(crawlParams):
    
    seedURLs = crawlParams["seedURLs"] 
    t = [(-0.0001,p,-1,"") for p in seedURLs]
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

def startCrawl(seedsFile,evaluator,modelFile,ct,num=5,pagesLimit=100, pageScoreThreshold=0.5,urlScoreThreshold=0):

    mode = 1 # URL scoring
    crawlParams = {"num_pages": pagesLimit,"pageScoreThreshold":pageScoreThreshold,"urlScoreThreshold":urlScoreThreshold ,"mode":mode}
    crawlParams['No_Keywords']=num
    seedURLs = getSeedURLs(seedsFile)
    crawlParams['seedURLs'] = seedURLs
    modelURLs = readFileLines(modelFile)
    crawlParams['model']=modelURLs
    crawlParams['restricted'] = 0
    crawlParams['combineScore'] = 0
    outputDir = seedsFile.split(".")[0]
    #crawlParams['t'] = t
    if ct =='b':
        #baseRelevantPages =baseFC(crawlParams)
        pagesDir=outputDir+"/base-webpages/"
        logDataFilename=pagesDir+"base-logData.txt"
        outputURLsFilename=pagesDir+"base-Output-URLs.txt"
        evalFilename=pagesDir+"base-evaluateData.txt"
        
        rp = baseFC(crawlParams)
        
    elif ct =='p':
        pagesDir=outputDir+"/prob-webpages/"
        logDataFilename=pagesDir+"prob-logData.txt"
        outputURLsFilename=pagesDir+"prob-Output-URLs.txt"
        evalFilename=pagesDir+"prob-evaluateData.txt"
        rp = probEventFC(crawlParams)
        
    elif ct =='e': 
        #eventRelevantPages = eventFC(crawlParams)
        pagesDir=outputDir+"/event-webpages/"
        logDataFilename=pagesDir+"event-logData.txt"
        outputURLsFilename=pagesDir+"event-Output-URLs.txt"
        evalFilename=pagesDir+"event-evaluateData.txt"
        rp = eventFC(crawlParams)
        
    
    #if not os.path.exists(outputDir):
    #    os.makedirs(outputDir)
    if not os.path.exists(pagesDir):
        os.makedirs(pagesDir)
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
    
    seedsFiles=['seeds-Sandra.txt','Output-tunisiaHotelAttack.txt','Output-samesexmarriage.txt','Output-CharlestonShooting.txt','Output-fifaArrests.txt','Output-boatCapsized.txt','Output-nepalEarthquake.txt','seeds_459.txt','seeds_474.txt','seedsURLs_z_534.txt','seedsURLs_z_501.txt','seedsURLs_z_540.txt']
    posFiles = ['evaluate-SandraBland.txt','pos-tunisiaHotelAttack.txt','pos-samesexmarriage.txt','pos-CharlestonShooting.txt','Output-fifaArrests.txt','Output-boatCapsized.txt','Output-nepalEarthquake.txt','pos-FSU.txt','pos-Hagupit.txt','pos-AirAsia.txt','pos-sydneyseige.txt','pos-Charlie.txt']
    negFiles = ['neg-FSU.txt','neg-Hagupit.txt','neg-AirAsia.txt','neg-sydneyseige.txt','neg-Charlie.txt']
    modelFiles = ['model-SandraBland.txt','model-tunisiaHotelAttack.txt','model-samesexmarriage.txt','model-CharlestonShooting.txt']
    evaluator = Evaluate()
    #for i in range(3):
    pagesLimit = 100
    noK = 5
    pageTh = 0.2
    urlsTh = 0
    i=0
    ct = 'e'
    
    
    posFile = posFiles[i]
    negFile = negFiles[i]
    vsmClassifierFileName = 'classifierVSM-'+posFile.split(".")[0].split('-')[1]+".p"
    evaluator.buildVSMClassifier(posFile, vsmClassifierFileName,pageTh,noK)
    inputFile = seedsFiles[i]
    modelFile = modelFiles[i]#'modelFile.txt'#inputFile
    
    mode = 1 # URL scoring with no page scoring
    crawlParams = {"num_pages": pagesLimit,"pageScoreThreshold":pageTh,"urlScoreThreshold":urlsTh ,"mode":mode}
    crawlParams['No_Keywords']=noK
    seedURLs = getSeedURLs(inputFile)
    crawlParams['seedURLs'] = seedURLs
    modelURLs = readFileLines(modelFile)
    crawlParams['model']=modelURLs
    crawlParams['restricted'] = 0
    crawlParams['combineScore'] = 0
    outputDir = inputFile.split(".")[0]
    #crawlParams['t'] = t
    if ct =='b':
        #baseRelevantPages =baseFC(crawlParams)
        pagesDir=outputDir+"/base-webpages/"
        logDataFilename=pagesDir+"base-logData.txt"
        outputURLsFilename=pagesDir+"base-Output-URLs.txt"
        evalFilename=pagesDir+"base-evaluateData.txt"
        
        rp = baseFC(crawlParams)
        
    elif ct =='p':
        pagesDir=outputDir+"/prob-webpages/"
        logDataFilename=pagesDir+"prob-logData.txt"
        outputURLsFilename=pagesDir+"prob-Output-URLs.txt"
        evalFilename=pagesDir+"prob-evaluateData.txt"
        rp = probEventFC(crawlParams)
        
    elif ct =='e': 
        #eventRelevantPages = eventFC(crawlParams)
        pagesDir=outputDir+"/event-webpages/"
        logDataFilename=pagesDir+"event-logData.txt"
        outputURLsFilename=pagesDir+"event-Output-URLs.txt"
        evalFilename=pagesDir+"event-evaluateData.txt"
        rp = eventFC(crawlParams)
        
    
    #if not os.path.exists(outputDir):
    #    os.makedirs(outputDir)
    if not os.path.exists(pagesDir):
        os.makedirs(pagesDir)
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
    
