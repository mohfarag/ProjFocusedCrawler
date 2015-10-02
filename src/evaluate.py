'''
Created on Mar 13, 2014

@author: mohamed
'''
from _collections import defaultdict
import sys
'''
#from SVMClassifier import SVMClassifier
from NBClassifier import NaiveBayesClassifier
import numpy as np
from sklearn import metrics
from Filter import downloadRawDocs
'''
from eventUtils import VSMClassifier, getWebpageText_NoURLs, getFreq, train_SaveClassifier, readFileLines,getTokens, getScalar,getSorted, train_SaveOneClassClassifier
import os
import math
import pickle
from document import Document
import codecs
'''
class VSMClassifier(object):
    def __init__(self, vocabDic,relevTh,docs):
        self.docs = docs
        self.relevanceth = relevTh
        self.vocabDic = vocabDic
        #doc1s = [1+math.log(self.topVocabDic[k]) for k in self.topVocabDic]
        self.docsScalar = []
        for d in docs:
            doc_s = d.values()
            self.docsScalar.append(getScalar(doc_s))
    
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
    
    def calculate_score(self, doc):
        sims=[]
        docWords = getTokens(doc)
        docTF = getFreq(docWords)
        maxFreq = float(max(docTF.values()))
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
            s = float(s)/ (doc1_s * self.docsScalar[ind])
            #s =  sum(doc1s * doc2s)
            sims.append(s)
        #sim = max(sims)
        sim = float(sum(sims))/len(sims)
        if sim >= self.relevanceth:
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
       
        if sim >= self.relevanceth:
            return [1,sim]
        else:
            return [0,sim]
'''    
    
class Evaluate(object):
    '''
    classdocs
    '''

    #def __init__(self,pages,posFile,negFile):
    '''
    def __init__(self):
        
        
        #saved = False
        #try:
        #classifierFile = open(classifierFileName,"rb")
        #self.classifier = pickle.load(classifierFile)
        #self.classifier = classifier
        #classifierFile.close()
            
        #except:
        #    self.classifier = train_SaveClassifier(posFile, negFile, classifierFileName)
            
    '''

    def buildClassifierFolder(self,posFile,negFolder,classifierFileName):
        #negURLsFile = 'negFile.txt'
        try:
            classifierFile = open(classifierFileName,"rb")
            self.classifier = pickle.load(classifierFile)
            classifierFile.close()
            
        except:
            posURLs = readFileLines(posFile)
            posLen = len(posURLs)
            negFiles = os.listdir(negFolder)
            negFiles = [os.path.join(negFolder,f) for f in negFiles if f.endswith(".txt")]
            #print negFiles
            negFilesURLs = [readFileLines(f) for f in negFiles]
            
            num = int(round(1.0* posLen/len(negFiles)))
            negURLs = []
            for nfu in negFilesURLs:
                #print len(nfu)
                if num < len(nfu):
                    #negURLs.extend(nfu[:num] )
                    negURLs.append(nfu[:num] )
                else:
                    #negURLs.extend(nfu )
                    negURLs.append(nfu )
            #print len(negURLs)
            #self.classifier = train_SaveClassifierRandom(posURLs, negURLs, classifierFileName)
            self.classifier = train_SaveClassifier(posURLs, negURLs, classifierFileName)
            #return cls

    def buildOneClassClassifier(self,posFile,negFile,classifierFileName):
        #negURLsFile = 'negFile.txt'
        try:
            classifierFile = open(classifierFileName,"rb")
            self.classifier = pickle.load(classifierFile)
            classifierFile.close()
            
        except:
            posURLs = readFileLines(posFile)
            negURLs = readFileLines(negFile)
            self.classifier = train_SaveOneClassClassifier(posURLs, negURLs, classifierFileName)
    
    def buildClassifier(self,posFile,negFile,classifierFileName):
        #negURLsFile = 'negFile.txt'
        try:
            classifierFile = open(classifierFileName,"rb")
            self.classifier = pickle.load(classifierFile)
            classifierFile.close()
            
        except:
            posURLs = readFileLines(posFile)
            negURLs = readFileLines(negFile)
            self.classifier = train_SaveClassifier(posURLs, negURLs, classifierFileName)
            #return cls
    '''
    def buildVSMClassifier(self,posFile,vsmClassifierFileName,leastDocFreq,lk):
        
        try:
            classifierFile = open(vsmClassifierFileName,"rb")
            self.classifier = pickle.load(classifierFile)
            classifierFile.close()
        except:
            docs = []
            
            f = open(posFile,'r')
            for url in f:
                url = url.strip()
                d = Document(url)
                if d and d.text:
                    docs.append(d)
            f.close()
            print len(docs)
            docsBOW = []
            vocabTFDic = defaultdict(list)
            maxFreqPerDocList = []
            for d in docs:
                docWords = d.getWords()
                #docLen = float(len(docWords))
                #print docLen
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
            
            vocab_filtered_dict = dict(voc_CollFreqSorted[:lk])
            
            #print len(vocab_filtered_dict)
            print vocab_filtered_dict
            # convert docs to BOW using new vocab
            newDocsBOW=[]
            for doc_bow in docsBOW:
                ndocBOW = {}
                for k in vocab_filtered_dict:
                    if k in doc_bow:
                        ndocBOW[k] = doc_bow[k]
                    else:
                        ndocBOW[k] = 0 #1/math.e
                newDocsBOW.append(ndocBOW)
            
            # Figure out similarity threshold using similarity between all docs
            newDocs_List = []
            for newdoc in newDocsBOW:
                newDocList = newdoc.values()
                newDocs_List.append(newDocList)
            docsSims = []
            for doc1s in newDocs_List:
                sims = []
                for doc2s in newDocs_List:
                    #s = self.cosSimAll(ndocTF, dTF)
                    #doc1s = [1+math.log(nd[k]) for k in nd]
                    #doc2s = [1+math.log(dTF[k]) for k in dTF]
                    s = 0
                    for i in range(len(doc1s)):
                        s += doc1s[i] * doc2s[i]
                    s = float(s)/ (getScalar(doc1s) * getScalar(doc2s))
                    #s =  sum(doc1s * doc2s)
                    sims.append(s)
                #docsSims.append(sims)
                #docsSims.append((max(sims),min(sims),float(sum(sims))/len(sims)))
                docsSims.append(min(sims))
                #docsSims.append(float(sum(sims))/len(sims))
            #th = min(docsSims)
            th = float(sum(docsSims))/len(docsSims)
            print th
                
            
            self.classifier = VSMClassifier(vocab_filtered_dict,th,newDocsBOW)
            classifierFile = open(vsmClassifierFileName,"wb")
            pickle.dump(self.classifier,classifierFile)
            classifierFile.close()
            return th
            
            # new logic code here

    def buildVSMClassifier_OneTargetTopicVector(self,posFile,vsmClassifierFileName,th,topK):
        
        try:
            classifierFile = open(vsmClassifierFileName,"rb")
            self.classifier = pickle.load(classifierFile)
            classifierFile.close()
        except:
            docs = []
            f = open(posFile,'r')
            for url in f:
                url = url.strip()
                d = Document(url)
                if d and d.text:
                    docs.append(d)
            f.close()
            
            docsTF = []
            vocabTFDic = {}
            n = len(docs)
            for d in docs:
                wordsFreq = getFreq(d.getWords())
                #docsTF.append(wordsFreq)
                for w in wordsFreq:
                    if w in vocabTFDic:
                        #vocabTFDic[w] += wordsFreq[w]
                        vocabTFDic[w].append( wordsFreq[w])
                    else:
                        vocabTFDic[w] = [wordsFreq[w]]
            #vocTF_IDF = [(w,sum(vocabTFDic[w])*math.log(n*1.0/len(vocabTFDic[w]))) for w in vocabTFDic]
            idf = 1.0
            vocTF_IDF = [(w,sum([1+math.log(vtf) for vtf in vocabTFDic[w]])*idf) for w in vocabTFDic]
             
            #vocabSorted = getSorted(vocabTFDic.items(), 1)
            vocabSorted = getSorted(vocTF_IDF, 1)
            print vocabSorted[:topK]
            topVocabDic = dict(vocabSorted[:topK])
            #topVocabDic = vocabTFDic
             
            
            self.classifier = VSMClassifier(topVocabDic,th)
            classifierFile = open(vsmClassifierFileName,"wb")
            pickle.dump(self.classifier,classifierFile)
            classifierFile.close()
    '''    
    
    def buildVSMClassifier(self,posFile,no_keywords,classifierFileName,error=0.05,roundPrec=3):
        try:
            classifierFile = open(classifierFileName,"rb")
            self.classifier = pickle.load(classifierFile)
            #self.classifier.error = 0.05
            #self.classifier.relevanceth = 0.75
            classifierFile.close()
        except:
            self.classifier = VSMClassifier()
            posURLs = readFileLines(posFile)
            self.classifier.buildVSMClassifier(posURLs, no_keywords, classifierFileName,error,roundPrec)
            print self.classifier.relevanceth
            classifierFile = open(classifierFileName,"wb")
            pickle.dump(self.classifier,classifierFile)
            classifierFile.close()
    
    
    def evaluateFC(self,pages):
        results=[]
        self.scores = []
        #for page,score in pages:
        for page in pages:
            #if page.estimatedScore > 0:
            try:
                s = self.classifier.calculate_score(page.text)
            except:
                #print sys.exc_info()
                s = self.classifier.calculate_score(page['text'])
            r = s[0]
            results.append(r)
            self.scores.append(s[1])
            
        print self.scores
        print results
        print sum(results)
        return results

def getWebpageTextFromFolder(collFolder,num):
    webpages = []
    for j in range(num):
        
        fn = collFolder+str(j)+'.txt'
        f = codecs.open(fn, encoding='utf-8')
        ftext = f.read()
        webpages.append({'text':ftext})
    return webpages


if __name__ == "__main__":
    evalr = Evaluate()
    eventName = 'oregonCommCollegeShooting'#'deltaStateUnivCampusShooting'#'charlestonShooting'
    #posFile = 'charlestonShooting-' + 'Pos.txt'
    #posFile = 'deltaStateUnivCampusShooting-' + 'Pos.txt'
    posFile = eventName+ '-Pos.txt'
    testFile = 'test.txt'
    classifierFileName= posFile.split(".")[0].split('-')[0]+"VSMClassifier"+".p"
    #classifierFileName= posFile.split(".")[0].split('-')[0]+"oneClassClassifier"+".p"
    #th=0.4
    #leastK = 40
    topK = 7
    leastDocFreq = 2
    error = 0.15
    roundPrec = 3
    negFile = 'charlestonShootingNeg.txt'
    #evalr.buildOneClassClassifier(posFile, negFile, oneClassClassifierFileName)
    evalr.buildVSMClassifier(posFile,topK, classifierFileName,error,roundPrec)
    
    #testPages = getWebpageText_NoURLs(readFileLines(testFile))
    testPages = getWebpageTextFromFolder('Output-oregonCommCollegeShooting-20seeds/event-webpages/',1000)
    
    #testPages = [tp for tp in testPages if 'text' in tp]
    #print len(testPages)
    evalr.evaluateFC(testPages)        
        