'''
Created on Nov 30, 2012

@author: Mohamed
'''
from sklearn import svm
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_selection import SelectKBest, chi2
import numpy as np

class SVMClassifier(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.classifier = svm.SVC(probability=True)
        #self.model = None
        
    def trainClassifier_old(self, trainingDocs, labels):
        self.trainingDocs = trainingDocs
        self.labels = labels
        '''
        self.count_vect = CountVectorizer(charset='utf-8-sig')
        X_train_counts = self.count_vect.fit_transform(self.trainingDocs)
        self.tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        '''
        
        self.model = self.classifier.fit(self.trainingDocs, self.labels)
        
    def trainClassifier(self, trainingDocs, labels):
        self.trainingDocs = trainingDocs
        self.labels = labels
        self.count_vect = CountVectorizer()
        X_train_counts = self.count_vect.fit_transform(self.trainingDocs)
        self.tf_transformer = TfidfTransformer(use_idf=True).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        
        self.ch2 = SelectKBest(chi2)
        X_train = self.ch2.fit_transform(X_train_tf, labels)
        
        #self.model = self.classifier.fit(X_train_tf, self.labels)
        #self.classifier.fit(X_train_tf, self.labels)
        self.classifier.fit(X_train, self.labels)
    
    def calculate_score(self, doc_new):
        doc_list = []
        doc_list.append(doc_new)
        X_new_counts = self.count_vect.transform(doc_list)
        X_new_tfidf = self.tf_transformer.transform(X_new_counts)
        X_test = self.ch2.transform(X_new_tfidf)
        #self.predicted = self.classifier.predict(X_new_tfidf)
        
        
        #self.predicted = self.classifier.predict(X_test)
        self.predicted = self.classifier.predict(X_test)
        
#         neg_prob = self.predicted[0][0]
#         pos_prob = self.predicted[0][1]
#         if (neg_prob > pos_prob):
#             return 0
#         else:
#             return pos_prob
        return self.predicted
    
    def calculate_score_prob(self, doc_new):
        doc_list = []
        doc_list.append(doc_new)
        X_new_counts = self.count_vect.transform(doc_list)
        X_new_tfidf = self.tf_transformer.transform(X_new_counts)
        X_test = self.ch2.transform(X_new_tfidf)
        #self.predicted = self.classifier.predict(X_new_tfidf)
        
        
        #self.predicted = self.classifier.predict(X_test)
        self.predicted = self.classifier.predict_proba(X_test)
        #return self.predicted[0]
        neg_prob = self.predicted[0][0]
        pos_prob = self.predicted[0][1]
        if (neg_prob > pos_prob):
            return 0
        else:
            return pos_prob
        ##return self.predicted
        #for doc, category in zip(docs_new, self.predicted):
            #print '%r => %s' % (doc,category)
    def classify_old(self, docs_new):
        #X_new_counts = self.count_vect.transform(docs_new)
        #X_new_tfidf = self.tf_transformer.transform(X_new_counts)
        
        predicted = self.model.predict(docs_new)
        
        for doc, category in zip(docs_new, predicted):
            print '%r => %s' % (doc,category)
        
    def score(self,docs_test,labels):
        X_new_counts = self.count_vect.transform(docs_test)
        X_new_tfidf = self.tf_transformer.transform(X_new_counts)
        X_test = self.ch2.transform(X_new_tfidf)
        #self.predicted = self.classifier.predict(X_new_tfidf)
        self.predicted = self.classifier.predict(X_test)
        accuracy = np.mean(self.predicted == labels)
        return accuracy        