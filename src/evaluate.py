'''
Created on Mar 13, 2014

@author: mohamed
'''
'''
#from SVMClassifier import SVMClassifier
from NBClassifier import NaiveBayesClassifier
import numpy as np
from sklearn import metrics
from Filter import downloadRawDocs
'''
from eventUtils import getFreq, train_SaveClassifier, readFileLines,getTokens, getScalar
import os
import math
import pickle
from document import Document

class VSMClassifier(object):
    def __init__(self, targetDocsTF):
        self.docsTF = targetDocsTF
        
    def cosSim(self, doc1,doc2):
        sim = 0
        for k in doc1:
            if k in doc2:
                sim += (1 + math.log(doc1[k])) *  (1+math.log(doc2[k]))
        
        if sim > 0:
            
            sim = float(sim)/(getScalar(doc1) * getScalar(doc2))
            
        else:
            sim = 0
        return sim
    
    def calculate_score(self, doc):
        sims=[]
        docWords = getTokens(doc)
        docTF = getFreq(docWords)
        for dTF in self.docsTF:
            s = self.cosSim(docTF, dTF)
            sims.append(s)
        return max(sims)
    
    
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
    
    def buildVSMClassifier(self,posFile,vsmClassifierFileName):
        
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
                docs.append(d)
            f.close()
            docsTF = []
            for d in docs:
                wordsFreq = getFreq(d.getWords())
                docsTF.append(wordsFreq)
            
            self.classifier = VSMClassifier(docsTF)
            classifierFile = open(vsmClassifierFileName,"wb")
            pickle.dump(self.classifier,vsmClassifierFileName)
            classifierFile.close()
        
    def evaluateFC(self,pages):
        results=[]
        #for page,score in pages:
        for page in pages:
            #if page.estimatedScore > 0:
            s = self.classifier.calculate_score(page.text)[0]
            results.append(s)
            #else:
            #    results.append(0)
        return results
        
        