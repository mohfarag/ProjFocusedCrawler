from document import Document
import eventUtils as utils
class Collection:
    ''' Class for handling corpus collection'''
    def __init__(self,urls=[],texts=[]):
        
        self.documents = []
        if len(urls)>0:
            self.URLs= urls
            if len(texts)>0:
                for u,d in zip(urls,texts):
                    doc = Document(u,d)
                    self.documents.append(doc)
            else:
                for u in self.URLs:
                    doc = Document(u)
                    self.documents.append(doc)
        
        self.words = []
        self.sentences = []
        self.wordsFrequencies = []
        self.indicativeWords = []
        self.indicativeSentences = []
    '''    
    def __init__(self):
        self.URLs= []
        self.documents = []
        self.words = []
        self.sentences = []
        self.wordsFrequencies = []
        self.indicativeWords = []
        self.indicativeSentences = []
    
    def __init__(self,urls,texts):
        self.URLs = urls
        self.documents = []
        self.words = []
        self.sentences = []
        self.wordsFrequencies = []
        self.indicativeWords = []
        self.indicativeSentences = []
        for u,d in zip(urls,texts):
            doc = Document(u,d)
            self.documents.append(doc)
    
    def __init__(self,urls):
        self.URLs = urls
        self.documents = []
        for u in self.URLs:
            doc = Document(u)
            self.documents.append(doc)
            
        #self.documents = []
        self.words = []
        self.sentences = []
        self.wordsFrequencies = []
        self.indicativeWords = []
        self.indicativeSentences = []
    '''
    def getWordsFrequencies(self):
        for d in self.documents:
            w = d.getWords()
            self.words.extend(w)
        f = utils.getFreq(self.words)
        tokensFreqs = f.items()
        self.wordsFrequencies = utils.getSorted(tokensFreqs,1)
        return self.wordsFrequencies
    
    def getIndicativeWords(self):
        if self.indicativeWords:
            return self.indicativeWords
        else:
            toksTFDF = self.getWordsTFDF()
            sortedToksTFDF = sorted(toksTFDF.items(), key=lambda x: x[1][0]*x[1][1], reverse=True)
            indWords = [w[0] for w in sortedToksTFDF]
            
            wordsTags = utils.getPOS(indWords)
            nvWords = [w[0] for w in wordsTags if w[1].startswith('N') or w[1].startswith('V')]
            wordsDic = dict(sortedToksTFDF)
            self.indicativeWords = [(w,wordsDic[w]) for w in nvWords]
            return self.indicativeWords
            
    def getWordsTFDF(self):
        
        tokensTF = dict(self.wordsFrequencies)
        tokensDF = {}
        for te in tokensTF:
            df = sum([1 for t in self.documents if te in t.getWords()])
            tokensDF[te] = df
        
        tokensTFDF = {}
        for t in tokensDF:
            tokensTFDF[t] = (tokensTF[t],tokensDF[t])
        
        return tokensTFDF
    
    def getIndicativeSentences(self,topK,intersectionTh):
        if len(self.indicativeSentences) > 0:
            return self.indicativeSentences
        else:
            topToksTuples = self.indicativeWords[:topK]
            topToks = [k for k,_ in topToksTuples]
            
            for d in self.documents:
                sents = d.getSentences()
                if len(sents)>0:
                    self.sentences.extend(sents)
            
            impSents ={}
            for sent in self.sentences:
                if sent not in impSents:
                    sentToks = utils.getTokens(sent)
                    if len(sentToks) > 100:
                        continue
                    intersect = utils.getIntersection(topToks, sentToks)
                    if len(intersect) > intersectionTh:
                        impSents[sent] = len(intersect)
                        #if sent not in impSentsF:
                        #    impSentsF[sent] = len(intersect)
                    #allImptSents.append(impSents)
            if impSents:
                self.indicativeSentences = utils.getSorted(impSents.items(),1)
            return self.indicativeSentences