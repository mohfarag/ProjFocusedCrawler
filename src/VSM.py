'''
Created on Dec 25, 2012

@author: Mohamed
'''
import math
from collection import Collection
from Filter import getTokenizedDocs, getTokenizedDoc
#from eventUtils import getWebpageText,getSorted
import eventUtils
class VSM:
    
    def __init__(self,docsURLs=[],docsTxts=[],docsColl=[]):
        if docsColl:
            self.coll = docsColl
        elif docsURLs:
            if docsTxts:
                self.coll = Collection(docsURLs,docsTxts)
            else:
                self.coll = Collection(docsURLs)
    
    
    # Function that builds VSM from set of documents
    def buildModel(self,num=10):
        #docs = downloadRawDocs(seedURLs)
        
        #td = getWebpageText(seedURLs)
        #docs = [t['text'] + " "+ t['title'] for t in td if t.has_key('text')]
        #docs = getTokenizedDocs(docs)
        #docsWords = [d.words for d in self.coll.documents if d.text]
        #self.n = len(docs)
        #docs_bow = [self.doc2bow(docWords) for docWords in docsWords]
        #docs_bow = [eventUtils.getFreq(d.words) for d in self.coll.documents if d.text]
        self.buildIndex()
        self.filterIndex(collFreq=10,docFreq=2)
        self.getDocsVecs()
        self.getCollVec(numWords=10)
        #selected = self.selectImportantWords_tf(num)
        #print selected
        #wordsList = self.index.keys()
        #selected_words = [wordsList[k[1]] for k in selected]
        #print selected_words
        #self.model = (selected,selected_words)
    
    def buildIndex(self):
        self.docs_bow = [eventUtils.getFreq(d.words) for d in self.coll.documents if d.text]
        for doc_bow in self.docs_bow:
            for w in doc_bow:
                if w in self.index:
                    self.index[w]['docs'].append(doc_bow[w])
                else:
                    self.index[w] = {}
                    self.index[w]['docs'] = [doc_bow[w]]
        for w in self.index:
            self.index[w]['docFreq'] = len(self.index[w]['docs'])
            self.index[w]['collFreq'] = sum(self.index[w]['docs'])
    
    def filterIndex(self,collFreq=10,docFreq=2):
        self.filteredIndex = {}
        for w in self.index:
            if self.index[w]['docFreq'] >= docFreq:
                if self.index[w]['collFreq'] >= collFreq:
                    self.filteredIndex[w] = self.index[w]
        self.index.clear()
        self.index = self.filteredIndex
    
    def getDocsVecs(self):
        n= len(self.docs_bow)
        indexWordsSet = self.index.keys()
        self.docsVecs = []
        for doc_bow in self.docs_bow:
            docVec = {}
            docWordsSet = set(doc_bow.keys())
            commWords = eventUtils.getIntersection(indexWordsSet, docWordsSet)
            for w in commWords:
                idf = math.log(n/self.index[w]['docFreq'])
                tf_idf = doc_bow[w] * idf
                docVec[w]=tf_idf
            self.docsVecs.append(docVec)
    
    def getCollVec(self,numWords=10):
        n = len(self.docsVecs)
        wordsWeights = [(w,self.index[w]['collFreq'] * math.log(n*1.0/self.index[w]['docFreq'])) for w in self.index]
        wordsWeightsSorted = eventUtils.getSorted(wordsWeights, 1)
        topWords = wordsWeightsSorted[:numWords]
        self.collVec = dict(topWords)
    #####################################
    def bm25(self,idf, tf, dl, avgdl, B, K1):
        return idf * ((tf * (K1 + 1)) / (tf + K1 * ((1 - B) + B * dl / avgdl)))
    
    def buildVocabIndex(self,docs):
        self.index = {}
        for i in range(len(docs)):
            for word in docs[i]:            
                if(self.index.has_key(word[0])):
                    #self.index[word[0]].append((i,word[1]))
                    self.index[word[0]].append(word[1])
                else:
                    #self.index[word[0]] = [(i,word[1])] 
                    self.index[word[0]] = [word[1]]
    
    
    # function to build vocabulary (unique words) from corpus
    # and calculate the document frequency and collection freq of each word
    # @docs a list of documents, where each document is a list of tuples (word, freq)
    def buildVocab(self,docs):
        self.dictionary = {}
        for doc in docs:
            for word in doc:
                if(self.dictionary.has_key(word[0])):
                    self.dictionary[word[0]] = (self.dictionary[word[0]][0]+1, self.dictionary[word[0]][1] + word[1])
                else:
                    self.dictionary[word[0]] = (1,word[1])
        return self.dictionary
    
    # no need for it
    def calculateIDF(self):
        self.idf = []
        n = len(self.dictionary.keys()) # wrong calculation, should be n= len(docs)
        for k,v in self.dictionary.iteritems():
            temp = n/math.log(v[0])
            self.idf.append(temp)
            
    def calculateTF(self,doc):
        doc_tf = []
        for t in doc:
            if t[1] > 0:
                v = 1 + math.log(t[1])
            else:
                v = 0
            doc_tf.append((t[0],v))
        return doc_tf 
    
    def selectImportantWords_tf(self,k):        
        words_tfidf_sum = []     
        #n = len(self.index.keys())
        i = 0
        for v in self.index.itervalues():
            #l = len(v)
            idf = 1
            #tf = [1 + math.log(t) for t in v]
            #tfidf = idf * sum(tf)
            
            #tf = 1+ math.log(sum(v))
            tf = sum([1+math.log(it) for it in v])
            tfidf = idf * tf
            words_tfidf_sum.append((tfidf,i))
            i = i+1
        self.words_tfidf_sorted = getSorted(words_tfidf_sum, 0)#sorted(words_tfidf_sum,reverse=True)
        selected = self.words_tfidf_sorted
        if len(self.words_tfidf_sorted) > k:
            selected = self.words_tfidf_sorted[:k]
        return selected
    
    def selectImportantWords(self,k):        
        words_tfidf_sum = []     
        #n = len(self.index.keys())
        i = 0
        for v in self.index.itervalues():
            l = len(v)
            idf = math.log(self.n/float(l))
            tf = [1 + math.log(t) for t in v]
            tfidf = idf * sum(tf)
            words_tfidf_sum.append((tfidf,i))
            i = i+1
        self.words_tfidf_sorted = sorted(words_tfidf_sum,reverse=True)
        selected = self.words_tfidf_sorted
        if len(self.words_tfidf_sorted) > k:
            selected = self.words_tfidf_sorted[:k]
        return selected
            
    #convert a document to a bag of words (word, freq)
    # doc is a list of words
    
    def doc2bow(self,doc): 
        temp = {}
        for word in doc:
            #if(word in temp.keys()):
            if(temp.has_key(word)):
                temp[word]+=1
            else:
                temp[word] = 1
        bow = [(w,f) for w,f in temp.iteritems()]
        return bow
    
    def calculate_tfidf(self,bow):
        return
    
    #def buildModel(self,docs):
    
    def buildModel_2(self,seedURLs,num):
        #docs = downloadRawDocs(seedURLs)
        td = getWebpageText(seedURLs)
        docs = [t['text'] + " "+ t['title'] for t in td if t.has_key('text')]
        
        docs = getTokenizedDocs(docs)
        self.n = len(docs)
        docs_bow = [self.doc2bow(doc) for doc in docs]
        #vocab = self.buildVocab(docs_bow)
        self.buildVocabIndex(docs_bow)
        selected = self.selectImportantWords_tf(num)
        print selected
        wordsList = self.index.keys()
        selected_words = [wordsList[k[1]] for k in selected]
        print selected_words
        self.model = (selected,selected_words)
        #n = len(docs)
        #selected_words_idfs = [n/math.log(len(self.index[w[1]])) for w in selected]
        
    def convertDoctoTFIDF(self,doc):
        '''
        stemmer = PorterStemmer()
        tokenizer = WordPunctTokenizer()
        stopwords_e = stopwords.words('english')
        stopwords_e.extend(["last","time","week","favorite","home","search","follow","year","account","update","com","video","close","http","retweet","tweet","twitter","news","people","said","comment","comments","share","email","new","would","one","world"])
        tokens = tokenizer.tokenize(doc)
        clean = [token for token in tokens if token.isalnum()]
        clean = [token.lower() for token in clean if token.lower() not in stopwords_e] 
        clean = [token for token in clean if len(token) > 2]
        final_doc = [stemmer.stem(word) for word in clean]
        '''
        final_doc = getTokenizedDoc(doc)
        doc_tfidf=[]
        words = self.model[1]
        for i in range(0,len(words)):            
            tf = final_doc.count(words[i])
            if tf > 0:
                tf = 1 + math.log(tf)  
            doc_tfidf.append((tf,words[i]))
        return doc_tfidf
    
    def getScalar(self,doc_tfidf):
        total = 0
        for i in range(len(doc_tfidf)):
            total += doc_tfidf[i][0] * doc_tfidf[i][0]
        return math.sqrt(total)
    
    def calculateCosSim(self,doc):
        doc_tfidf = self.convertDoctoTFIDF(doc)
        total = 0
        model_tfidf = self.model[0]
        for i in range(len(model_tfidf)):
            total += model_tfidf[i][0] * doc_tfidf[i][0]        
        if total > 0:
            return float(total)/(self.getScalar(model_tfidf) * self.getScalar(doc_tfidf))
        else:
            return 0
    
    def calculate_score(self,query,m):
        score = self.calculateCosSim(query)
        return score        
            
            
            
            
            
            
            
            
            
            
            