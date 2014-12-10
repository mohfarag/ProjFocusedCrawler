from gensim import corpora, models, similarities
from webpage import Webpage
from scorer import Scorer

class TFIDF_Scorer(Scorer):
    '''
    def __init__(self):
        super(TFIDF_Scorer, self).__init__()
        self.seedPages = []
        '''
    def __init__(self,seedUrls):
        self.exclude_words = ['ads','print','advertisement']
        self.seedUrls = seedUrls
        super(TFIDF_Scorer, self).__init__(None)
        self.seedPages = []
        self.avgdl = 0
        for url in self.seedUrls:
            page = Webpage(url)
            data = self.cleanDoc(page.text)
            self.seedPages.append(data)
            self.avgdl += len(data)
        self.buildModel(self.seedPages)
        
            
    
    def bm25(self,idf, tf, dl, avgdl, B, K1):
        return idf * ((tf * (K1 + 1)) / (tf + K1 * ((1 - B) + B * dl / avgdl)))
    
    def buildModel(self,docs):
        self.docsDictionary = corpora.Dictionary(docs)
        corpus = [self.docsDictionary.doc2bow(text) for text in docs]        
        #doc_map = dict((v,k) for k,v in docsDictionary.token2id.iteritems())
        self.tfidf = models.TfidfModel(corpus,normalize=True)
        corpus_tfidf = self.tfidf[corpus]        
        self.index = similarities.MatrixSimilarity(corpus_tfidf)
        return
    def calculate_score(self,url):
        query_doc = url.lower().split()
        #for w in self.exclude_words:
        #    if w in query_doc:
        #        return 0
        query_doc = [self.stemmer.stem(word) for word in query_doc]
        query_bow = self.docsDictionary.doc2bow(query_doc)
        query_tfidf = self.tfidf[query_bow]
        simsc = self.index[query_tfidf]
        #score = sum(simsc)/len(simsc)
        score = max(simsc)
        return score
    

        
