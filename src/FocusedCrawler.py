#!/usr/local/bin/python
from crawler import Crawler
from priorityQueue import PriorityQueue
from tfidfScorer import TFIDF_Scorer
from NBClassifier import NaiveBayesClassifier
from SVMClassifier import SVMClassifier
from Filter import *
import numpy as np
from sklearn import metrics
from TFIDF import TFIDF
from ExtendedPriorityQueue import PubVenPriorityQueue
from url import Url
from EnhancedCrawler import EnhancedCrawler
#import nltk
#class FocusedCrawler:
	
def baseFC(scorer,options):
#     seedUrls = ["http://www.cnn.com/2013/09/27/world/africa/kenya-mall-attack/index.html",
#                 "http://www.youtube.com/watch?v=oU9Oop892BQ",
#                 "http://ifrc.org/en/news-and-media/press-releases/africa/kenya/kenya-red-cross-society-continues-to-provide-vital-support-to-victims-and-families-of-the-westgate-shopping-mall-attack/"               
#                 ]
    #keywords = ['demonstrations','protest','elections','egypt','revolution','uprising','arab','spring','tunisia','libya','military']
    
    t = [(-1,p,-1) for p in options['seeds']]
    #t = [(-1,Url(p)) for p in seedUrls]
    priorityQueue = PriorityQueue(t)
    
    crawler = Crawler(priorityQueue,scorer,options)
    crawler.crawl()
    print crawler.relevantPagesCount
    print crawler.pagesCount
    
    f = open("harverstRatioData.txt","w")
    for r,p in crawler.harvestRatioData:
        f.write(str(r) + "," + str(p) + "\n")
    f.close()
    
    f = open("logData.txt","w")
    for p in crawler.relevantPages:
        f.write(str(p.pageId) + "," + str(p.pageUrl[2]) + "\n")
    f.close()
    
    
def intelligentFC(scorer,options):
#     seedUrls = ["http://www.cnn.com/2013/09/27/world/africa/kenya-mall-attack/index.html",
#                 "http://www.youtube.com/watch?v=oU9Oop892BQ",
#                 "http://ifrc.org/en/news-and-media/press-releases/africa/kenya/kenya-red-cross-society-continues-to-provide-vital-support-to-victims-and-families-of-the-westgate-shopping-mall-attack/"               
#                 ]
    #keywords = ['demonstrations','protest','elections','egypt','revolution','uprising','arab','spring','tunisia','libya','military']
    
    t = [(-1,p,-1) for p in options['seeds']]
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

def main():
    
    #seedUrls = ["http://www.huffingtonpost.com/news/arab-spring/","http://www.opendemocracy.net/david-hayes/arab-spring-protest-power-prospect","http://www.washingtonpost.com/wp-srv/special/world/middle-east-protests/"]
    #seedUrls = ["http://www.ndtv.com/article/india/big-earthquake-in-sikkim-tremors-across-india-54-dead-over-100-injured-134537",
    #           "http://articles.timesofindia.indiatimes.com/2011-09-21/india/30184028_1_construction-site-teesta-urja-gangtok",
    #            "http://www.ndtv.com/article/india/quake-aftermath-many-villages-in-sikkim-still-cut-off-thousands-waiting-for-help-135132",
    #            "http://www.ndtv.com/article/india/12-dead-40-missing-at-sikkim-plant-hit-by-quake-135215"
    #            ]
    seedUrls = ["http://www.ndtv.com/topic/sikkim-earthquake",
                "http://zeenews.india.com/tags/Sikkim_earthquake.html",
                "http://earthquake-report.com/2011/09/18/very-strong-earthquake-in-sikkim-india/",
                "http://articles.timesofindia.indiatimes.com/2011-09-21/india/30184028_1_construction-site-teesta-urja-gangtok"
                ]
    '''
    seedUrls = ["http://www.aljazeera.com/indepth/spotlight/anger-in-egypt/",
                "http://live.reuters.com/Event/Unrest_in_Egypt?Page=0",
                "http://www.guardian.co.uk/world/series/egypt-protests",
                "http://www.huffingtonpost.com/2012/06/24/egypt-uprising-election-timeline_n_1622773.html",
                "http://www.washingtonpost.com/wp-srv/world/special/egypt-transition-timeline/index.html",
                "http://botw.org/top/Regional/Africa/Egypt/Society_and_Culture/Politics/Protests_2011/"
                ]
    '''
    #topicKeywords = ['demonstrations','protest','elections','egypt','revolution','uprising','arab','spring','tunisia','libya','military']
    ##topicKeywords = getTopicKeywords("manual-sikkim-earthquake-wikipedia.txt")
    urls_tokens = []
    title_tokens = []
    docs = getrawDocs("html_files2-balanced.txt",urls_tokens, title_tokens)
    #writeToFile(docs,"rawData.txt")
    print("raw docs extracted")
    docs_len = len(docs)
    #docs_tokens = getTokenizedDocs(docs)
    #print(" docs tokens extracted")
    #labels = getLabels(docs_tokens, topicKeywords)
    #writeToFile(labels,"labels.txt")
    labels = getLabelsFromFile("labels2-balanced.txt")
    print sum(labels)
    
    ##print("docs labels calcualted")
    
    sep = int(docs_len*0.9)
    
    trainingDocs = docs[:sep]
    
    trainingLabels = labels[:sep]
    
    testDocs = docs[sep:]
    test_labels=labels[sep:]
    
    classifier = NaiveBayesClassifier()
    
    #classifier = SVMClassifier()
    
    trainingLabelsArr = np.array(labels)
    classifier.trainClassifier(docs,trainingLabelsArr)
    
    #print classifier.classifier.coef_
    #print classifier.ch2.get_support()
    
    trainingLabelsArr = np.array(trainingLabels)
    classifier.trainClassifier(trainingDocs,trainingLabelsArr)
    
    #print len(trainingDocs) 
    #print len (trainingLabelsArr)
    #classifier.trainClassifier(trainingDocs,trainingLabels)
    
    #print("classifer trained")
    #print (classifier.classifier)
    #print sum(test_labels)
    
    test_labelsArr = np.array(test_labels)
    print classifier.score(testDocs, test_labelsArr)
    
    #print sum(classifier.predicted)
    #print classifier.score(testDocs, test_labels)
    
    print metrics.classification_report(test_labelsArr, classifier.predicted)
    
    '''
    t = [(-1,p) for p in seedUrls]
    priorityQueue = PriorityQueue(t)
    #sc = Scorer(seedUrls)
    #sc = Scorer(keywords)
    #sc = TFIDF_Scorer(seedUrls)
    #crawler = Crawler(priorityQueue,sc,10)
    crawler = Crawler(priorityQueue,classifier,100)
    crawler.crawl()
    print crawler.relevantPagesCount
    #print crawler.totalPagesCount
    print crawler.pagesCount
    #print "Precision %f" % crawler.relevantPagesCount / float(crawler.totalPagesCount)
    '''

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

def getSeedURLs(fileName):
	seeds = []
	f = open(fileName,"r")
	for line in f:
		seeds.append(line[:-1])
	return seeds

def test():
    mytfidf = TFIDF()
    docs = downloadRawDocs("typhoon_haiyan_SEED_URLs.txt")
    seedURLs = getSeedURLs("typhoon_haiyan_SEED_URLs.txt")
    pagesLimit = 1000
    pageScoreThreshold = 0.5
    urlScoreThreshold = 0.4
    options = {"num_pages": pagesLimit,"pageScoreThreshold":pageScoreThreshold,"urlScoreThreshold":urlScoreThreshold , "seeds":seedURLs}
    #print urls_tokens
    #print title_tokens    
    
    cleandocs = getTokenizedDocs(docs)
    
    pos = cleandocs
    
    #print len(pos)
    #print len(neg)
    #print pos
    mytfidf.buildModel(pos)
    #mytfidf.buildModel(cleandocs)
    #mytfidf.buildModel(cleandocs,urls_tokens,title_tokens)
    
    baseFC(mytfidf,options,)
    #intelligentFC(mytfidf,options)

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

if __name__ == "__main__":
    #baseFC()
    #main()
    test()
    #getPosFiles()
    #getStats()
    
