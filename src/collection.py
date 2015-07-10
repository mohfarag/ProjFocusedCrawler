from document import Document
import eventUtils as utils
import math
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
                    if doc and doc.text:
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
            if w:
                self.words.extend(w)
        f = utils.getFreq(self.words)
        tokensFreqs = f.items()
        self.wordsFrequencies = utils.getSorted(tokensFreqs,1)
        return self.wordsFrequencies
    
    def getIndicativeWords_old(self):
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
    
    def getIndicativeWords(self,t):
        if self.indicativeWords:
            return self.indicativeWords
        else:
            
            #toksTFDF = self.getWordsTFDF()
            #sortedToksTFDF = sorted(toksTFDF.items(), key=lambda x: x[1][0], reverse=True)
            #indWords = [w[0] for w in sortedToksTFDF]
            
            #wordsTags = utils.getPOS(indWords)
            #nvWords = [w[0] for w in wordsTags if w[1].startswith('N') or w[1].startswith('V')]
            #wordsDic = dict(sortedToksTFDF)
            #self.indicativeWords = [(w,wordsDic[w]) for w in nvWords]
            #-----

            #self.indicativeWords = self.getWordsFrequencies()
            
            if t =='TFIDF':
                toks = self.getWordsTFIDF()
            elif t == 'TFDF':
                toks = self.getWordsTFDF()
            elif t == 'TF':
                toks = self.getWordsTF()
            #self.indicativeWords = utils.getSorted(toks.items(),1)
            self.indicativeWords = toks
            return self.indicativeWords
            
    def getWordsTFDF(self):
        self.getWordsFrequencies()
        tokensTF = dict(self.wordsFrequencies)
        tokensDF = {}
        for te in tokensTF:
            df = sum([1 for t in self.documents if te in t.words])
            tokensDF[te] = df
        
        tokensTFDF = {}
        for t in tokensDF:
            tokensTFDF[t] = (tokensTF[t],tokensDF[t])
        
        return tokensTFDF
    
    def getWordsTFIDF(self):
        self.getWordsFrequencies()
        tokensTF = dict(self.wordsFrequencies)
        tokensDF = {}
        for te in tokensTF:
            df = sum([1 for t in self.documents if te in t.words])
            tokensDF[te] = df
        
        tokensTFIDF = {}
        for t in tokensDF:
            tokensTFIDF[t] = (1+ math.log(tokensTF[t])) * math.log(len(self.documents)/ 1.0*tokensDF[t])
        
        return tokensTFIDF
    
    def getWordsTF(self):
        self.getWordsFrequencies()
        tokensTF = dict(self.wordsFrequencies)
        '''
        tokensDF = {}
        for te in tokensTF:
            df = sum([1 for t in self.documents if te in t.words])
            tokensDF[te] = df
        
        tokensTFIDF = {}
        for t in tokensDF:
            tokensTFIDF[t] = (1+ math.log(tokensTF[t])) * math.log(len(self.documents)/ 1.0*tokensDF[t])
        '''
        for te in tokensTF:
            tokensTF[te] = (1+ math.log(tokensTF[te]))
        return tokensTF
    
    def getIndicativeSentences(self,topK,intersectionTh):
        if len(self.indicativeSentences) > 0:
            return self.indicativeSentences
        else:
            topToksTuples = self.indicativeWords[:topK]
            #topToksTuples = self.indicativeWords
            topToks = [k for k,_ in topToksTuples]
            
            for d in self.documents:
                sents = d.getSentences()
                if sents and len(sents)>0:
                    self.sentences.extend(sents)
            
            impSents ={}
            for sent in self.sentences:
                if sent not in impSents:
                    sentToks = utils.getTokens(sent)
                    if len(sentToks) > 100:
                        continue
                    intersect = utils.getIntersection(topToks, sentToks)
                    if len(intersect) > intersectionTh:
                        #impSents[sent] = len(intersect)
                        impSents[sent] = intersect
                        #print intersect
                        #if sent not in impSentsF:
                        #    impSentsF[sent] = len(intersect)
                    #allImptSents.append(impSents)
            if impSents:
                #self.indicativeSentences = utils.getSorted(impSents.items(),1)
                self.indicativeSentences = sorted(impSents.items(),key=lambda x: len(x[1]), reverse=True)
                #sortedToksTFDF = sorted(toksTFDF.items(), key=lambda x: x[1][0], reverse=True)
            return self.indicativeSentences