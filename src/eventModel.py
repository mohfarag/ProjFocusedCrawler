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
from eventUtils import getEventModelInsts
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
    
    
    def buildEventModel(self,seedURLs,topK=10,intersectionTh=1):
        corpus = Collection(seedURLs)
        #sortedTokensFreqs = corpus.getWordsFrequencies()
        sortedToksTFDF = corpus.getIndicativeWords()
        print sortedToksTFDF
        sortedImptSents = corpus.getIndicativeSentences(topK,intersectionTh)
        # Get Event Model
        eventModelInstances = getEventModelInsts(sortedImptSents)
        self.entities['Disaster'] = sortedToksTFDF[:topK]
        for e in eventModelInstances:
            if 'LOCATION' in e:
                self.entities['LOCATION'].extend( e['LOCATION'])
            elif 'DATE' in e:
                self.entities['DATE'].extend( e['DATE'])
        
        entityList = []
        self.entitiesSet = {}
        if self.entities.has_key("Disaster"):
            for k in self.entities:
                entityList.extend( self.entities[k])
                entityL = self.entities[k]
                ltext = " ".join(entityL)
                tokens = getTokenizedDoc(ltext)
                locs = set(tokens)
                self.entitiesSet[k] = [i for i in locs]
                self.entities[k] = [i for i in locs]
        
        
        self.entity_set = set(entityList)
        #self.entity_set = set(tokens)
        print self.entity_set

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
        #disasters=["attack","kill"]
        disasters=self.entities["Disaster"]
        #disasters = [self.stemWord(d) for d in disasters]
        
        text = docText.split("\n")
        text = [elem for elem in text if len(elem)>2]
        sentences = []
        
        #tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        
        for elem in text:
            #sentences.extend(tokenizer.tokenize(elem))
            sentences.extend(nltk.sent_tokenize(elem))
        #sentences = tokenizer.tokenize(all_text.strip())
        
        entity_names = []    
        """
        Run the Stanford NER in server mode using the following command:
        java -mx1000m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer -loadClassifier classifiers/english.muc.7class.distsim.crf.ser.gz -port 8080 -outputFormat inlineXML
        """
        
        tagger = ner.SocketNER(host='localhost',port=8080)
        #sentence = " I live in Egypt. and it will be the greatest country on Friday Feb 22, 2015"
        #sentence_entities = tagger.get_entities(sentence)
        #print sentence_entities
        
        for sentence in sentences:
            sentence_entities = tagger.get_entities(sentence)
            if sentence_entities:
                #words = nltk.word_tokenize(sentence)
                words = getTokenizedDoc(sentence)
                if len(words) > 1:
                    #names = [n[0] for n in nltk.pos_tag(words) if n[1].startswith('N')]                    
                    #for n in names:
                    for n in words:
                        #if self.stemWord(n) in disasters:
                        if n in disasters:
                        #if lemmatize(n) in disasters:
                            if sentence_entities.has_key('Disaster'):
                                #sentence_entities["Disaster"].append(self.stemWord(n))
                                sentence_entities["Disaster"].append(n)
                            else:
                                sentence_entities["Disaster"] = [n]
                    #print (sentence,sentence_entities)
                    #print sentence_entities
                    entity_names.append((sentence,sentence_entities))    
        return entity_names
    
    
    
    def calculate_similarity(self,doc):
        tokens = getTokenizedDoc(doc)
        doc_set = set(tokens)
        #doc_set = set(doc.split(" "))
        
        scores = []
        #intersect = len(doc_set & self.entity_set)
        #intersect = len(doc_set & self.entitiesSet["Disaster"])
        
        for k in self.entitiesSet:
                intersect = len(doc_set & self.entitiesSet[k])
                score = intersect * 1.0 / len(self.entitiesSet[k])
                if k == "Disaster":
                    if intersect == 0:
                        return 0
                    
                    score = score * self.dw
                else:
                    score = score * self.ltw
                
                scores.append(score)
        
        score = sum(scores)
        #score = intersect * 1.0 /len(self.entity_set)       
        return score
    
    def calculate_score(self,doc=""):
        entities = self.webpageEntities(doc)       
        if len(entities) > 1:
        #if entities.has_key("Disaster"):
            uentities = {"Disaster":[],"LOCATION":[],"DATE":[]}
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
    #             for k in uentities:            
    #                 tempSet = set(uentities[k])
    #                 #tempList = [i for i in tempSet]
    #                 uentities[k] = [i for i in tempSet]
            webpageEntities = [] 
            webpageSets = {}   
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
                    #tempList = [i for i in tempSet]
                uentities[k] = [i for i in locs]
            scores = []
            for k in webpageSets:
                intersect = len(webpageSets[k] & self.entitiesSet[k])
                #print intersect
                score = intersect * 1.0 / len(self.entitiesSet[k])
#                 if k == "Disaster":
#                     score = score * self.dw
#                 else:
#                     score = score * self.ltw
                scores.append(score)
                #print webpageSets[k]
            #print scores
            
            #score = sum(scores) / 3.0
            score = sum(scores)
            #print score
            #if score > 1.0:
            #    score = 1.0
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