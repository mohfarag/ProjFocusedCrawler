'''
Created on Sep 20, 2015

@author: mmagdy
'''
import numpy as np
from sklearn import svm
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_selection import SelectKBest, chi2
class OneClassClassifier(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.classifier = svm.OneClassSVM( kernel="rbf", gamma=0.0)#(nu=0.1, kernel="rbf", gamma=0.1)
        
    def trainClassifier(self, trainingDocs,labels):
        #self.trainingDocs = trainingDocs
        #self.labels = labels
        
        self.count_vect = CountVectorizer(stop_words='english')
        #X_train_counts = self.count_vect.fit_transform(self.trainingDocs)
        X_train_counts = self.count_vect.fit_transform(trainingDocs)
        self.tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
        #self.tf_transformer = TfidfTransformer().fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        
        self.ch2 = SelectKBest(chi2,k=100)
        X_train = self.ch2.fit_transform(X_train_tf, labels)
        
        #self.classifier.fit(X_train_tf, self.labels)
        self.classifier.fit(X_train)
    
    def calculate_score(self, doc_new):
        doc_list = [doc_new]
        #doc_list.append(doc_new)
        X_new_counts = self.count_vect.transform(doc_list)
        X_new_tfidf = self.tf_transformer.transform(X_new_counts)
        #X_test = self.ch2.transform(X_new_tfidf)
        X_test = X_new_tfidf
        self.predicted = self.classifier.predict(X_test)
        return self.predicted
    
    def score(self,docs_test,labels):
        '''
        Here labels are 1 and -1
        '''
        X_new_counts = self.count_vect.transform(docs_test)
        X_new_tfidf = self.tf_transformer.transform(X_new_counts)
        
        X_test = self.ch2.transform(X_new_tfidf)
        #X_test = X_new_tfidf
        self.predicted = self.classifier.predict(X_test)
        print self.predicted
        accuracy = np.mean(self.predicted == labels)
        #accuracy = self.classifier.score(X_new_tfidf, labels)
        return accuracy