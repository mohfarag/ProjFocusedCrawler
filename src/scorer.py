import nltk
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models, similarities
from nltk.tokenize.regexp import WordPunctTokenizer

class Scorer(object):
    #docs =[]
    #docs_length=[]
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stopwords = nltk.corpus.stopwords.words('english')
        self.tokenizer = WordPunctTokenizer()
        self.keywords = []
        self.score = 0

    def cleanDoc(self,doc):
        
        tokens = self.tokenizer.tokenize(doc)
        clean = [token.lower() for token in tokens if token.lower() not in self.stopwords and len(token) > 2]
        final = [self.stemmer.stem(word) for word in clean]
        return final
    
    #def __init__(self,seedUrls):
    def __init__(self,keywords):
        self.stemmer = PorterStemmer()
        self.stopwords = nltk.corpus.stopwords.words('english')
        self.tokenizer = WordPunctTokenizer()
        self.score = 0
        self.keywords = keywords
        #self.keywords = []
        '''for url in seedUrls:
            page = Webpage(url)
            data = self.cleanDoc(page.text)
            for d in data:
                self.keywords.append(d)'''
# this function checks if the url words contain the keywords or not.
# the score given is calculated by finding how many keywords occur in the url.
    def calculate_score(self,url):
        words = url.getAllText().split()        
        for w in self.keywords:
            if w in words:
                self.score +=1
        self.score = self.score / float(len(self.keywords))
        return self.score
