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
from Filter import getTokenizedDocs, getTokenizedDoc, getSeedURLs
from zss import simple_distance, Node

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
    """
    def main_old():
        disasters=["earthquake","fire","floods","typhoon","tornado","cyclone","hurricane","shooting","bombing","blast"]
        disasters = [stemWord(d) for d in disasters]
        #disasters = [lemmatize(d) for d in disasters]
        all_text = getTextFromWebpage("http://www.reuters.com/article/2013/12/30/us-russia-blast-trolley-idUSBRE9BT03N20131230")
        text = all_text.split("\n")
        text = [elem for elem in text if len(elem)>2]
        sentences = []
        
        #tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        
        for elem in text:
            #sentences.extend(tokenizer.tokenize(elem))
            sentences.extend(nltk.sent_tokenize(elem))
        #sentences = tokenizer.tokenize(all_text.strip())
        
        entity_names = []    
        
        #Run the Stanford NER in server mode using the following command:
        #java -mx1000m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer -loadClassifier classifiers/english.muc.7class.distsim.crf.ser.gz -port 8080 -outputFormat inlineXML
        
        
        tagger = ner.SocketNER(host='localhost',port=8080)
        for sentence in sentences:
            sentence_entities = tagger.get_entities(sentence)
            if sentence_entities:
                words = nltk.word_tokenize(sentence)
                if len(words) > 1:
                    names = [n[0] for n in nltk.pos_tag(words) if n[1].startswith('N')]
                    for n in names:
                        if stemWord(n) in disasters:
                        #if lemmatize(n) in disasters:
                            if sentence_entities.has_key('Disaster'):
                                sentence_entities["Disaster"].append(n)
                            else:
                                sentence_entities["Disaster"] = [n]
                    print (sentence,sentence_entities)
                    #print sentence_entities
                    entity_names.append(sentence_entities)
    """
#     def buildEventModel(self,urls=[]):
#         eventText = ""
#         for url in urls:
#             text = self.getTextFromWebpage(url)
#             eventText = eventText + "\n" + text
#         eventEntities = self.webpageEntities(eventText)
#         self.entities = {"Disaster":[],"LOCATION":[],"DATE":[]}
#         entityList = []
#         for sent in eventEntities:
#             dictval = sent[1]
#             if dictval.has_key("Disaster"):
#                 for k in dictval:
#                     #entityList.extend(dictval[k])
#                     if k in ["LOCATION","Disaster","DATE"]:
#                         if self.entities.has_key(k):
#                             self.entities[k].extend(dictval[k])
#                         else:
#                             self.entities[k] = []
#                             self.entities[k].extend(dictval[k])
#         
#         for k in self.entities:            
#             tempSet = set(self.entities[k])
#             tempList = [i for i in tempSet]
#             self.entities[k] = [i for i in tempList]            
#             entityList.extend(tempList)                        
#         #self.eventTreeModel,self.modelSize = self.getEventTree(self.eventEntities)
#         self.eventTreeModel,size = self.getEventTree([("",self.entities)])
#         self.modelSize = size
#         
# #         entityList = []
# #         for entity in self.eventEntities:
# #             val = entity[1]
# #             if val.has_key("Disaster"):
# #                 for k in val:
# #                     entityList.extend(val[k])
#         text = " ".join(entityList)
#         tokens = getTokenizedDoc(text)
#         self.entity_set = set(tokens)
#         print self.entity_set        

    def buildEventModel(self,urls=[]):
        #,"fire","gas", "leak"
        #self.entities = {"Disaster":["attack","kill","dead","school"],"LOCATION":["DAMATURU","Yobe","Nigeria"],"DATE":["2014","February","Tuesday"]}
        #self.entities = {"Disaster":["blast","explosion","collapse","explode"],"LOCATION":["East Harlem","Park Avenue","Manhattan","New York"],"DATE":["March 12, 2014","Wednesday"]}
        self.entities = {"Disaster":["blast","explosion","collapse"],"LOCATION":["East Harlem","Manhattan","New York"],"DATE":["March, 2014","Wednesday"]}
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
        
        tagger = ner.SocketNER(host='localhost',port=8000)
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
    
    def getEventTree_Separete(self,entities):
        eventTree = Node("eventRoot")
        for p in entities:
            e = p[1]
            if "Disaster" in e.keys():
                for k in e.keys():
                    s = Node(k)
                    for l in e[k]:
                        n = Node(l)
                        s.addkid(n)
                    eventTree.addkid(s) 
        return eventTree
    
    
    def getEventTree(self,entities):
        size = 0
        eventTree = Node("eventRoot")
        l = Node("Location")
        d = Node("Date")
        t = Node("Disaster")
        eventTree.addkid(l)
        eventTree.addkid(d)
        eventTree.addkid(t)
        for p in entities:
            e = p[1]
            if "Disaster" in e.keys():
                for k in e.keys():
                    size+= len(e[k])
                    if k == "LOCATION":
                        for i in e[k]:
                            n = Node(i)
                            l.addkid(n)
                    elif k == "DATE":
                        for j in e[k]:
                            n = Node(j)
                            d.addkid(n)
                    else:
                        for f in e[k]:
                            n = Node(f)
                            t.addkid(n) 
        return eventTree,size
    
    def calculate_similarity(self,doc):
        tokens = getTokenizedDoc(doc)
        doc_set = set(tokens)
        #doc_set = set(doc.split(" "))
        intersect = len(doc_set & self.entity_set)
        #union = len(doc_set | self.entity_set)
        score = intersect * 1.0 /len(self.entity_set)       
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
            #webpageEntitiesSet = set(webpageEntities)   
#             locs = uentities["LOCATION"]
#             ltext = " ".join(locs)
#             tokens = getTokenizedDoc(ltext)
#             locs = set(tokens)
#             uentities["LOCATION"] = [i for i in locs]           
                #entityList.extend(tempList)    
            #print uentities
            #print webpageEntitiesSet
            #pageEventTree,size = self.getEventTree([("",uentities)])
            scores = []
            for k in webpageSets:
                intersect = len(webpageSets[k] & self.entitiesSet[k])
                score = intersect * 1.0 / len(self.entitiesSet[k])
                scores.append(score)
                print webpageSets[k]
            print scores
            score = sum(scores) / 3.0
            
            

            #distance = simple_distance(self.eventTreeModel,pageEventTree)
#             maxS = self.modelSize
#             if  size > maxScore:
#                 maxScore = size
            #s = distance * 1.0 / self.modelSize
            #s = distance * 1.0 / (self.modelSize + size)
            #print distance
            #score = 1 - s
            if score < 0:
                score = 0.0
            
        else:
            score = self.calculate_similarity(doc)
        
        #score = 1.0/distance
        return score
    
    
    def calculate_score(self,doc=""):
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
            
#             for k in uentities:            
#                 tempSet = set(uentities[k])
#                 #tempList = [i for i in tempSet]
#                 uentities[k] = [i for i in tempSet]
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
#             locs = uentities["LOCATION"]
#             ltext = " ".join(locs)
#             tokens = getTokenizedDoc(ltext)
#             locs = set(tokens)
#             uentities["LOCATION"] = [i for i in locs]           
                #entityList.extend(tempList)    
            #print uentities
            print webpageEntitiesSet
            #pageEventTree,size = self.getEventTree([("",uentities)])
            
            intersect = len(webpageEntitiesSet & self.entity_set)
            score = intersect * 1.0 / len(self.entity_set)

            #distance = simple_distance(self.eventTreeModel,pageEventTree)
#             maxS = self.modelSize
#             if  size > maxScore:
#                 maxScore = size
            #s = distance * 1.0 / self.modelSize
            #s = distance * 1.0 / (self.modelSize + size)
            #print distance
            #score = 1 - s
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