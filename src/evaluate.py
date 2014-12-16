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
from eventUtils import train_SaveClassifier,readFileLines
import os
#import pickle
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

    def buildClassifier(self,posFile,negFolder,classifierFileName):
        #negURLsFile = 'negFile.txt'
        posURLs = readFileLines(posFile)
        posLen = len(posURLs)
        negFiles = os.listdir(negFolder)
        negFiles = [os.path.join(negFolder,f) for f in negFiles if f.endswith(".txt")]
        #print negFiles
        negFilesURLs = [readFileLines(f) for f in negFiles]
        
        num = posLen/len(negFiles)
        negURLs = []
        for nfu in negFilesURLs:
            #print len(nfu)
            if num < len(nfu):
                negURLs.extend(nfu[:num] )
            else:
                negURLs.extend(nfu )
        #print len(negURLs)
        self.classifier = train_SaveClassifier(posURLs, negURLs, classifierFileName)
        #return cls

    
    def evaluateFC(self,pages):
        results=[]
        for page,score in pages:
            #results.append(self.classifier.calculate_score(page.text))
            if score ==1:
                s = self.classifier.calculate_score(page.text)[0]
                results.append(s)
            else:
                results.append(0)
        return results
        
        