'''
Created on Mar 13, 2014

@author: mohamed
'''
#from SVMClassifier import SVMClassifier
from NBClassifier import NaiveBayesClassifier
import numpy as np
from sklearn import metrics
from Filter import downloadRawDocs, getTokenizedDocs
class Evaluate(object):
    '''
    classdocs
    '''


    #def __init__(self,pages,posFile,negFile):
    def __init__(self,posFile,negFile):
        '''
        Constructor
        '''
        #self.pages = pages
        #posURLs = getSeedURLs(posFile)
        posDocs = downloadRawDocs(posFile)
        #posDocs = getTokenizedDocs(docs)
        
        #negURLs = getSeedURLs(negFile)
        negDocs = downloadRawDocs(negFile)
        #negDocs = getTokenizedDocs(docs) 
        posLen = len(posDocs)
        negLen = len(negDocs)
        posLabels = [1]* posLen
        negLabels = [0]*negLen 
        
        posSep = int(posLen*0.7)
        negSep = int(negLen*0.7)
        
        trainingDocs = posDocs[:posSep] + negDocs[:negSep]
        
        trainingLabels = posLabels[:posSep] + negLabels[:negSep]
        
        testDocs = posDocs[posSep:] + negDocs[negSep:]
        test_labels=posLabels[posSep:] + negLabels[negSep:]
        
        self.classifier = NaiveBayesClassifier()
        
        #trainingLabelsArr = np.array(labels)
        #classifier.trainClassifier(docs,trainingLabelsArr)
        
        trainingLabelsArr = np.array(trainingLabels)
        self.classifier.trainClassifier(trainingDocs,trainingLabelsArr)
        test_labelsArr = np.array(test_labels)
        print self.classifier.score(testDocs, test_labelsArr)
        
        print metrics.classification_report(test_labelsArr, self.classifier.predicted)
    
    def evaluateFC(self,pages):
        results=[]
        for page in pages:
            results.append(self.classifier.calculate_score(page.text))
        return results
        
        