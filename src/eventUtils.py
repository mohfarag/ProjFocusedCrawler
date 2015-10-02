#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
'''
Created on Oct 10, 2014

@author: dlrl
'''
import nltk
import sys, os
import re
from bs4 import BeautifulSoup, Comment, NavigableString
#import bs4
import requests
from nltk.corpus import stopwords
from readability.readability import Document
from operator import itemgetter
import math
import logging
from NBClassifier import NaiveBayesClassifier
from SVMClassifier import SVMClassifier
from oneClassClassifier import OneClassClassifier
import numpy as np
from sklearn import metrics
import ner
from gensim import corpora, models
import pickle
import random
import json
from nltk.stem.porter import PorterStemmer
from nltk.tokenize.regexp import WordPunctTokenizer
from _collections import defaultdict
#from _socket import timeout

#requests.packages.urllib3.disable_warnings()
from contextlib import closing

logging.getLogger('requests').setLevel(logging.WARNING)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}#'Digital Library Research Laboratory (DLRL)'}
#corpusTokens = []
#docsTokens = []
#allSents = []

stopwordsList = stopwords.words('english')
#stopwordsList.extend(["last","time","week","favorite","home","search","follow","year","account","update","com","video","close","http","retweet","tweet","twitter","news","people","said","comment","comments","share","email","new","would","one","world"])
stopwordsList.extend(["com","http","retweet","tweet","twitter","news","people"])

class VSMClassifier(object):
    '''
    def __init__(self, vocabDic,relevTh,docs):
        self.docs = docs
        self.relevanceth = relevTh
        self.vocabDic = vocabDic
        #doc1s = [1+math.log(self.topVocabDic[k]) for k in self.topVocabDic]
        self.docsScalar = []
        for d in docs:
            doc_s = d.values()
            self.docsScalar.append(getScalar(doc_s))
    '''
    #def __init__(self,error=0.05):
    #    self.error = error
    
    def buildVSMClassifier(self,posURLs,lk,vsmClassifierFileName='',error=0.05,roundPrec=3):
        self.error = error
        self.roundPrec = roundPrec
        #try:
        #    classifierFile = open(vsmClassifierFileName,"rb")
        #    self.classifier = pickle.load(classifierFile)
        #    classifierFile.close()
        #except:
        #docs = []
        if not vsmClassifierFileName:
            vsmClassifierFileName = posURLs.split('.')[0] + '-vsmClassifier.p'
        docs = getWebpageText_NoURLs(posURLs)
        docs = [d['text'] for d in docs if 'text' in d] 
        '''
        f = open(posFile,'r')
        for url in f:
            url = url.strip()
            d = Document(url)
            if d and d.text:
                docs.append(d)
        f.close()
        '''
        print len(docs)
        docsBOW = []
        vocabTFDic = defaultdict(list)
        maxFreqPerDocList = []
        for d in docs:
            docWords = getTokens(d) #d.getWords()
            wFreq = getFreq(docWords)
            maxFreq = float(max(wFreq.values()))
            maxFreqPerDocList.append(maxFreq)
            wordsFreq = {}
            for wf in wFreq:
                #wordsFreq[wf] = wFreq[wf]/docLen
                wordsFreq[wf] = wFreq[wf]/maxFreq
            docsBOW.append(wordsFreq)
            for w in wordsFreq:
                vocabTFDic[w].append( wordsFreq[w])
        
        print vocabTFDic
        
        #idf = 1.0
        #vocTF_IDF = [(w,sum([1+math.log(vtf) for vtf in vocabTFDic[w]])*idf) for w in vocabTFDic]
        
        #voc_CollFreq = [(w,sum(vocabTFDic[w]),len(vocabTFDic[w])) for w in vocabTFDic]
        voc_CollFreq = [(w,sum(vocabTFDic[w])) for w in vocabTFDic]
        voc_CollFreqSorted = getSorted(voc_CollFreq, 1)
        #maxFreq = max([fr for _,fr,_ in voc_CollFreq])
        #leastK = lk*1.0 / maxFreq
        
        #avgMaxFreq = sum(maxFreqPerDocList)*1.0 / len(maxFreqPerDocList)
        #if len(docs) > lk:
        #    lk = len(docs)
        #leastK = lk / avgMaxFreq
        #print leastK
        #print voc_CollFreq
        #vocab_filtered = [(w,fr) for w,fr,df in voc_CollFreq if fr>= leastK and df >= leastDocFreq] 
        #vocab_filtered_dict = dict(vocab_filtered)
        
        self.vocabDic = dict(voc_CollFreqSorted[:lk])
        
        #print len(vocab_filtered_dict)
        print self.vocabDic
        '''
        print vocabSorted[:topK]
        topVocabDic = dict(vocabSorted[:topK])
        '''
        # convert docs to BOW using new vocab
        newDocsBOW=[]
        for doc_bow in docsBOW:
            ndocBOW = {}
            for k in self.vocabDic:
                if k in doc_bow:
                    ndocBOW[k] = doc_bow[k]
                else:
                    ndocBOW[k] = 0 #1/math.e
            newDocsBOW.append(ndocBOW)
        self.docs = newDocsBOW
        
        self.docsScalar = []
        for d in newDocsBOW:
            doc_s = d.values()
            self.docsScalar.append(getScalar(doc_s))
        
        # Figure out similarity threshold using similarity between all docs
        newDocs_List = []
        for newdoc in newDocsBOW:
            newDocList = newdoc.values()
            newDocs_List.append(newDocList)
        docsSims = []
        #for doc1s in newDocs_List:
        for a in range(len(newDocs_List)-1):
            sims = []
            #for doc2s in newDocs_List:
            for b in range(a+1,len(newDocs_List)):
                s = 0
                '''
                for i in range(len(doc1s)):
                    s += doc1s[i] * doc2s[i]
                s = float(s)/ (getScalar(doc1s) * getScalar(doc2s))
                '''
                doc1s = newDocs_List[a]
                doc2s = newDocs_List[b]
                for i in range(len(doc1s)):
                    s += doc1s[i] * doc2s[i]
                #try:
                if s > 0:
                    s = float(s)/ (self.docsScalar[a] * self.docsScalar[b])
                #except:
                #else:
                    #print sys.exc_info()
                    #s= 0
                sims.append(s)
            #docsSims.append(sims)
            #docsSims.append((max(sims),min(sims),float(sum(sims))/len(sims)))
            if sims:
                #docsSims.append(min(sims))
                docsSims.append(float(sum(sims))/len(sims))
        #th = min(docsSims)
        relevanceth = float(sum(docsSims))/len(docsSims)
        self.relevanceth = round(relevanceth,self.roundPrec)
        print self.relevanceth
            
            #self.classifier = VSMClassifier(vocab_filtered_dict,th,newDocsBOW)
            #classifierFile = open(vsmClassifierFileName,"wb")
            #pickle.dump(self.classifier,classifierFile)
            #classifierFile.close()
            #return th
    
    def cosSimAll(self, doc1,doc2):
        sim = 0
        for k in doc1:
            #if k in doc2:
            a = (1 + math.log(doc1[k]))
            b = (1+math.log(doc2[k]))
            sim +=  a * b 
        
        if sim > 0:
            doc1s = [1+math.log(doc1[k]) for k in doc1]
            doc2s = [1+math.log(doc2[k]) for k in doc2]
            sim = float(sim)/(getScalar(doc1s) * getScalar(doc2s))
            
        else:
            sim = 0
        return sim
    
    def cosSim(self,doc2):
        sim = 0
        #for k in doc1:
        for k in self.vocabDic:
            if k in doc2:
                #a = (1 + math.log(self.topVocabDic[k]))
                #b = (1+math.log(doc2[k]))
                a = self.vocabDic[k]
                b = doc2[k]
                sim +=  a * b 
        
        if sim > 0:
            #doc1s = [1+math.log(doc1[k]) for k in doc1]
            
            #doc2s = [1+math.log(doc2[k]) for k in doc2]
            doc2s = [doc2[k] for k in doc2]
            #sim = float(sim)/(getScalar(doc1s) * getScalar(doc2s))
            sim = float(sim)/(self.vocabScalar * getScalar(doc2s))
            
        else:
            sim = 0
        return sim
    
    def calculate_score(self, doc,mode='U'):
            
        sims=[]
        docWords = getTokens(doc)
        docTF = getFreq(docWords)
        try:
            maxFreq = float(max(docTF.values()))
        except:
            print sys.exc_info()
        ndTF = {}
        for d in docTF:
            ndTF[d] = docTF[d] / maxFreq
         
        ndocTF = dict.fromkeys(self.vocabDic)
        for k in ndocTF:
            if k in ndTF:
                ndocTF[k] = ndTF[k]
            else:
                ndocTF[k] = 0#1/math.e
        doc1s = ndocTF.values()
        doc1_s = getScalar(doc1s)
        for ind,dTF in enumerate(self.docs):
            #doc1s = [1+math.log(ndocTF[k]) for k in ndocTF]
            doc2s = dTF.values()
            #doc2s = [1+math.log(dTF[k]) for k in dTF]
            s = 0
            for i in range(len(doc1s)):
                s += doc1s[i] * doc2s[i]
            #s = float(s)/ (doc1_s * getScalar(doc2s))
            #try:
            if s > 0:
                s = float(s)/ (doc1_s * self.docsScalar[ind])
            #except:
                #print sys.exc_info()
            #s =  sum(doc1s * doc2s)
            sims.append(s)
        #sim = max(sims)
        sim = float(sum(sims))/len(sims)
        sim = round(sim,self.roundPrec)
        if sim >= self.relevanceth:
            return [1,sim]
        elif (self.relevanceth - sim) <= self.error:
            return [1,sim]
        else:
            return [0,sim]
    
    def calculate_score_AllDocs_old(self, doc):
        sims=[]
        docWords = getTokens(doc)
        docTF = getFreq(docWords)
        ndocTF = dict.fromkeys(self.topVocabDic)
        for k in ndocTF:
            if k in docTF:
                ndocTF[k] = docTF[k]
            else:
                ndocTF[k] = 1/math.e
        for dTF in self.docsTF:
            s = self.cosSim(ndocTF, dTF)
            sims.append(s)
        sim = max(sims)
        if sim >= self.relevanceth:
            return [1,sim]
        else:
            return [0,sim]
    
    def calculate_score_one(self, doc):
        #sims=[]
        docWords = getTokens(doc)
        docTF = getFreq(docWords)
        sim = self.cosSim( docTF)
        
        if sim >= self.relevanceth:
            return [1,sim]
        else:
            return [0,sim]
    
    def calculate_score_old(self, doc):
        #sims=[]
        docWords = getTokens(doc)
        docTF = getFreq(docWords)
        ndocTF = dict.fromkeys(self.topVocabDic)
        
        
        for k in ndocTF:
            if k in docTF:
                ndocTF[k] = docTF[k]
            else:
                ndocTF[k] = 1/math.e
        sim = self.cosSim(self.topVocabDic, ndocTF)
        '''
        for dTF in self.docsTF:
            s = self.cosSim(ndocTF, dTF)
            sims.append(s)
        sim = max(sims)
        '''
        if sim >= self.relevanceth:
            return [1,sim]
        else:
            return [0,sim]

'''
def train_SaveClassifier(posURLs,negURLs,classifierFileName):
    #posURLs = readFileLines(posURLsFile)
    #negURLs = readFileLines(negURLsFile)
    
    #random.shuffle(negURLs)
    
    posDocs = getWebpageText(posURLs)
    posDocs = [d['title'] + " " + d['text'] for d in posDocs if d]
    
    #negURLsList = []
    negDocsList = []
    for n in negURLs:
        negDocsList.append(getWebpageText(n))
    #negDocs = getWebpageText(negURLs)
    #negDocs = getWebpageText(negURLsList)
    
    negTraining = []
    negTesting =[]
    for nu in negDocsList:
        ns = int(len(nu)*0.7)
        negTraining.extend(nu[:ns])
        negTesting.extend(nu[ns:])
    #print len(negTraining)
    #print len(negTesting)
    negTraining = [d['title'] + " " + d['text'] for d in negTraining if d]
    negTesting = [d['title'] + " " + d['text'] for d in negTesting if d]
    
    posLen = len(posDocs)
    print posLen
    negLen = len(negTraining) + len(negTesting)
    print negLen
    posLabels = [1]* posLen
    #negLabels = [0]*negLen 
    posSep = int(posLen*0.7)
    #negSep = int(negLen*0.7)
    
    trainingDocs = posDocs[:posSep] + negTraining
    #trainingLabels = posLabels[:posSep] + negLabels[:negSep]
    trainingLabels = posLabels[:posSep] + [0]*len(negTraining)
    trainingSet = zip(trainingDocs,trainingLabels)
    random.shuffle(trainingSet)
    
    testDocs = posDocs[posSep:] + negTesting
    #test_labels=posLabels[posSep:] + negLabels[negSep:]
    test_labels=posLabels[posSep:] + [0]*len(negTesting)
    
    testSet = zip(testDocs,test_labels)
    random.shuffle(testSet)
    
    
    #trainingDocs = posDocs[:posSep] + negDocs[:negSep]
    
    #trainingLabels = posLabels[:posSep] + negLabels[:negSep]
    
    #testDocs = posDocs[posSep:] + negDocs[negSep:]
    #test_labels=posLabels[posSep:] + negLabels[negSep:]
    
    classifier = NaiveBayesClassifier()
    
    trainingLabels = [v for _,v in trainingSet]
    trainingDocs = [k for k,_ in trainingSet]
    
    trainingLabelsArr = np.array(trainingLabels)
    classifier.trainClassifier(trainingDocs,trainingLabelsArr)
    
    print classifier.score(trainingDocs, trainingLabelsArr)
    print metrics.classification_report(trainingLabelsArr, classifier.predicted)
    
    test_labels = [v for _,v in testSet]
    testDocs = [v for v,_ in testSet]
    
    test_labelsArr = np.array(test_labels)
    print classifier.score(testDocs, test_labelsArr)
    
    print metrics.classification_report(test_labelsArr, classifier.predicted)
    classifierFile = open(classifierFileName,"wb")
    pickle.dump(classifier,classifierFile)
    classifierFile.close()
    return classifier
'''

def getTweets(jsonFileName):
    f = open(jsonFileName,'r')
    texts = {}
    tweets = []
    for line in f:
        l = line.strip()
        if l:
            try:
                s = json.loads(l)
                tweets.append(s)
                if 'id_str' in s:
                    #if s['id_str'] in texts:
                    #	continue
                    if 'text' in s:
                        texts[s['id_str']] = s['text']
            except Exception as e: 
                print(e)
                print l
    f.close()
    print len(texts)
    print len(tweets)
    return texts

def extractShortURLsFreqDic(tweetsText):
    shortURLsDic = {}
    regExp = "(?P<url>https?://[a-zA-Z0-9\./-]+)"
    for t in tweetsText:
        #t = t[0]
        url_li = re.findall(regExp, t)  # find all short urls in a single tweet
        while (len(url_li) > 0): 
            surl = url_li.pop()
            '''
            i = surl.rfind("/")
            if i+1 >= len(surl):
                continue
            p = surl[i+1:]
            if len(p) < 10:
                continue
            '''
            while surl.endswith("."):
                surl = surl[:-1]
            if surl in shortURLsDic:
                shortURLsDic[surl] += 1
            else:
                shortURLsDic[surl]=1
            #shortURLsList.append()
    return shortURLsDic#shortURLsList

def getOrigLongURLs(shortURLs):
    expandedURLs = {}
        #freqShortURLs = freqShortURLs[:2000]
    i=0
    e=0
    
    for surl,v in shortURLs:
        try:
            with closing(requests.get(surl,timeout=10, stream=True, verify=False)) as r:
                #print r.status_code
                if r.status_code == requests.codes.ok:
                    #print surl
                    ori_url =r.url
                    if ori_url in expandedURLs:
                        expandedURLs[ori_url].append((surl,v))
                    else:
                        expandedURLs[ori_url] = [(surl,v)]
                    #expandedURLs.append(ori_url)
                    i  =i+1
                elif r.url != surl:
                    ori_url =r.url
                    if ori_url in expandedURLs:
                        expandedURLs[ori_url].append((surl,v))
                    else:
                        expandedURLs[ori_url] = [(surl,v)]
                    i  =i+1
                elif r.request.url != surl:
                    ori_url =r.request.url
                    if ori_url in expandedURLs:
                        expandedURLs[ori_url].append((surl,v))
                    else:
                        expandedURLs[ori_url] = [(surl,v)]
                    i  =i+1
                else:
                    e = e+1    
                    print r.status_code , surl, r.url, r.request.url
                    #expandedURLs.append("")
        except :
            print sys.exc_info()[0], surl
            #expandedURLs.append("")
            e = e +1
    print "urls expanded: ", i
    print "bad Urls: ",e
    return expandedURLs



def getSourceFreqDic(origLongURLsFreqDic):
    sourcesFreqDic = {}
    for k,v in origLongURLsFreqDic.items():
        su = sum([l for s,l in v])
        dom = getDomain(k)
        if dom in sourcesFreqDic:
            sourcesFreqDic[dom].append(su)
        else:
            sourcesFreqDic[dom] = [su]
            
    return sourcesFreqDic


def saveSourcesFreqDic(sourcesFreqDic,filename):
    t = [(k, len(v),sum(v)) for k,v in sourcesFreqDic.items()]
    st = getSorted(t, 1)
    f= open(filename,'w')
    #for k,v in sourcesFreqDic.items():
    for k,l,s in st:
        #f.write(k +"," + str(len(v))+"," + str(sum(v))+"\n")
        f.write(k +"," + str(l)+"," + str(s)+"\n")
    f.close()

def getDomain(url):
    domain = ""
    ind = url.find("//")
    if ind != -1 :
        domain = url[ind+2:]
        ind = domain.find("/")
        domain = domain[:ind]
    return domain

def saveObjUsingPickle(obj,fileName):
    out_s = open(fileName, 'wb')
    try:
        # Write to the stream
        pickle.dump(obj, out_s)
    finally:
        out_s.close() 

def train_SaveClassifierFolder(posURLs,negURLs,classifierFileName):
        
    posDocs = getWebpageText(posURLs)
    posDocs = [d['title'] + " " + d['text'] for d in posDocs if d]
    
    negDocsList = []
    for n in negURLs:
        negDocsList.append(getWebpageText(n))
    
    negTraining = []
    negTesting =[]
    for nu in negDocsList:
        ns = int(len(nu)*0.7)
        negTraining.extend(nu[:ns])
        negTesting.extend(nu[ns:])
    
    negTraining = [d['title'] + " " + d['text'] for d in negTraining if d]
    negTesting = [d['title'] + " " + d['text'] for d in negTesting if d]
    
    
    posLen = len(posDocs)
    posSep = int(0.7*posLen)
    posTraining = posDocs[:posSep]
    posTest = posDocs[posSep:]
    
    trainingDocs = posTraining + negTraining
    trainingLabels = [1]* len(posTraining) + [0]*len(negTraining)
    
    testingDocs = posTest + negTesting
    testingLabels = [1]*len(posTest) + [0]*len(negTesting)
        
    classifier = NaiveBayesClassifier()
    #classifier = SVMClassifier()
    
    trainingLabelsArr = np.array(trainingLabels)
    classifier.trainClassifier(trainingDocs,trainingLabelsArr)
    
    print classifier.score(trainingDocs, trainingLabelsArr)
    print metrics.classification_report(trainingLabelsArr, classifier.predicted)
       
    test_labelsArr = np.array(testingLabels)
    print classifier.score(testingDocs, test_labelsArr)
    
    
    print metrics.classification_report(test_labelsArr, classifier.predicted)
    classifierFile = open(classifierFileName,"wb")
    pickle.dump(classifier,classifierFile)
    classifierFile.close()
    return classifier

def train_SaveOneClassClassifier(posURLs,negURLs,classifierFileName):
        
    #posDocs = getWebpageText(posURLs)
    posDocs = getWebpageText_NoURLs(posURLs)
    posDocs = [d['text'] for d in posDocs if d]
    
    #negDocs = getWebpageText(negURLs)
    negDocs = getWebpageText_NoURLs(negURLs)
    negDocs = [d['text'] for d in negDocs if d]
    
    
    posLen = len(posDocs)
    posSep = int(0.7*posLen)
    posTraining = posDocs[:posSep]
    posTest = posDocs[posSep:]
    
    negLen = len(negDocs)
    negSep = int(0.7*negLen)
    #negTraining = negDocs[:negSep]
    negTest = negDocs[negSep:]
    
    trainingDocs = posTraining #+ negTraining
    trainingLabels = [1]* len(posTraining) #+ [0]*len(negTraining)
    
    testingDocs = posTest + negTest
    testingLabels = [1]*len(posTest) + [-1]*len(negTest)
        
    classifier = OneClassClassifier()
    #classifier = NaiveBayesClassifier()
    #classifier = SVMClassifier()
    
    trainingLabelsArr = np.array(trainingLabels)
    classifier.trainClassifier(trainingDocs,trainingLabelsArr)
    #print trainingLabelsArr
    print classifier.score(trainingDocs, trainingLabelsArr)
    print metrics.classification_report(trainingLabelsArr, classifier.predicted)
       
    test_labelsArr = np.array(testingLabels)
    print classifier.score(testingDocs, test_labelsArr)
    print metrics.classification_report(test_labelsArr, classifier.predicted)
    
    #print classifier.classifier.feature_log_prob_
    #print classifier.classifier.coef_
    
    classifierFile = open(classifierFileName,"wb")
    pickle.dump(classifier,classifierFile)
    classifierFile.close()
    return classifier

def train_SaveClassifier(posURLs,negURLs,classifierFileName):
        
    #posDocs = getWebpageText(posURLs)
    posDocs = getWebpageText_NoURLs(posURLs)
    posDocs = [d['text'] for d in posDocs if d]
    
    #negDocs = getWebpageText(negURLs)
    negDocs = getWebpageText_NoURLs(negURLs)
    negDocs = [d['text'] for d in negDocs if d]
    
    #negTraining = [d['title'] + " " + d['text'] for d in negTraining if d]
    #negTesting = [d['title'] + " " + d['text'] for d in negTesting if d]
    
    posLen = len(posDocs)
    posSep = int(0.7*posLen)
    posTraining = posDocs[:posSep]
    posTest = posDocs[posSep:]
    
    negLen = len(negDocs)
    negSep = int(0.7*negLen)
    negTraining = negDocs[:negSep]
    negTest = negDocs[negSep:]
    
    trainingDocs = posTraining + negTraining
    trainingLabels = [1]* len(posTraining) + [0]*len(negTraining)
    
    testingDocs = posTest + negTest
    testingLabels = [1]*len(posTest) + [0]*len(negTest)
        
    classifier = NaiveBayesClassifier()
    #classifier = SVMClassifier()
    
    trainingLabelsArr = np.array(trainingLabels)
    classifier.trainClassifier(trainingDocs,trainingLabelsArr)
    
    print classifier.score(trainingDocs, trainingLabelsArr)
    print metrics.classification_report(trainingLabelsArr, classifier.predicted)
       
    test_labelsArr = np.array(testingLabels)
    print classifier.score(testingDocs, test_labelsArr)
    print metrics.classification_report(test_labelsArr, classifier.predicted)
    
    #print classifier.classifier.feature_log_prob_
    #print classifier.classifier.coef_
    
    classifierFile = open(classifierFileName,"wb")
    pickle.dump(classifier,classifierFile)
    classifierFile.close()
    return classifier

def train_SaveClassifierRandom(posURLs,negURLs,classifierFileName):
        
    posDocs = getWebpageText(posURLs)
    posDocs = [d['title'] + " " + d['text'] for d in posDocs if d]
    
    negDocs = getWebpageText(negURLs)
    negDocs = [d['title'] + " " + d['text'] for d in negDocs if d]
    
    posLen = len(posDocs)
    print posLen
    negLen = len(negDocs)
    print negLen
    posLabels = [1]* posLen
    negLabels = [0]*negLen 
    
    
    
    dataSetDocs = posDocs + negDocs
    dataSetLabels = posLabels + negLabels
    
    dataDocLabels = zip(dataSetDocs,dataSetLabels)
    random.shuffle(dataDocLabels)
    
    sep = int(0.7*len(dataDocLabels))
    trainingDocLabels = dataDocLabels[:sep]
    testDocLabels = dataDocLabels[sep:]
    
    trainingLabels = [v for _,v in trainingDocLabels]
    trainingDocs = [k for k,_ in trainingDocLabels]
    
    testDocs = [d for d,_ in testDocLabels]
    test_labels=[l for _,l in testDocLabels]
    
    classifier = NaiveBayesClassifier()
    
    trainingLabelsArr = np.array(trainingLabels)
    classifier.trainClassifier(trainingDocs,trainingLabelsArr)
    
    print classifier.score(trainingDocs, trainingLabelsArr)
    print metrics.classification_report(trainingLabelsArr, classifier.predicted)
       
    test_labelsArr = np.array(test_labels)
    print classifier.score(testDocs, test_labelsArr)
    
    
    print metrics.classification_report(test_labelsArr, classifier.predicted)
    classifierFile = open(classifierFileName,"wb")
    pickle.dump(classifier,classifierFile)
    classifierFile.close()
    return classifier

def getScalar(doc_tfidf):
        total = 0
        for i in range(len(doc_tfidf)):
            total += doc_tfidf[i] * doc_tfidf[i]
        #for k in doc_tfidf:
        #    total += doc_tfidf[k] * doc_tfidf[k]
        return math.sqrt(total)

def getEntities(texts):
        
        if type(texts) != type([]):
            texts = [texts]   
        """
        Run the Stanford NER in server mode using the following command:
        java -mx1000m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer -loadClassifier classifiers/english.muc.7class.distsim.crf.ser.gz -port 8000 -outputFormat inlineXML
        """
        
        tagger = ner.SocketNER(host='localhost',port=8000)
        entities = []
        for t in texts:
            ents = tagger.get_entities(t)
            entities.append(ents)
        return entities

def isListsDisjoint(l1,l2):
    s1 = set(l1)
    s2 = set(l2)
    return s1.isdisjoint(s2)

def getIntersection(l1,l2):
    s1 = set(l1)
    s2 = set(l2)
    return s1.intersection(s2)

def readFileLines(filename):
    f = open(filename,"r")
    lines = f.readlines()
    lines = [l.strip() for l in lines]
    return lines

def saveListToFile(l, filename):
    f = open(filename,"w")
    li = [str(il) for il in l]
    liStr = '\n'.join(li)
    f.write(liStr)
    f.close()
    #return lines

def getSorted(tupleList,fieldIndex):
    sorted_list = sorted(tupleList, key=itemgetter(fieldIndex), reverse=True)
    return sorted_list

def filterLinks(element):
    if element.parent.name == 'a':
        return False

    p = element.parent
    if p.parent.name == 'a':
        return False

    return True

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head']:
        return False
    return True

def getStemmedWords(words):
    stemmer = PorterStemmer()
    stemmedWords = []
    for w in words:
        stemmedWords.append(stemmer.stem(w))
    return stemmedWords

def getDocTokens(docText):
    stemmer = PorterStemmer()
    tokenizer = WordPunctTokenizer()
    docTokens = tokenizer.tokenize(docText)
    
    allTokens_2 = [t.lower() for t in docTokens if len(t)>2]
    allTokens_an = [t2 for t2 in allTokens_2 if t2.isalnum()]
    allTokens_stw = [t3 for t3 in allTokens_an if t3 not in stopwordsList]
    allTokens_stem = [stemmer.stem(word) for word in allTokens_stw]
    final = [t for t in allTokens_stem if t not in stopwordsList]
    return final

def getTokens(texts):
    #global corpusTokens
    #global docsTokens
    stemmer = PorterStemmer()
    tokenizer = WordPunctTokenizer()
    
    allTokens=[]
    #tokens=[]
    if type(texts) != type([]):
        texts = [texts]
    for s in texts:
        #toks = nltk.word_tokenize(s.lower())
        toks = tokenizer.tokenize(s)
        allTokens.extend(toks)
        #corpusTokens.extend(toks)
        #docsTokens.append(toks)
   
    allTokens_2 = [t.lower() for t in allTokens if len(t)>2]
    allTokens_an = [t2 for t2 in allTokens_2 if t2.isalnum()]
    allTokens_stw = [t3 for t3 in allTokens_an if t3 not in stopwordsList]
    allTokens_stem = [stemmer.stem(word) for word in allTokens_stw]
    final = [t for t in allTokens_stem if t not in stopwordsList]
    return final

def getFreq(tokens):
    toks = [t.lower() for t in tokens]
    return nltk.FreqDist(toks)

def getSentences(textList =[]):
    #stopwordsList = stopwords.words('english')
    #stopwordsList.extend(["news","people","said"])
    if type(textList) != type([]):
        textList = [textList]
    sents = []
    for text in textList:
        sentences = nltk.sent_tokenize(text)
        newSents = []
        for s in sentences:
			if len(re.findall(r'.\..',s))>0:
				ns = re.sub(r'(.)\.(.)',r'\1. \2',s)
				newSents.extend(nltk.sent_tokenize(ns))
			else:
				newSents.append(s)

        
        newSents = [s for sent in newSents for s in sent.split("\n") if len(s) > 3]
        cleanSents = [sent.strip() for sent in newSents if len(sent.split()) > 3]
        sents.extend(cleanSents)
    return sents

def _cleanSentences(sents):
    sentences = [s for sent in sents for s in sent.split("\n") if len(s) > 3]
    cleanSents = [sent.strip() for sent in sentences if len(sent.split()) > 3]
    return cleanSents

def getUniqueEntities(sents):
    uniqueEntities = {}
    allEnts = getEntities(sents)
    for ent in allEnts:
        for k in ent:
            if k in uniqueEntities:
                uniqueEntities[k].extend(ent[k])
            else:
                uniqueEntities[k] = []
                uniqueEntities[k].extend(ent[k])
    #now you have a huge one dic with different entities as keys and list of values for each key
    # we need to get the unique values in each list
    entitiesCount= {}
    
    locDateEntities = {}
    for k in uniqueEntities:
        if k in ["LOCATION","DATE"]:
            #l = uniqueEntities[k]
            #s = set(l)
            #locDateEntities[k] = list(s)
            locDateEntities[k] = [].extend(uniqueEntities[k])
    for k in locDateEntities:
    	for ent in locDateEntities[k]:
    		if ent in entitiesCount:
    			entitiesCount[ent]+=1
    		else:
    			entitiesCount[ent]=1
    
    return locDateEntities

def getUniqueEntitiesWords(entities):
    words = []
    for k in entities:
        words.extend(entities[k])
    entitiesWords = []
    for w in words:
        p = w.split()
        if len(p)>1:
            entitiesWords.extend(p)
        else:
            entitiesWords.append(w)
    entitiesWords = [ew.lower() for ew in entitiesWords]
    return entitiesWords

def getPOS(words):
    tags = nltk.pos_tag(words)
    return tags

def getFilteredImptWords(texts,freqWords):
	#nltk.pos_tag(text)
    impWordsTuples = getIndicativeWords(texts,freqWords)
    impWordsList = [w[0] for w in impWordsTuples]
    
    wordsTags = nltk.pos_tag(impWordsList)
    nvWords = [w[0] for w in wordsTags if w[1].startswith('N') or w[1].startswith('V')]
    wordsDic = dict(impWordsTuples)
    nvWordsTuple = [(w,wordsDic[w]) for w in nvWords]
    return nvWordsTuple
    

def getLDATopics(documents):
	texts = []
	for doc in documents:
		docToks = getTokens(doc)
		texts.append(docToks)
		
		
	dictionary = corpora.Dictionary(texts)
	corpus = [dictionary.doc2bow(text) for text in texts]

	notopics = 3
	lda = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=notopics)


	outputTopics = []
	for i in range(0, lda.num_topics):
		
		#outputTopics.append( "Topic"+ str(i+1) + ":"+ lda.print_topic(i))
		t = lda.show_topic(i)
		#print type(t)
		t = [w for _,w in t]
		#for tu in t:
		#	print tu[1]
		outputTopics.append( "Topic"+ str(i+1) + ":"+ ", ".join(t))
	return "<br>".join(outputTopics)

def extractMainArticle(html):
    p = Document(html)
    readable_article = p.summary()
    readable_title = p.short_title()
    
    soup = BeautifulSoup(readable_article)
    text_nodes = soup.findAll(text=True)
    text = ''.join(text_nodes)
    
    #text = readable_title + " " + text
    #return text
    
    wtext = {"title":readable_title, "text": text}
    return wtext

def extractTextFromHTML(page):
    try:
        soup = BeautifulSoup(page)
        title = ""
        text = ""
        if soup.title:
            if soup.title.string:
                title = soup.title.string
        
        comments = soup.findAll(text=lambda text:isinstance(text,Comment))
        [comment.extract() for comment in comments]

        
        text_nodes = soup.findAll(text=True)
        #text_nodes_noLinks = soup.findAll(text=True)
        visible_text = filter(visible, text_nodes)
        text = '\n'.join(visible_text)
        
        if text.strip():
            text = title +" " + text
            wtext = {"text":text,"title":title}
        else:
            wtext = {}
    except:
        print sys.exc_info()
        #text = ""
        wtext = {}
    #return text
    return wtext
'''
def getWebpage(url):
    try:
        r = requests.get(url.strip(),timeout=10,verify=False,headers=headers)            
        if r.status_code == requests.codes.ok:
            page = r.content
            #text = extractTextFromHTML(page)
            #text['html']= page
        else:
            page = ''
    except:
        print sys.exc_info()
        #text = ""
        page = ''
    return page
'''
def extractTextFromHTML_noURLs(page):
    try:
        soup = BeautifulSoup(page)
        title = ""
        text = ""
        if soup.title:
            if soup.title.string:
                title = soup.title.string
        
        comments = soup.findAll(text=lambda text:isinstance(text,Comment))
        [comment.extract() for comment in comments]
        '''
        links = soup.findAll('a')
        for tn in links:
            if tn.name == 'a':
                tn.extract()
        '''
        text_nodes = soup.findAll(text=True)
        #text_nodes_noLinks = soup.findAll(text=True)
        visible_text = filter(visible, text_nodes)
        text_noURLs = filter(filterLinks,visible_text)
        #text = ''.join(visible_text)
        text = '\n'.join(text_noURLs)
        if text.strip():
            text = title +" " + text
            wtext = {"text":text,"title":title}
        else:
            wtext = {}
    except:
        print sys.exc_info()
        #text = ""
        wtext = {}
    #return text
    return wtext

def getWebpage(url):
    try:
        r = requests.get(url.strip(),timeout=10,verify=False,headers=headers)            
        if r.status_code == requests.codes.ok:
            page = r.content
            #text = extractTextFromHTML(page)
            #text['html']= page
        else:
            page = ''
    except:
        print sys.exc_info()
        #text = ""
        page = ''
    return page
'''
def extractTextFromHTML_noURLs(page):
    try:
        soup = BeautifulSoup(page)
        title = ""
        text = ""
        if soup.title:
            if soup.title.string:
                title = soup.title.string
        
        comments = soup.findAll(text=lambda text:isinstance(text,Comment))
        [comment.extract() for comment in comments]
        
        text_nodes = soup.findAll(text=True)
        #text_nodes_noLinks = soup.findAll(text=True)
        visible_text = filter(visible, text_nodes)
        text_noURLs = filter(filterLinks,visible_text)
        #text = ''.join(visible_text)
        text = ' '.join(text_noURLs)
        
        text = title + text
        wtext = {"text":text,"title":title}
    except:
        print sys.exc_info()
        #text = ""
        wtext = {}
    #return text
    return wtext
'''
def getWebpageText(URLs = []):
    webpagesText = []
    if type(URLs) != type([]):
        URLs = [URLs]
    for url in URLs:
        try:
            r = requests.get(url.strip(),timeout=10,verify=False,headers=headers)            
            if r.status_code == requests.codes.ok:
                page = r.content
                text = extractTextFromHTML(page)
                text['html']= page
            else:
                text = {}
        except:
            print sys.exc_info()
            #text = ""
            text = {}
        webpagesText.append(text)
    return webpagesText


def getWebpageText_NoURLs(URLs = []):
    webpagesText = []
    if type(URLs) != type([]):
        URLs = [URLs]
    for url in URLs:
        try:
            r = requests.get(url.strip(),timeout=10,verify=False,headers=headers)            
            if r.status_code == requests.codes.ok:
                page = r.content
                text = extractTextFromHTML_noURLs(page)
                if text:
                    text['html']= page
            else:
                text = {}
        except:
            print sys.exc_info()
            #text = ""
            text = {}
        webpagesText.append(text)
    return webpagesText

'''
def saveObjUsingPickle(obj,fileName):
    out_s = open(fileName, 'wb')
    try:
        # Write to the stream
        pickle.dump(obj, out_s)
    finally:
        out_s.close() 
'''

#Get Frequent Tokens
#moved
def getFreqTokens(texts):
	tokens = getTokens(texts)
	f = getFreq(tokens)
	tokensFreqs = f.items()
	sortedTokensFreqs = getSorted(tokensFreqs,1)
	return sortedTokensFreqs

def getIndicativeWords(texts,tokensFreqs):
	#global allSents
	#Get Indicative tokens
	toksTFDF = getTokensTFDF(texts,tokensFreqs)
	
	#sortedToksTFDF = sorted(filteredToksTFDF, key=lambda x: x[1][0]*x[1][1], reverse=True)
	sortedToksTFDF = sorted(toksTFDF.items(), key=lambda x: x[1][0]*x[1][1], reverse=True)
	return sortedToksTFDF
	
def getIndicativeSents(texts,sortedToksTFDF,topK,intersectionTh):
	# Get Indicative Sentences
	topToksTuples = sortedToksTFDF[:topK]
	topToks = [k for k,_ in topToksTuples]
	#allImptSents = []
	allSents = getSentences(texts)
	
	#impSentsF = {}
	impSents ={}
	for sent in allSents:
		if sent not in impSents:
			sentToks = getTokens(sent)
			if len(sentToks) > 100:
				continue
			intersect = getIntersection(topToks, sentToks)
			if len(intersect) >= intersectionTh:
				impSents[sent] = len(intersect)
				#if sent not in impSentsF:
				#	impSentsF[sent] = len(intersect)
			#allImptSents.append(impSents)
	
	sortedImptSents = getSorted(impSents.items(),1)
	return sortedImptSents



def getEventModelInsts(sortedImptSents):
    '''    
    eventModelInstances = []
    for sent in sortedImptSents:
        sentEnts = getEntities(sent[0])[0]
        eventModelInstances.append(sentEnts)
    '''
    imptSents = [s[0] for s in sortedImptSents]
    eventModelInstances = getEntities(imptSents)
    impEventModelInstances = []
    for emi,s in zip(eventModelInstances,sortedImptSents):
        if emi.has_key('LOCATION'):
            emi['Topic'] = s[1]
            impEventModelInstances.append(emi)
            
        if emi.has_key('DATE'):
            if 'Topic' not in emi:
                emi['Topic'] = s[1]
            impEventModelInstances.append(emi)
            
    #return eventModelInstances
    return impEventModelInstances

'''
def getTokensTFDF(texts):
	tokensTF = []
	#allTokensList=[]
	allTokens = []
	allSents = []
	for t in texts:
		sents = getSentences(t)
		toks = getTokens(sents)
		toksFreqs = getFreq(toks)
		allTokens.extend(toksFreqs.keys())
		#allTokensList.append(toks)
		allSents.append(sents)
		sortedToksFreqs = getSorted(toksFreqs.items(), 1)
		tokensTF.append(sortedToksFreqs)
	tokensDF = getFreq(allTokens).items()
	tokensTFDF = {}
	for t in tokensTF:
		for tok in t:
			if tok[0] in tokensTFDF:
				tokensTFDF[tok[0]] += tok[1]
			else:
				tokensTFDF[tok[0]] = tok[1]
	for t in tokensDF:
		tokensTFDF[t[0]] = (tokensTFDF[t[0]],t[1])
	
	return tokensTFDF,allSents
'''	

def getTokensTFDF(texts,termFreq):
    docsTokens=[]
    for t in texts:
        toks = getTokens(t)
        docsTokens.append(toks)
    #tokensTF = dict(getFreqTokens(texts))
    tokensTF = dict(termFreq)
    tokensDF = {}
    for te in tokensTF:
        
        df = sum([1 for t in docsTokens if te in t])
        tokensDF[te] = df
    
    tokensTFDF = {}
    for t in tokensDF:
        tokensTFDF[t] = (tokensTF[t],tokensDF[t])
    
    return tokensTFDF

def parseLogFileForHtml(log_file):
    htmlList = []
    
    with open(log_file, 'r+b') as f:
        for line in f:
            splitext = line.split('\t')
            if len(splitext) >= 9:
                content_type = splitext[6]
                if content_type.find("text/html") == 0:
                    htmlList.append({"file":splitext[7], "wayback_url":splitext[8], "url":splitext[5]})
                
    return htmlList

# Extracts text from a given HTML file and indexes it into the Solr Instance
def extractText(html_files):
    textFiles = []
    docsURLs = []
    titles = {}
    for f in html_files:
        html_file = f["file"].strip()
        file_url = f["url"].strip()
        wayback_url = f["wayback_url"].strip()

        try:   
        	html_fileh = open(html_file, "r")
        	html_string = html_fileh.read()

        except:
        	print "Error reading"
        	#logging.exception('')
        
        if len(html_string) < 1:
            print "error parsing html file " + str(html_file)
            continue
        try:   
            d = extractTextFromHTML(html_string)

        except:
            print "Error: Cannot parse HTML from file: " + html_file
            print sys.exc_info()
            #logging.exception('')
            continue    
        
        
        
        title = d['title']
        if title and title in titles:
            #print "Title already exists"
            continue
        else:
            titles[title]=1
        html_body = d['text']
        textFiles.append(html_body)
        docsURLs.append(file_url)
    return textFiles,docsURLs
    

#def main(argv):
def expandWarcFile(warcFile):
#     if (len(argv) < 1):
#         print >> sys.stderr, "usage: processWarcDir.py -d <directory> -i <collection_id> -e <event> -t <event_type>"
#         sys.exit()
#         
#     if (argv[0] == "-h" or  len(argv) < 4):
#         print >> sys.stderr, "usage: processWarcDir.py -d <directory> -i <collection_id> -e <event> -t <event_type>"
#         sys.exit()
    
    
    rootdir = os.path.dirname(warcFile)
    filename = os.path.basename(warcFile)
    filePath =warcFile
    if filename.endswith(".warc") or filename.endswith(".warc.gz"):# or filename.endswith(".arc.gz"):
		# processWarcFile(filePath, collection_id, event, event_type)
		splitext = filePath.split('.')
		output_dir = splitext[0] + "/"
		
		log_file = os.path.join(output_dir, filePath[filePath.rfind("/")+1:] + '.index.txt')
		
		# output_file = output_dir + filePath.split("/")[1] + ".index.txt"
		if os.path.exists(output_dir) == False:                    
		
			os.makedirs(output_dir)

			# unpackWarcAndRetrieveHtml(filePath, collection_id, event, event_type)
			# output_dir = filePath.split(".")[0] + "/"
			default_name = 'crawlerdefault'
			wayback = "http://wayback.archive-it.org/"
			collisions = 0
				
			#log_file = os.path.join(output_dir, filePath[filePath.rfind("/")+1:] + '.index.txt')
			
			log_fileh = open(log_file, 'w+b')
			warcunpack_ia.log_headers(log_fileh)
		
			try:
				with closing(ArchiveRecord.open_archive(filename=filePath, gzip="auto")) as fh:
					collisions += warcunpack_ia.unpack_records(filePath, fh, output_dir, default_name, log_fileh, wayback)
		
			except StandardError, e:
				print "exception in handling", filePath, e
				return
		else:
			print "Directory Already Exists"
		
			#print "Warc unpack finished"
		
		html_files = parseLogFileForHtml(log_file)
		#print "Log file parsed for html files pathes"
		#print len(html_files)
		
		# for i in html_files:
			# extractTextAndIndexToSolr(i["file"], i["url"], i["wayback_url"], collection_id, event, event_type)
		tf,urls = extractText(html_files)
		#print "extracting Text finished"
		return tf,urls