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
#import nltk
#class FocusedCrawler:

""" 
def getPosFiles():
    f = open("html_files-sikkim.txt","r")
    fl = open("labels.txt","r")
    fw = open("positive.txt","w")
    for line in fl:
        strl = f.readline()
        if int(line) == 1:            
            #fw.write(strl +"\n")
            fw.write(strl)
    fw.close()
    fl.close()
    f.close()
    
   
def getStats():
    urls = open("positive.txt","r").readlines()
    stats = getDomainStat(urls)
    for k,v in stats.iteritems():
        print k + " " + str(len(v))


def writeToFile(data, fileName):
    f = codecs.open(fileName, "w")
    for elem in data:
        f.write(str(elem) + "\n")
    f.close()
    
def getLabelsFromFile(fileName):
    f = codecs.open(fileName,"r")
    labels = []
    for elem in f:
        num = int(elem[:-1])
        labels.append(int(num))
    f.close()
    return labels

def filterData(docs,urls,titles):
    pos = []
    neg = []
    
    topicKeywords = getTopicKeywords("topic-keywords.txt")
    i = 0
    f = open("labels.txt","w")
    for doc in docs:
        labels = []
        page_res = checkRelevance(doc, topicKeywords)
        url_res = checkRelevance(urls[i], topicKeywords)
        title_res = checkRelevance(titles[i], topicKeywords)
        
        avg = page_res + url_res + title_res / 3.0
        if avg > 3:
            pos.append(doc)
            f.write("1\n")
            labels.append(1)
        else:
            neg.append(doc)
            f.write("0\n")
            labels.append(0)
        i = i +1
    
    
    f.close()
    return pos,neg

def classifierFC():
    
    seedUrls = ["http://www.ndtv.com/topic/sikkim-earthquake",
                "http://zeenews.india.com/tags/Sikkim_earthquake.html",
                "http://earthquake-report.com/2011/09/18/very-strong-earthquake-in-sikkim-india/",
                "http://articles.timesofindia.indiatimes.com/2011-09-21/india/30184028_1_construction-site-teesta-urja-gangtok"
                ]
    urls_tokens = []
    title_tokens = []
    docs = getrawDocs("html_files2-balanced.txt",urls_tokens, title_tokens)
    print("raw docs extracted")
    docs_len = len(docs)
    labels = getLabelsFromFile("labels2-balanced.txt")
    print sum(labels)
    
    sep = int(docs_len*0.9)
    
    trainingDocs = docs[:sep]
    
    trainingLabels = labels[:sep]
    
    testDocs = docs[sep:]
    test_labels=labels[sep:]
    
    classifier = NaiveBayesClassifier()
    
    trainingLabelsArr = np.array(labels)
    classifier.trainClassifier(docs,trainingLabelsArr)
    
    trainingLabelsArr = np.array(trainingLabels)
    classifier.trainClassifier(trainingDocs,trainingLabelsArr)
    test_labelsArr = np.array(test_labels)
    print classifier.score(testDocs, test_labelsArr)
    
    print metrics.classification_report(test_labelsArr, classifier.predicted)
"""



def baseFC(crawlParams):
#def baseFC(crawlParams):
    #seedURLs = getSeedURLs(seedsFile)
    
    priorityQueue = PriorityQueue(crawlParams['t'])
    
    crawlParams["priorityQueue"]=priorityQueue
    mytfidf = TFIDF()
    
#     docs = downloadRawDocs(seedsFile)
#     cleandocs = getTokenizedDocs(docs)
#     mytfidf.buildModel(cleandocs)
    #seedURLs = crawlParams['seeds']
    mytfidf.buildModel(crawlParams['seedURLs'],crawlParams['No_Keywords'])
    crawlParams['scorer']=mytfidf
    
    #crawler = Crawler(priorityQueue,scorer,options)
    crawler = Crawler(crawlParams)
    crawler.crawl()
    
    print crawler.relevantPagesCount
    print crawler.pagesCount
    '''
    f = open("base-harverstRatioData.txt","w")
    for r,p in crawler.harvestRatioData:
        f.write(str(r) + "," + str(p) + "\n")
    f.close()
    '''
    f = open("base-logData.txt","w")
    furl = open("base-Output-URLs.txt","w")
    for p in crawler.relevantPages:
        f.write(str(p.pageId) + "," + str(p.pageUrl[2]) + "\n")
        furl.write(p.pageUrl[1]+"\n")
        ftext = open("base-webpages/"+str(p.pageId) + ".txt", "w")
        ftext.write(p.text.encode("utf-8"))
        ftext.close()
    f.close()
    furl.close()
    return crawler.pages
    #return crawler.relevantPages

def eventFC(crawlParams):
    
    #crawlParams["seeds"] = seedURLs
    
    priorityQueue = PriorityQueue(crawlParams['t'])
    
    crawlParams["priorityQueue"]=priorityQueue
    
    #eventModel = EventModel()
    #eventModel.buildEventModel(crawlParams['seedURLs'],crawlParams['No_Keywords'])
    eventModel = EventModel(crawlParams['No_Keywords'])
    eventModel.buildEventModel(crawlParams['seedURLs'])
    
    
    crawlParams['scorer']=eventModel
    crawler = Crawler(crawlParams)
    crawler.crawl()
    print crawler.relevantPagesCount
    print crawler.pagesCount
    
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
    return crawler.pages
    #return crawler.relevantPages
    

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
    pagesLimit = 100
    
    pageScoreThreshold =0.7
    urlScoreThreshold = 0
    #mode = 0 # no URL scoring
    mode = 1 # URL scoring
    crawlParams = {"num_pages": pagesLimit,"pageScoreThreshold":pageScoreThreshold,"urlScoreThreshold":urlScoreThreshold ,"mode":mode}
    crawlParams['No_Keywords']=num
    seedURLs = getSeedURLs(seedsFile)
    crawlParams['seedURLs'] = seedURLs
    
    t = [(-1,p,-1,"") for p in seedURLs]
    crawlParams['t'] = t
    
    baseRelevantPages =baseFC(crawlParams)
    
    bres = evaluator.evaluateFC(baseRelevantPages)
    writeEvaluation(bres,"base-evaluateData.txt")    
    print sum(bres)
    print len(bres)
    
    #else:
    t = [(-3,p,-1,"") for p in seedURLs]
    crawlParams['t'] = t
    
    eventRelevantPages = eventFC(crawlParams)   
    
    eres = evaluator.evaluateFC(eventRelevantPages)
    writeEvaluation(eres,"event-evaluateData.txt")    
    print sum(eres)
    print len(eres)



if __name__ == "__main__":
    
    seedsFiles=['seeds_459.txt','seeds_474.txt','seeds_478.txt']
    posFiles = ['pos-FSU.txt','pos-Hagupit.txt','pos-LAFire.txt']
    negFolder = 'neg'
    
    #i=0
    evaluator = Evaluate()
    #for i in range(3):
    i=0
    posFile = posFiles[i]
    classifierFileName = 'classifier'+posFile.split(".")[0].split('-')[1]+".p"
    
    evaluator.buildClassifier(posFile,negFolder,classifierFileName)

    
    v=0
    inputFile = seedsFiles[i].split('.')[0]+"_"+str(v)+".txt"
    
    startCrawl(inputFile,evaluator)
    
