'''
Created on Feb 18, 2014

@author: mohamed
'''
import urllib2
from bs4 import BeautifulSoup,Comment
#import nltk_contrib
from nltk import stem
import math
#import nltk.data
from collection import Collection
import eventUtils
#from eventUtils import getEventModelInsts, getSentences, getEntities, getTokens, getIntersection
from Filter import getTokenizedDoc
#from eventUtils import getFreq
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
    
    def __init__(self,topK=3,th=1):
        self.entities = {}
        self.topK=topK
        self.intersectionTh=th
    
    def getEntitiesFreq(self,entityList):
        el = [e.lower() for e in entityList]
        
        entitiesWords = []
        for w in el:
            p = w.split()
            if len(p)>1:
                entitiesWords.extend(p)
            else:
                entitiesWords.append(w)
        s = eventUtils.getFreq(entitiesWords)
        s = eventUtils.getSorted(s.items(), 1)
        return s
        
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
    
    
    def buildEventModel(self,keywordsTh, seedURLs):
        
        corpus = Collection(seedURLs)
        
        #NoTFDF
        sortedToksTFIDF = corpus.getIndicativeWords()
        
        self.toksTFIDFDic = dict(sortedToksTFIDF)
        #print sortedToksTFDF
        
        #sortedImptSents = corpus.getIndicativeSentences(self.topK,self.intersectionTh)
        sortedImptSents = corpus.getIndicativeSentences(keywordsTh,self.intersectionTh)
        for s in sortedImptSents[:self.topK]: 
            print s 
        # Get Event Model
        eventModelInstances = eventUtils.getEventModelInsts(sortedImptSents)
        #print eventModelInstances[:self.topK]
        
        self.entities['LOCATION']= []
        self.entities['DATE'] = []
        self.entities['Topic']=[]
        
        for e in eventModelInstances:
            if 'LOCATION' in e:
                self.entities['LOCATION'].extend( e['LOCATION'])
            elif 'DATE' in e:
                self.entities['DATE'].extend( e['DATE'])
            self.entities['Topic'].extend(e['Topic'])
        
        entitiesFreq = {}
        entitiesFreq['LOCATION'] = self.getEntitiesFreq(self.entities['LOCATION'])
        entitiesFreq['DATE'] = self.getEntitiesFreq(self.entities['DATE'])
        entitiesFreq['Topic'] = self.getEntitiesFreq(self.entities['Topic'])
        
        
        if self.topK < len(entitiesFreq['Topic']):
            entitiesFreq['Topic'] = entitiesFreq['Topic'][:self.topK]
        self.entities['Topic'] = dict(entitiesFreq['Topic'])
        print entitiesFreq['Topic']
        
        filteredDates = []
        months = ['jan','feb','mar','apr','aug','sept','oct','nov','dec','january','february','march','april','may','june','july','august','september','october','november','december']
        for d,v in entitiesFreq['DATE']:
            if d.isdigit() and len(d) == 4:
                filteredDates.append((d,v))
            elif d.lower() in months:
                filteredDates.append((d,v))
        entitiesFreq['DATE']=filteredDates
        
        llen = 5
        dlen = 5
        #l = [k for k,_ in entitiesFreq['LOCATION']]
        s = len(entitiesFreq['LOCATION'])
        
        if llen < s:
            s = llen
        t = entitiesFreq['LOCATION'][:s]
        print t
        self.entities['LOCATION'] = dict(t)
               
        #d = [k for k,_ in entitiesFreq['DATE']]
        s = len(entitiesFreq['DATE'])
        if dlen < s:
            s = dlen
        self.entities['DATE'] = dict(entitiesFreq['DATE'][:s])
        print entitiesFreq['DATE'][:s]
        
        
        #locDate = [k for k,_ in entitiesFreq['LOCATION']] + [m for m,_ in entitiesFreq['DATE']]
        
        #locDate = eventUtils.getTokens(' '.join(locDate))
        
        '''
        ntopToks = []
        topToks = [k for k,_ in entitiesFreq['Topic']]
        for tok in topToks:
            if tok not in locDate:
                ntopToks.append(tok)
        topToks = ntopToks
        
        if self.topK < len(topToks):
            topToks =  topToks[:self.topK]
        #print "Disaster: ", topToks
        
        
        topToksDic = {}
        for t in topToks:
            topToksDic[t] = self.toksTFIDFDic[t]
        #self.entities['Disaster'] = set(topToks)
        self.entities['Topic'] = topToksDic
        
        #print self.entities
        print topToksDic
        '''
        #self.vecs = {}
        self.scalars = {}
        for k in self.entities:
            ekv = self.entities[k]
            '''
            if k == 'Disaster':
                ev = [1+math.log(e*v) for e,v in ekv.values()]
            else:
                ev = [1+math.log(e) for e in ekv.values()]
            '''
            #NoTFDF
            ev = [1+math.log(e) for e in ekv.values()]
            #self.vecs[k] = ev
            self.scalars[k] = self.getScalar(ev)
    
    def buildEventModel_old(self,seedURLs):
        
        corpus = Collection(seedURLs)
        #sortedTokensFreqs = corpus.getWordsFrequencies()
        sortedToksTFDF = corpus.getIndicativeWords()
        print sortedToksTFDF
        sortedImptSents = corpus.getIndicativeSentences(self.topK,self.intersectionTh)
        # Get Event Model
        eventModelInstances = eventUtils.getEventModelInsts(sortedImptSents)
        #topToks = [k for k,_ in sortedToksTFDF]
        #if self.topK < len(topToks):
        #    topToks =  topToks[:self.topK]
        #self.entities['Disaster'] = set(topToks)
        
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
            l = l[:3]
        self.entities['LOCATION'] = set(l)
        
        d = [k for k,_ in entitiesFreq['DATE']]
        if self.topK < len(d):
            #d = d[:self.topK]
            d = d[:3]
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
        
        locDate = list(self.entities['LOCATION']) + list(self.entities['DATE'])
        locDate = eventUtils.getTokens(' '.join(locDate))
        
        ntopToks = []
        topToks = [k for k,_ in sortedToksTFDF]
        for tok in topToks:
            if tok not in locDate:
                ntopToks.append(tok)
        topToks = ntopToks
        if self.topK < len(topToks):
            topToks =  topToks[:self.topK]
        self.entities['Topic'] = set(topToks)
        
        
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
        disasters=set(self.entities["Topic"].keys())
        
        sentences = eventUtils.getSentences(docText)
        webpageEnts =[]
        for sent in sentences:
            sentToks = eventUtils.getTokens(sent)
            if len(sentToks) > 100:
                continue
            intersect = eventUtils.getIntersection(disasters, sentToks)
            if len(intersect) > self.intersectionTh:
                #print intersect
                sentEnts = eventUtils.getEntities(sent)[0]
                if sentEnts.has_key('LOCATION') or sentEnts.has_key('DATE'):
                    sentEnts['Topic'] = intersect
                    webpageEnts.append((sent,sentEnts))
        
        return webpageEnts
    
    def webpageEntities_old(self,docText=""):
        disasters=self.entities["Topic"]
        
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
                if sentEnts.has_key('LOCATION') or sentEnts.has_key('DATE'):
                    sentEnts['Topic'] = intersect
                    webpageEnts.append((sent,sentEnts))
        #entities = getEntities(impSentences)
        #webpageEnts = zip(impSentences,entities)
        
        return webpageEnts
    
    def calculate_similarity(self,doc):
        eDisDic = self.entities['Topic']
        
        locToks = self.entities['LOCATION'].keys()
        locToks = eventUtils.getStemmedWords(locToks)
        locDic = dict(zip(locToks,self.entities['LOCATION'].values()))
        
        dToks = self.entities['DATE'].keys()
        dToks = eventUtils.getStemmedWords(dToks)
        dDic = dict(zip(dToks,self.entities['DATE'].values()))
        
        tokens = eventUtils.getTokens(doc)
        tokensDic = eventUtils.getFreq(tokens)
        wv = [1+math.log(e) for e in tokensDic.values()]
        wvScalar = self.getScalar(wv)
        scores = []
        
        ksd = 0    
        for i in tokensDic:
            if i in eDisDic:
                ksd += (1+math.log(eDisDic[i]))* (1+math.log(tokensDic[i]))
        if ksd > 0:
            ksd = float(ksd)/(self.scalars['Topic'] * wvScalar)
        else:
            ksd = 0
        if ksd == 0:
            return 0
        scores.append(ksd)
        ksl = 0    
        for i in tokensDic:
            if i in locDic:
                ksl += (1+math.log(locDic[i]))* (1+math.log(tokensDic[i]))
        if ksl > 0:
            ksl = float(ksl)/(self.scalars['LOCATION'] * wvScalar)
            
        else:
            ksl = 0
        scores.append(ksl)
        
        ks = 0    
        for i in tokensDic:
            if i in dDic:
                ks += (1+math.log(dDic[i]))* (1+math.log(tokensDic[i]))
        if ks > 0:
            ks = float(ks)/(self.scalars['DATE'] * wvScalar)
            
        else:
            ks = 0
        scores.append(ks)
        
        score = sum(scores) / 3.0
        return score
    
    def calculate_similarity_intersect(self,doc):
        #tokens = getTokenizedDoc(doc)
        tokens = eventUtils.getTokens(doc)
        doc_set = set(tokens)
        
        scores = []
        
        for k in self.entities:
            entSet = set(self.entities[k].keys())
            intersect = len(doc_set & entSet)
            union = len(doc_set | entSet)
            if k == "Topic":
                if intersect == 0:
                    return 0
            
            score = intersect * 1.0 / union #len(self.entities[k])
            
            scores.append(score)
        
        score = sum(scores)/3.0     
        return score
    
    def extractWebpageEventModel(self, text):
        webpageEventModel = {}
        
        entities = self.webpageEntities(text)
        if len(entities) > 1:
            for sent in entities:
                dictval = sent[1]
                for k in dictval:
                    if k in ["LOCATION","Topic","DATE"]:
                        if webpageEventModel.has_key(k):
                            webpageEventModel[k].extend(dictval[k])
                        else:
                            webpageEventModel[k] = []
                            webpageEventModel[k].extend(dictval[k])
            for k in webpageEventModel:
                if k in ["LOCATION","DATE"]:
                    webpageEventModel[k] = dict(self.getEntitiesFreq(webpageEventModel[k]))
            
            webpageToks = eventUtils.getTokens(text)
            webpageDis = set(webpageEventModel['Topic'])
            webpageDisDic = {}
            for wd in webpageDis:
                webpageDisDic[wd]=webpageToks.count(wd)
            webpageEventModel['Topic']=webpageDisDic
            
            
        return webpageEventModel
    
    def extractWebpageEventModel_old(self, text):
        webpageEventModel = {}
        entities = self.webpageEntities(text)
        if len(entities) > 1:
            for sent in entities:
                dictval = sent[1]
                if dictval.has_key("Topic"):
                    
                    for k in dictval:
                        if k in ["LOCATION","Topic","DATE"]:
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
    
    def getScalar(self,doc_tfidf):
        total = 0
        for i in range(len(doc_tfidf)):
            total += doc_tfidf[i] * doc_tfidf[i]
        return math.sqrt(total)
    
    def calculate_score_intersect(self,doc=""):
        uentities = self.extractWebpageEventModel(doc)
        if uentities and uentities.has_key('Topic'):
            scores = []
            for k in uentities:
                entSet = set(self.entities[k].keys())
                intersect = len(uentities[k] & entSet)
                union = len(uentities[k] | entSet)
                score = intersect * 1.0 / union#len(self.entities[k])
                scores.append(score)
            score = sum(scores)/3.0
        else:
            score = self.calculate_similarity(doc)
        return score
    
    def calculate_score(self,doc,m):
        
        if m == 'W':
            uentities = self.extractWebpageEventModel(doc)
            scores = []
            for k in uentities:
                #print 'yes'
                ks = 0
                
                ekv = self.entities[k]
                wkv = uentities[k]
                wv = [1+math.log(e) for e in wkv.values()]
                wvscalar = self.getScalar(wv)
                    
                for i in ekv:
                    if i in wkv:
                        ks += (1+math.log(ekv[i]))* (1+math.log(wkv[i]))
                if ks > 0:
                    ks = float(ks)/(self.scalars[k] * wvscalar)
                    
                else:
                    ks = 0
                #scores.append(0.25*ks)
                scores.append(ks)
            score = sum(scores)/3.0
            #score = sum(scores)
        else:
            #print 'no'
            score = self.calculate_similarity(doc)
        return score
    
    def calculate_score_old(self,doc=""):
        uentities = self.extractWebpageEventModel(doc)
        if uentities and uentities.has_key('Topic'):
            scores = []
            for k in uentities:
                #print 'yes'
                ks = 0
                
                ekv = self.entities[k]
                wkv = uentities[k]
                wv = [1+math.log(e) for e in wkv.values()]
                wvscalar = self.getScalar(wv)
                '''
                if k == 'Disaster':
                    for i in ekv:
                        if i in wkv:
                            ks += (1+math.log(ekv[i][0]*ekv[i][1]))* (1+math.log(wkv[i]))
                    if ks > 0:
                        #ev = [1+math.log(e) for e,_ in ekv.values()]
                        
                        #ks = float(ks)/(self.getScalar(ev) * wvscalar)
                        ks = float(ks)/(self.scalars[k] * wvscalar)
                        
                    else:
                        ks = 0
                #if k == 'Disaster':
                    #scores.append(0.5*ks)
                    scores.append(ks)
                else:
                '''    
                for i in ekv:
                    if i in wkv:
                        ks += (1+math.log(ekv[i]))* (1+math.log(wkv[i]))
                if ks > 0:
                    #ev = [1+math.log(e) for e in ekv.values()]
                    
                    #ks = float(ks)/(self.getScalar(ev) * wvscalar)
                    ks = float(ks)/(self.scalars[k] * wvscalar)
                    
                else:
                    ks = 0
                #scores.append(0.25*ks)
                scores.append(ks)
            score = sum(scores)/3.0
            #score = sum(scores)
        else:
            #print 'no'
            score = self.calculate_similarity(doc)
        return score
    
    def calculate_score_TFDF(self,doc=""):
        uentities = self.extractWebpageEventModel(doc)
        if uentities and uentities.has_key('Topic'):
            scores = []
            for k in uentities:
                ks = 0
                
                ekv = self.entities[k]
                wkv = uentities[k]
                wv = [1+math.log(e) for e in wkv.values()]
                wvscalar = self.getScalar(wv)
                if k == 'Topic':
                    for i in ekv:
                        if i in wkv:
                            ks += (1+math.log(ekv[i][0]*ekv[i][1]))* (1+math.log(wkv[i]))
                    if ks > 0:
                        #ev = [1+math.log(e) for e,_ in ekv.values()]
                        
                        #ks = float(ks)/(self.getScalar(ev) * wvscalar)
                        ks = float(ks)/(self.scalars[k] * wvscalar)
                        
                    else:
                        ks = 0
                #if k == 'Disaster':
                    #scores.append(0.5*ks)
                    scores.append(ks)
                else:
                    
                    for i in ekv:
                        if i in wkv:
                            ks += (1+math.log(ekv[i]))* (1+math.log(wkv[i]))
                    if ks > 0:
                        #ev = [1+math.log(e) for e in ekv.values()]
                        
                        #ks = float(ks)/(self.getScalar(ev) * wvscalar)
                        ks = float(ks)/(self.scalars[k] * wvscalar)
                        
                    else:
                        ks = 0
                    #scores.append(0.25*ks)
                    scores.append(ks)
            #score = sum(scores)/3.0
            score = sum(scores)
        else:
            score = self.calculate_similarity(doc)
        return score
    
    def calculate_score_veryold(self,doc=""):
        uentities = self.extractWebpageEventModel(doc)
        if uentities and uentities.has_key('Topic'):
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
            uentities = {"Topic":[],"LOCATION":[],"DATE":[]}
            #entityList = []
            for sent in entities:
                dictval = sent[1]
                if dictval.has_key("Topic"):
                    for k in dictval:
                        #entityList.extend(dictval[k])
                        if k in ["LOCATION","Topic","DATE"]:
                            if uentities.has_key(k):
                                uentities[k].extend(dictval[k])
                            else:
                                uentities[k] = []
                                uentities[k].extend(dictval[k])
            webpageEntities = []    
            for k in uentities:
                   
                temp = uentities[k]
                ltext = " ".join(temp)
                
                if k != "Topic":
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
