'''
Created on Feb 18, 2014

@author: mohamed
'''
import urllib2
from bs4 import BeautifulSoup,Comment
#import nltk_contrib
import nltk
from nltk import stem
#import nltk.data
import ner
from collection import Collection
import eventUtils
#from eventUtils import getEventModelInsts, getSentences, getEntities, getTokens, getIntersection
from Filter import getTokenizedDoc
#from zss import simple_distance, Node

class EventModel:

    def visible(self,element):
            if element.parent.name in ['style', 'script', '[document]', 'head']:
                return False
            return True
    
    def extract_entity_names(self,t):
        entity_names = []
        
        if hasattr(t,'node') and t.node:
            if t.node == 'S':
                for child in t:
                    elist = self.extract_entity_names(child)
                    entity_names.extend(elist)
            else:
                e = []
                for child in t:
                    e.append(child[0])
                s = " ".join(e)
                entity_names.append((t.node,s))
        return entity_names
     
    def getTextFromWebpage(self,url):
        headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 5.1; rv:10.0.1) Gecko/20100101 Firefox/10.0.1'}
        #url = "http://www.cnn.com/2013/09/27/world/africa/kenya-mall-attack/index.html"    
        
        req = urllib2.Request(url, None, headers)
        page = urllib2.urlopen(req).read() 
        
        soup = BeautifulSoup(page)
        #title = ""
        #if soup.title:
        #    title = soup.title.string
        comments = soup.findAll(text=lambda text:isinstance(text,Comment))
        [comment.extract() for comment in comments]
        text_nodes = soup.findAll(text=True)
        visible_text = filter(self.visible, text_nodes)
        text = ''.join(visible_text)
        #all_text = title + " " + text
        return text
        #return all_text
    
    def stemWord(self,word):
        
        
        return self.stemmer.stem(word)
    
    def lemmatize(self,word):
        from nltk.stem.wordnet import WordNetLemmatizer
        lmtzr = WordNetLemmatizer()
        lematized = lmtzr.lemmatize(word)
        return lematized
    
    def __init__(self,topK=5,th=1):
        self.entities = {}
        self.topK=topK
        self.intersectionTh=th
        
    def getUniqueEntities(self,entityList):
        el = [e.lower() for e in entityList]
        
        entitiesWords = []
        for w in el:
            p = w.split()
            if len(p)>1:
                entitiesWords.extend(p)
            else:
                entitiesWords.append(w)
        s = set(entitiesWords)
        return s
    
    
    def buildEventModel(self,seedURLs):
        
        corpus = Collection(seedURLs)
        #sortedTokensFreqs = corpus.getWordsFrequencies()
        sortedToksTFDF = corpus.getIndicativeWords()
        print sortedToksTFDF
        sortedImptSents = corpus.getIndicativeSentences(self.topK,self.intersectionTh)
        # Get Event Model
        eventModelInstances = eventUtils.getEventModelInsts(sortedImptSents)
        topToks = [k for k,_ in sortedToksTFDF]
        if self.topK < len(topToks):
            topToks =  topToks[:self.topK]
        self.entities['Disaster'] = set(topToks)
        
        self.entities['LOCATION']= []
        self.entities['DATE'] = []
        for e in eventModelInstances:
            if 'LOCATION' in e:
                self.entities['LOCATION'].extend( e['LOCATION'])
            elif 'DATE' in e:
                self.entities['DATE'].extend( e['DATE'])
        
        entitiesFreq = {}
        entitiesFreq['LOCATION'] = eventUtils.getFreq(self.entities['LOCATION'])
        entitiesFreq['LOCATION'] = eventUtils.getSorted(entitiesFreq['LOCATION'].items(), 1)
        entitiesFreq['DATE'] = eventUtils.getFreq(self.entities['DATE'])
        entitiesFreq['DATE'] = eventUtils.getSorted(entitiesFreq['DATE'].items(), 1)
        
        l = [k for k,_ in entitiesFreq['LOCATION']]
        if self.topK < len(l):
            #l = l[:self.topK]
            l = l[:5]
        self.entities['LOCATION'] = set(l)
        
        d = [k for k,_ in entitiesFreq['DATE']]
        if self.topK < len(d):
            #d = d[:self.topK]
            d = d[:5]
        self.entities['DATE'] = set(d)
        '''
        locList = self.entities['LOCATION']
        locSet = set(locList)
        self.entities['LOCATION'] = [l for l in locSet]
        '''
        self.entities['LOCATION'] = self.getUniqueEntities(self.entities['LOCATION'])
        
        '''
        dateList = self.entities['DATE']
        dateSet = set(dateList)
        self.entities['DATE'] = [d for d in dateSet]
        '''
        self.entities['DATE'] = self.getUniqueEntities(self.entities['DATE']) 
        
        self.allEntities = []
        for k in self.entities:
            self.allEntities.extend(self.entities[k]) 
            
        print self.allEntities
               
    '''
    def buildEventModel(self,urls=[],dw = 0.6, ltw =0.2):
        #,"fire","gas", "leak"
        #self.entities = {"Disaster":["attack","kill","dead","school"],"LOCATION":["DAMATURU","Yobe","Nigeria"],"DATE":["2014","February","Tuesday"]}
        
        # self.entities = {"Disaster":["blast","explosion","collapse","explode"],"LOCATION":["East Harlem","Park Avenue","Manhattan","New York"],"DATE":["March 12, 2014","Wednesday"]}
               
        #old#self.entities = {"Disaster":["blast","explosion","collapse"],"LOCATION":["East Harlem","Manhattan","New York"],"DATE":["March, 2014","Wednesday"]}
        
        #self.entities = {"Disaster":["landslide","mudslide","slide","Debris"],"LOCATION":["Oso","Washington"],"DATE":["March 22, 2014","Saturday"]}
        #self.entities = {"Disaster":["shooting","killing","rampage"],"LOCATION":["Isla Vista","Santa Barbara", "California"],"DATE":["May 2014","Friday"]}
        self.entities = {"Disaster":["Hannah Graham","missing","disappear"],"LOCATION":["charlottesvil", "Virginia"],"DATE":["September","Sept","2014"]}
        
        self.dw = dw
        self.ltw = ltw
        entityList = []
        self.entitiesSet = {}
        if self.entities.has_key("Disaster"):
            for k in self.entities:
                entityL = self.entities[k]
                ltext = " ".join(entityL)
                tokens = getTokenizedDoc(ltext)
                locs = set(tokens)
                self.entitiesSet[k] = set(tokens)
                self.entities[k] = [i for i in locs]
        
        #self.eventTreeModel,self.modelSize = self.getEventTree([("",self.entities)])
        self.stemmer = stem.LancasterStemmer() 
        
        if self.entities.has_key("Disaster"):
            for k in self.entities:
                entityList.extend( self.entities[k])
        
        #text = " ".join(entityList)
        #tokens = getTokenizedDoc(text)
        
        self.entity_set = set(entityList)
        #self.entity_set = set(tokens)
        print self.entity_set        
        #print self.entities
        #return eventTreeModel
    '''
    
    def webpageEntities(self,docText=""):
        disasters=self.entities["Disaster"]
        
        sentences = eventUtils.getSentences(docText)
        #impSentences = getIndicativeSents(sentences, disasters, len(disasters), 0)
        #impSentences = []
        webpageEnts =[]
        for sent in sentences:
            sentToks = eventUtils.getTokens(sent)
            if len(sentToks) > 100:
                continue
            intersect = eventUtils.getIntersection(disasters, sentToks)
            if len(intersect) > self.intersectionTh:
                #impSentences.append(sent)
                sentEnts = eventUtils.getEntities(sent)[0]
                sentEnts['Disaster'] = intersect
                webpageEnts.append((sent,sentEnts))
        #entities = getEntities(impSentences)
        #webpageEnts = zip(impSentences,entities)
        
        return webpageEnts
    
    
    
    def calculate_similarity(self,doc):
        #tokens = getTokenizedDoc(doc)
        tokens = eventUtils.getTokens(doc)
        doc_set = set(tokens)
        
        scores = []
        
        for k in self.entities:
                intersect = len(doc_set & self.entities[k])
                if k == "Disaster":
                    if intersect == 0:
                        return 0
                score = intersect * 1.0 / len(self.entities[k])
                    
                    #score = score * self.dw
                #else:
                    #score = score * self.ltw
                
                scores.append(score)
        
        score = sum(scores)
        #score = intersect * 1.0 /len(self.entity_set)       
        return score
    
    def extractWebpageEventModel(self, text):
        webpageEventModel = {}
        entities = self.webpageEntities(text)
        if len(entities) > 1:
            for sent in entities:
                dictval = sent[1]
                if dictval.has_key("Disaster"):
                    
                    for k in dictval:
                        if k in ["LOCATION","Disaster","DATE"]:
                            if webpageEventModel.has_key(k):
                                webpageEventModel[k].extend(dictval[k])
                            else:
                                webpageEventModel[k] = []
                                webpageEventModel[k].extend(dictval[k])
            for k in webpageEventModel:
                webpageEventModel[k] = self.getUniqueEntities(webpageEventModel[k])
            
        return webpageEventModel
    '''
    def calculate_score(self,doc=""):
        entities = self.webpageEntities(doc)       
        if len(entities) > 1:
        #if entities.has_key("Disaster"):
            #uentities = {"Disaster":[],"LOCATION":[],"DATE":[]}
            uentities = {}
            empty = True
            #entityList = []
            for sent in entities:
                dictval = sent[1]
                if dictval.has_key("Disaster"):
                    empty = False
                    for k in dictval:
                        #entityList.extend(dictval[k])
                        if k in ["LOCATION","Disaster","DATE"]:
                            if uentities.has_key(k):
                                uentities[k].extend(dictval[k])
                            else:
                                uentities[k] = []
                                uentities[k].extend(dictval[k])
            if empty:
                return self.calculate_similarity(doc)
            
            webpageEntities = [] 
            webpageSets = {}   
            #Fix this by doing it as in buildEventModel
            for k in uentities:    
                temp = uentities[k]
                ltext = " ".join(temp)
                if k != "Disaster":
                    tokens = getTokenizedDoc(ltext)              
                else:
                    tokens = temp
                webpageEntities.extend(tokens)   
                locs = set(tokens)
                webpageSets[k] = set(tokens)
                uentities[k] = [i for i in locs]
                
            scores = []
            for k in webpageSets:
                intersect = len(webpageSets[k] & self.entitiesSet[k])
                score = intersect * 1.0 / len(self.entitiesSet[k])
                scores.append(score)
            score = sum(scores)
        else:
            score = self.calculate_similarity(doc)
        return score
    '''
    
    
    def calculate_score(self,doc=""):
        uentities = self.extractWebpageEventModel(doc)
        if uentities and uentities.has_key('Disaster'):
            scores = []
            for k in uentities:
                intersect = len(uentities[k] & self.entities[k])
                score = intersect * 1.0 / len(self.entities[k])
                scores.append(score)
            score = sum(scores)
        else:
            score = self.calculate_similarity(doc)
        return score
    
    
    def calculate_score2(self,doc=""):
        entities = self.webpageEntities(doc)        
        if len(entities) > 1:
            uentities = {"Disaster":[],"LOCATION":[],"DATE":[]}
            #entityList = []
            for sent in entities:
                dictval = sent[1]
                if dictval.has_key("Disaster"):
                    for k in dictval:
                        #entityList.extend(dictval[k])
                        if k in ["LOCATION","Disaster","DATE"]:
                            if uentities.has_key(k):
                                uentities[k].extend(dictval[k])
                            else:
                                uentities[k] = []
                                uentities[k].extend(dictval[k])
            webpageEntities = []    
            for k in uentities:
                   
                temp = uentities[k]
                ltext = " ".join(temp)
                
                if k != "Disaster":
                    tokens = getTokenizedDoc(ltext)              
                else:
                    tokens = temp
                webpageEntities.extend(tokens)   
                locs = set(tokens)
                    #tempList = [i for i in tempSet]
                uentities[k] = [i for i in locs]  
            webpageEntitiesSet = set(webpageEntities)
            #print webpageEntitiesSet
            
            intersect = len(webpageEntitiesSet & self.entity_set)
            score = intersect * 1.0 / len(self.entity_set)
            #print intersect
            if score < 0:
                score = 0.0
            
        else:
            score = self.calculate_similarity(doc)
        
        #score = 1.0/distance
        return score
"""
def test():
    e = EventModel()
    #urls = getSeedURLs("seedsURLs")
    e.buildEventModel()
    
    

def pageUrlEventModel(url=""):
    text = getTextFromWebpage(url)
    entities = webpageEntities(text)
    eventTree = getEventTree(entities)
    return eventTree

if __name__ == "__main__":
    test()    
"""