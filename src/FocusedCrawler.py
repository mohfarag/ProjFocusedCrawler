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

def startCrawl(v,seedsFile,evaluator,modelFile,ct):

    #switchFC = 1
    #number of keywords to represent event/topic
    num = 15
    pagesLimit = 500
    
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
    
    
    #crawlParams['t'] = t
    if ct =='b':
        #baseRelevantPages =baseFC(crawlParams)
        
        
        rp = baseFC(crawlParams)
        
        f = open("base-webpages/"+str(v)+"/"+"base-logData.txt","w")
        furl = open("base-webpages/"+str(v)+"/"+"base-Output-URLs.txt","w")
        for p in rp:
            f.write(str(p.pageId) + "," + str(p.pageUrl[2]) + "\n")
            #furl.write(p.pageUrl[1].encode("utf-8")+","+str(p.estimatedScore)+"\n")
            furl.write(p.pageUrl[1].encode("utf-8")+"\n")
            ftext = open("base-webpages/"+str(v)+"/"+str(p.pageId) + ".txt", "w")
            ftext.write(p.text.encode("utf-8"))
            ftext.close()
        f.close()
        furl.close()
        
        res = evaluator.evaluateFC(rp)
        writeEvaluation(res,"base-webpages/"+str(v)+"/"+"base-evaluateData.txt")    
        print sum(res)
        print len(res)
    else: 
        #eventRelevantPages = eventFC(crawlParams)
        
        rp = eventFC(crawlParams)
        f = open("event-webpages/"+str(v)+"/"+"event-logData.txt","w")
        furl = open("event-webpages/"+str(v)+"/"+"event-Output-URLs.txt","w")
        for p in rp:
            f.write(str(p.pageId) + "," + str(p.pageUrl[2]) + "\n")
            #furl.write(p.pageUrl[1].encode('utf-8')+","+str(p.estimatedScore)+"\n")
            furl.write(p.pageUrl[1].encode('utf-8')+"\n")
            ftext = open("event-webpages/"+str(v)+"/"+str(p.pageId) + ".txt", "w")
            ftext.write(p.text.encode("utf-8"))
            ftext.close()
        f.close()
        furl.close()
        res = evaluator.evaluateFC(rp)
        writeEvaluation(res,"event-webpages/"+str(v)+"/"+"event-evaluateData.txt")    
        print sum(res)
        print len(res)
    


if __name__ == "__main__":
    #modelFile = 'modelFile'
    #seedsFiles=['seeds_459.txt','seeds_474.txt','seeds_478.txt','seedsURLs_z_534.txt']
    seedsFiles=['seeds_459.txt','seeds_474.txt','seedsURLs_z_534.txt','seedsURLs_z_501.txt','seedsURLs_z_540.txt']
    #seedsFiles=['seedsURLs_z_501.txt','seedsURLs_z_504.txt','seedsURLs_z_529.txt','seedsURLs_z_540.txt']
    #posFiles = ['pos-FSU.txt','pos-Hagupit.txt','pos-LAFire.txt','pos-AirAsia.txt']
    posFiles = ['pos-FSU.txt','pos-Hagupit.txt','pos-AirAsia.txt','pos-sydneyseige.txt','pos-Charlie.txt']
    #negFolder = 'neg'
    negFiles = ['neg-FSU.txt','neg-Hagupit.txt','neg-AirAsia.txt','neg-sydneyseige.txt','neg-Charlie.txt']
    
    '''
    seedsFiles=['seedsURLs_z_501.txt','seedsURLs_z_540.txt']
    
    #posFiles = ['pos-FSU.txt','pos-Hagupit.txt','pos-AirAsia.txt']
    #negFiles = ['neg-FSU.txt','neg-Hagupit.txt','neg-AirAsia.txt']
    
    posFiles = ['pos-Charlie.txt','pos-sydneyseige.txt']
    negFiles = ['neg-Charlie.txt','neg-sydneyseige.txt']
    '''
    
    evaluator = Evaluate()
    #for i in range(3):
    noK = 10
    th = 0.75
    i=0
    posFile = posFiles[i]
    negFile = negFiles[i]
    #modelFile = modelFile +"-"+str(i)+".txt"
    #classifierFileName = 'classifier'+posFile.split(".")[0].split('-')[1]+".p"
    vsmClassifierFileName = 'classifierVSM-'+posFile.split(".")[0].split('-')[1]+".p"
    #evaluator.buildClassifier(posFile,negFolder,classifierFileName)
    #evaluator.buildClassifier(posFile,negFile,classifierFileName)
    evaluator.buildVSMClassifier(posFile, vsmClassifierFileName,th,noK)

    v = 0

    inputFile = seedsFiles[i].split('.')[0]+"_"+str(v)+".txt"
    
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
    startCrawl(v,inputFile,evaluator,modelFile,crawlType)
    
