'''
Created on Nov 30, 2012

@author: Mohamed
'''
import numpy as np
from sklearn.naive_bayes import *

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_selection import SelectKBest, chi2
class NaiveBayesClassifier(object):
    '''
    classdocs
    '''
        
    def __init__(self):
        
        self.classifier = MultinomialNB()
        #self.model = None
        
    def trainClassifier(self, trainingDocs, labels):
        self.trainingDocs = trainingDocs
        self.labels = labels
        
        self.count_vect = CountVectorizer()
        X_train_counts = self.count_vect.fit_transform(self.trainingDocs)
        self.tf_transformer = TfidfTransformer(use_idf=True).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        
        self.ch2 = SelectKBest(chi2)
        X_train = self.ch2.fit_transform(X_train_tf, self.labels)
        
        #self.classifier.fit(X_train_tf, self.labels)
        self.classifier.fit(X_train, self.labels)
        
    def classify(self, docs_new):
        X_new_counts = self.count_vect.transform(docs_new)
        X_new_tfidf = self.tf_transformer.transform(X_new_counts)
        X_test = self.ch2.transform(X_new_tfidf)
        #predicted = self.model.predict(X_new_tfidf)
        #self.predicted = self.classifier.predict(X_new_tfidf)
        self.predicted = self.classifier.predict(X_test)
        #for doc, category in zip(docs_new, self.predicted):
        #    print '%r => %s' % (doc,category)
        return self.predicted
    
    def score(self,docs_test,labels):
        X_new_counts = self.count_vect.transform(docs_test)
        X_new_tfidf = self.tf_transformer.transform(X_new_counts)
        
        X_test = self.ch2.transform(X_new_tfidf)
        #self.predicted = self.classifier.predict(X_new_tfidf)
        self.predicted = self.classifier.predict(X_test)
        accuracy = np.mean(self.predicted == labels)
        #accuracy = self.classifier.score(X_new_tfidf, labels)
        return accuracy