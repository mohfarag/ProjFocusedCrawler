#!/usr/local/bin/python
#import sys
from crawler import Crawler
from priorityQueue import PriorityQueue
#from NBClassifier import NaiveBayesClassifier
from Filter import downloadRawDocs, getTokenizedDocs, getSeedURLs

#import numpy as np
#from sklearn import metrics
from TFIDF import TFIDF
from ExtendedPriorityQueue import PubVenPriorityQueue
from EnhancedCrawler import EnhancedCrawler
from eventModel import EventModel
from evaluate import Evaluate
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



def baseFC(crawlParams,seedsFile):
#def baseFC(crawlParams):

    mytfidf = TFIDF()
    
#     docs = downloadRawDocs(seedsFile)
#     cleandocs = getTokenizedDocs(docs)
#     mytfidf.buildModel(cleandocs)
    #seedURLs = crawlParams['seeds']
    mytfidf.buildModel(seedsFile)
    crawlParams['scorer']=mytfidf
    
    #crawler = Crawler(priorityQueue,scorer,options)
    crawler = Crawler(crawlParams)
    crawler.crawl()
    
    print crawler.relevantPagesCount
    print crawler.pagesCount
    
    f = open("base-harverstRatioData.txt","w")
    for r,p in crawler.harvestRatioData:
        f.write(str(r) + "," + str(p) + "\n")
    f.close()
    
    f = open("base-logData.txt","w")
    furl = open("base-Output-URLs.txt","w")
    for p in crawler.relevantPages:
        f.write(str(p.pageId) + "," + str(p.pageUrl[2]) + "\n")
        furl.write(p.pageUrl[1]+"\n")
    f.close()
    furl.close()
    return crawler.relevantPages

def eventFC(crawlParams):
    eventModel = EventModel()
    seedURLs = crawlParams['seeds']
    eventModel.buildEventModel(seedURLs)
    crawlParams['scorer']=eventModel
    crawler = Crawler(crawlParams)
    crawler.crawl()
    print crawler.relevantPagesCount
    print crawler.pagesCount
    
    f = open("event-harverstRatioData.txt","w")
    for r,p in crawler.harvestRatioData:
        f.write(str(r) + "," + str(p) + "\n")
    f.close()
    
    f = open("event-logData.txt","w")
    furl = open("event-Output-URLs.txt","w")
    for p in crawler.relevantPages:
        f.write(str(p.pageId) + "," + str(p.pageUrl[2]) + "\n")
        furl.write(p.pageUrl[1]+"\n")
    f.close()
    furl.close()
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


def startCrawl(seedsFile,posFile,negFile):
    #mytfidf = TFIDF()
    #docs = downloadRawDocs("typhoon_haiyan_SEED_URLs.txt")
    
    #seedURLs = getSeedURLs("typhoon_haiyan_SEED_URLs.txt")
    seedURLs = getSeedURLs(seedsFile)
    #posURLs = getSeedURLs(posFile)
    #negURLs = getSeedURLs(negFile)
    t = [(-1,p,-1,"") for p in seedURLs]
    priorityQueue = PriorityQueue(t)
    pagesLimit = 500
    pageScoreThreshold = 0.13
    urlScoreThreshold = 0.1
    
    #cleandocs = getTokenizedDocs(docs)
    #mytfidf.buildModel(cleandocs)
    
    #crawlParams = {"scorer":mytfidf,"num_pages": pagesLimit,"pageScoreThreshold":pageScoreThreshold,"urlScoreThreshold":urlScoreThreshold , "seeds":seedURLs, "priorityQueue":priorityQueue}
    crawlParams = {"num_pages": pagesLimit,"pageScoreThreshold":pageScoreThreshold,"urlScoreThreshold":urlScoreThreshold , "seeds":seedURLs, "priorityQueue":priorityQueue}
    
    #baseFC(crawlParams,seedsFile)
    
    relevantPages =baseFC(crawlParams,seedsFile) #3-13-14
    #relevantPages = eventFC(crawlParams)
    
    #intelligentFC(mytfidf,options)
    
    evaluator = Evaluate(posFile, negFile)
    res = evaluator.evaluateFC(relevantPages)
    print sum(res)
    print len(res)
    

if __name__ == "__main__":
    #inputFile = sys.argv[1]
    inputFile = "seedURLs.txt"
    posFile = "pos.txt"
    negFile = "neg.txt"
    startCrawl(inputFile,posFile,negFile)
    
