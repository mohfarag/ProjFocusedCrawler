#!/usr/local/bin/python
from crawler import Crawler
from priorityQueue import PriorityQueue
from tfidfScorer import TFIDF_Scorer
from NBClassifier import NaiveBayesClassifier
from SVMClassifier import SVMClassifier
from Filter import *
from nltk import FreqDist
import numpy as np
from gensim import corpora, models, similarities

def baseFC():
    seedUrls = ["http://www.aljazeera.com/indepth/spotlight/anger-in-egypt/",
                "http://live.reuters.com/Event/Unrest_in_Egypt?Page=0",
                "http://www.guardian.co.uk/world/series/egypt-protests",
                "http://www.huffingtonpost.com/2012/06/24/egypt-uprising-election-timeline_n_1622773.html",
                "http://www.washingtonpost.com/wp-srv/world/special/egypt-transition-timeline/index.html",
                "http://botw.org/top/Regional/Africa/Egypt/Society_and_Culture/Politics/Protests_2011/"
                ]
    #keywords = ['demonstrations','protest','elections','egypt','revolution','uprising','arab','spring','tunisia','libya','military']
    
    t = [(-1,p) for p in seedUrls]
    priorityQueue = PriorityQueue(t)
    #sc = Scorer(seedUrls)
    #sc = Scorer(keywords)
    sc = TFIDF_Scorer(seedUrls)
    crawler = Crawler(priorityQueue,sc,10)
    crawler.crawl()
    print crawler.relevantPagesCount
    print crawler.totalPagesCount

def documents_features(word_features,docs):
    
    docs_features = []
    doc_features=[]
    for doc in docs:
        for word in word_features:
            if word in doc:
                doc_features.append(word)
            #else:
            #    doc_features.append("")
        docs_features.append(doc_features)
    return docs_features
        

def main():
    #seedUrls = ["http://www.huffingtonpost.com/news/arab-spring/","http://www.opendemocracy.net/david-hayes/arab-spring-protest-power-prospect","http://www.washingtonpost.com/wp-srv/special/world/middle-east-protests/"]
    seedUrls = ["http://www.aljazeera.com/indepth/spotlight/anger-in-egypt/",
                "http://live.reuters.com/Event/Unrest_in_Egypt?Page=0",
                "http://www.guardian.co.uk/world/series/egypt-protests",
                "http://www.huffingtonpost.com/2012/06/24/egypt-uprising-election-timeline_n_1622773.html",
                "http://www.washingtonpost.com/wp-srv/world/special/egypt-transition-timeline/index.html",
                "http://botw.org/top/Regional/Africa/Egypt/Society_and_Culture/Politics/Protests_2011/"
                ]
    #topicKeywords = ['demonstrations','protest','elections','egypt','revolution','uprising','arab','spring','tunisia','libya','military']
    topicKeywords = getTopicKeywords("manual-sikkim-earthquake-wikipedia.txt")
    
    docs = getrawDocs("html_files.txt")
    #docs = downloadRawDocs("urls.txt")
    docs = [page for page in docs if page != ""]
    print("raw docs extracted")
    docs_len = len(docs)
    docs_tokens = getTokenizedDocs(docs)
    print(" docs tokens extracted")
    labels = getLabels(docs_tokens, topicKeywords)
    
    print("docs labels calcualted")
    
    all_words = [w for doc in docs_tokens for w in doc]
    docs_tf= []
    freq = FreqDist(all_words)
    word_features = freq.keys()[:100]
    
    #for doc in docs_tokens:
    #   doc_tf = [freq[word]/float(len(doc)) for word in doc]
    #    docs_tf.append(doc_tf)
    
    docs_features = documents_features(word_features,docs_tokens)
    docsDictionary = corpora.Dictionary(docs_features)
    corpus = [docsDictionary.doc2bow(text) for text in docs_features]
    tfidf = models.TfidfModel(corpus,normalize=True)
    corpus_tfidf = tfidf[corpus]
    
    '''docs_tf_array = np.array(docs_tf)
    print docs_tf_array.shape
    sep = int(docs_len*0.9)
    trainingDocs = docs_tf_array[:sep]
    trainingLabels = np.array(labels[:sep])
    testDocs = docs_tf_array[sep:]
    test_labels=np.array(labels[sep:])
    print trainingDocs.shape
    '''
    '''
    sep = int(docs_len*0.9)
    trainingDocs = docs[:sep]
    trainingLabels = labels[:sep]
    testDocs = docs[sep:]
    test_labels=labels[sep:]
    '''
    #classifier = NaiveBayesClassifier()
    classifier = SVMClassifier()
    
    classifier.trainClassifier(trainingDocs,trainingLabels)
    
    print("classifer trained")
    
    print classifier.score(testDocs, test_labels)
    
    
    
    '''t = [(-1,p) for p in seedUrls]
    priorityQueue = PriorityQueue(t)
    #sc = Scorer(seedUrls)
    #sc = Scorer(keywords)
    sc = TFIDF_Scorer(seedUrls)
    crawler = Crawler(priorityQueue,sc,10)
    crawler.crawl()
    print crawler.relevantPagesCount
    print crawler.totalPagesCount
    #print "Precision %f" % crawler.relevantPagesCount / float(crawler.totalPagesCount)
    '''

if __name__ == "__main__":
    main()
