'''
Created on Oct 20, 2012

@author: mohamed
'''

import urllib2
import nltk
from urllib import FancyURLopener
from nltk.stem.porter import PorterStemmer
from nltk.tokenize.regexp import WordPunctTokenizer
import codecs
import re
from bs4 import BeautifulSoup,Comment
#from crawler import preprocess
#import crawler

class MyOpener(FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
#stemmer = None

def getTopicKeywords(fileName):
    stemmer = PorterStemmer()
    topicKeywords=[]
    f = open(fileName,'r')
    for line in f:
        #topicKeywords.append(line[:-1])
        topicKeywords.append(stemmer.stem(line[:-1]))
    return topicKeywords

def preprocess(url):
    try:
        myopener = MyOpener()
        webpage = myopener.open(url).read()
        #webpage = urllib2.urlopen(url).read()
        #webpage = webpage.decode('utf-8')
        text = nltk.clean_html(webpage)
        tokens = nltk.word_tokenize(text)
        return tokens
    except urllib2.URLError, e:
        return str(e.reason)
    except urllib2.HTTPError, e:
        return str(e.code)

def downloadRawDocs(fileName):
    docs = []
    text = ""
    #titles = []
    f = open(fileName,'r')
    myopener = MyOpener()
    
    for line in f:
        line = line[:-1]
        try:
            #print len(docs)
            webpage = myopener.open(line).read()
            #text = nltk.clean_html(webpage)            
            soup = BeautifulSoup(webpage)
        #t = soup.html.head.title
#             t = soup.title
#             if (t != None):
#                 if t.string != None:
#                     titles.append(t.string.split(' '))
#                 else:
#                     titles.append([])
#             else:
#                 titles.append([])
            title = ""
            if soup.title:
                if soup.title.string:
                    title = soup.title.string
            comments = soup.findAll(text=lambda text:isinstance(text,Comment))
            [comment.extract() for comment in comments]
            text_nodes = soup.findAll(text=True)
            visible_text = filter(visible, text_nodes)
            text = ''.join(visible_text)
            #text = ""
            text = text + title
            #print text
            #print line
            #webpage = codecs.open(line, 'r',encoding='utf-8').read()
            #text = nltk.clean_html(webpage)
            docs.append(text)
            myopener.close()
        except Exception:
            print "Exception, URL couldn't be retrieved"
            text = ""
            docs.append(text)
    f.close()
    return docs

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head']:
        return False
    return True

def getUrls_tokens(fileName):
    urls = []
    f =  open(fileName,'r')
    #f = codecs.open(fileName, 'r',encoding='utf-8')
    for line in f:
        line = line[:-1]
        # get url part and put it in urls
        ind = line.find("http")
        if ind == -1:
            ind = line.find("https")
            u = line[ind+5:]
        else:
            u = line[ind+4:]
        parts = [s for s in re.findall(r'\w+',u) if s]
        parts = [s for s in parts if s not in ['https','http','www','com','htm','html','asp','jsp','aspx','php','org','net']]
        urls.append(parts)
    f.close()
    return urls

def getrawDocs(fileName):
    docs = []
    titles = []
    f =  open(fileName,'r')
    #f = codecs.open(fileName, 'r',encoding='utf-8')
    #i = 0
    for line in f:
        line = line[:-1]       
        webpage = open(line,'r').read()
        #print line
        soup = BeautifulSoup(webpage)
        #t = soup.html.head.title
        t = soup.title
        if (t != None):
            if t.string != None:
                titles.append(t.string.split(' '))
            else:
                titles.append([])
        else:
            titles.append([])
        comments = soup.findAll(text=lambda text:isinstance(text,Comment))
        [comment.extract() for comment in comments]
        text_nodes = soup.findAll(text=True)
        visible_text = filter(visible, text_nodes)
        text = ''.join(visible_text)
        #print line
        #webpage = codecs.open(line, 'r',encoding='utf-8').read()
        #text = nltk.clean_html(webpage)
        docs.append(text)        
    f.close()
    return docs,titles

def getSeedURLs(fileName):
    seeds = []
    f = open(fileName,"r")
    for line in f:
        seeds.append(line[:-1])
    return seeds

def getTokenizedDoc(doc):
    #docs_tokens=[]
    stemmer = PorterStemmer()
    tokenizer = WordPunctTokenizer()
    stopwords = nltk.corpus.stopwords.words('english')
    
    tokens = tokenizer.tokenize(doc)
    clean = [token for token in tokens if token.isalnum()]
    clean = [token.lower() for token in clean if token.lower() not in stopwords] 
    #clean = [token for token in clean if len(token) > 2]
    final = [stemmer.stem(word) for word in clean]
    #docs_tokens.append(final)
    return final

def getTokenizedDocs(docs):
    docs_tokens=[]
    for doc in docs:
        final = getTokenizedDoc(doc)
        docs_tokens.append(final)
    return docs_tokens

# def getTokenizedDocs(docs):
#     docs_tokens=[]
#     stemmer = PorterStemmer()
#     tokenizer = WordPunctTokenizer()
#     stopwords = nltk.corpus.stopwords.words('english')
#     for text in docs:
#         tokens = tokenizer.tokenize(text)
#         clean = [token for token in tokens if token.isalnum()]
#         clean = [token.lower() for token in clean if token.lower() not in stopwords] 
#         clean = [token for token in clean if len(token) > 2]
#         final = [stemmer.stem(word) for word in clean]
#         docs_tokens.append(final)
#     return docs_tokens

def getTokens(doc): 
    #global stemmer
    stemmer = PorterStemmer()
    tokenizer = WordPunctTokenizer()
    stopwords = nltk.corpus.stopwords.words('english')
      
    webpage = open(doc,'r').read()
    text = nltk.clean_html(webpage)
    #tokens = nltk.word_tokenize(text)
    tokens = tokenizer.tokenize(text)
    clean = [token.lower() for token in tokens if token.lower() not in stopwords]
    final = [stemmer.stem(word) for word in clean]
    return final

def getDocs(fileName):
    
    docs = []
    
    f = open(fileName,'r')

    for line in f:
        line = line[:-1]
        words = getTokens(line)
        docs.append((line,words))        
    f.close()
    return docs

def getLabels(docs,topicKeywords):
    labels = []
    for doc in docs:
        result = checkRelevance(doc, topicKeywords)
        if result > 3:
            labels.append(1)
        else:
            labels.append(0)
    return labels

def getTrainingData(docs,topicKeywords):
    trainingData = {
    "positiveDocs" : [],
    "negativeDocs" : [],
    "numOfPos" : 0,
    "numOfNeg" : 0
    }
    for doc in docs:
        result = checkRelevance(doc[1], topicKeywords)
        #if result == True:
        if result > 1:
            trainingData['positiveDocs'].append(doc)
            trainingData['numOfPos'] += 1
        else:
            trainingData['negativeDocs'].append(doc)
            trainingData['numOfNeg'] += 1
    return trainingData

def downloadPages():
    #urls_Words = []
    data = ""
    urls_fileName = "urls.txt"
    fw = open("urls_tokens.txt","w")
    #output_file = "urls-i.html"
    f = open(urls_fileName,'r')
    for line in f:
        line = line[:-1]
        words = preprocess(line)
        if type(words) is list:    
            data = " ".join(words)
        #try:
            #s = json.dumps(data)
        #except UnicodeDecodeError:
            #print words
            
        #urls_Words.append(s)
        fw.write(data+"\n")
    f.close()
    fw.close()

def checkRelevance(pageWords, topicWords):
    
    presence = [word in pageWords for word in topicWords]
    res = []
    for elem in presence:
        if elem:
            res.append(1)
        else:
            res.append(0)
    #m = reduce(lambda x,y: x or y, presence)
    #return m
    m = reduce(lambda x,y: x +y,res)
    return m

def getDomainStat(data):
    stat = {}
    url = ""
    for elem in data:
        #url = elem[0]
        url = elem
        ind = url.find("http")
        if ind != -1 :
            url2 = url[ind:]
            ind = url2.find("\\")
            domain = url2[ind+1:]
            ind = domain.find("\\")
            domain = domain[:ind]
            if domain not in stat:
                stat[domain] = [url]
            else:
                stat[domain].append(url)
    return stat

'''
def main():
    global stemmer
    stemmer = PorterStemmer()
    fileName = "html_files.txt"
    #topicKeywords = getTopicKeywords("manual-sikkim-earthquake-wikipedia.txt")
    
    docs = getDocs(fileName)
    #print len(docs)
    #trainingData = getTrainingData(docs,topicKeywords)
    #print trainingData['numOfPos']
    #print trainingData['numOfNeg']
    #stats = getDomainStat(trainingData["positiveDocs"])
    
    for k,v in stats.iteritems():
        print k + " " + str(len(v))


if __name__ == "__main__":
    main()
'''
