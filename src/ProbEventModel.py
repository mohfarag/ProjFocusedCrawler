'''
Created on Apr 9, 2015

@author: mmagdy
'''

import eventUtils
import math,sys
import logging

logging.basicConfig(filename='probEventModellogging.log',level=logging.DEBUG)
log = logging.getLogger(__name__)



class ProbEventModel:
    
    def getCollectionDocs(self,inputURLs):
        
        #f = open(inputURLs)
        #ls = f.readlines()
        #f.close()
        #ls = [l.strip() for l in ls]
        ls = inputURLs
        docsL = eventUtils.getWebpageText(ls)
        return docsL
    
    def buildProbEventModel(self,urlsList,topK):
        
        docsList = self.getCollectionDocs(urlsList)
        t = ''
        #docsTotalFreqs=[]
        docsEntities=[]
        docsEntitiesFreq = []
        entitiesProb = {}
        
        # Convert each doc to tokens, locations, dates lists and their corresponding frequency distributions
        # Also produces the total frequency for each document of each list (tokens, locations, and dates)
        for doc in docsList:
            
            if doc.has_key('text'):
                t = doc['text']
                if doc.has_key('title'):
                    t =doc['title']+ " "+t
            if t:
                #print 'Reading ' + t[:100]
                ents = eventUtils.getEntities(t)[0]
                docEnt = {}
                docEnt['LOCATION']={}
                if 'LOCATION' in ents:
                    docEnt['LOCATION'] =  ents['LOCATION']
                docEnt['DATE']={}
                if 'DATE' in ents:
                    docEnt['DATE'] = ents['DATE']
                toks = eventUtils.getTokens(t)
                docEnt['Topic'] = toks
                docsEntities.append(docEnt)
                
                docEntFreq = {}
                #docTotals = {}
                for k in docEnt:
                    docEntFreq[k] = eventUtils.getFreq(docEnt[k])
                    #totalFreq = sum([v for _,v in docEntFreq[k].items()])
                    
                    #docTotals[k] = totalFreq
                docsEntitiesFreq.append(docEntFreq)
                #docsTotalFreqs.append(docTotals)
        
        # Collection-level frequency for each entity(tokens, locations, dates)
        
        #Calculating prob for each item in each entity lists (tokens, locations, and dates) as 
        # freq of item in all docs / total freq of all terms in that list
        entitiesProb['LOCATION']={}
        entitiesProb['DATE']={}
        entitiesProb['Topic']={}
        
        for docEntFreq in docsEntitiesFreq:
            for entity in docEntFreq:
                for val in docEntFreq[entity]:
                    if val in entitiesProb[entity]:
                        entitiesProb[entity][val] += docEntFreq[entity][val]
                    else:
                        entitiesProb[entity][val] = docEntFreq[entity][val]
        
        for ent in entitiesProb:
            allvalsFreq = sum([v for _,v in entitiesProb[ent].items()])
            for k in entitiesProb[ent]:
                #entitiesProb[ent][k] = (1.0 + (entitiesProb[ent][k] *1.0)) / (docsTotalFreqs[ent] + allDocsTotal[ent])
                
                entitiesProb[ent][k] = (1.0 + (entitiesProb[ent][k] *1.0)) / (len(entitiesProb[ent]) + allvalsFreq)
                
            
        #self.probEvtModel = entitiesProb
        
        mle =  self.getMLEEventEntities(entitiesProb,10)
        for k in mle:
            print k, mle[k]
            
        
        self.probEvtModel = {}
        for k in mle:
            self.probEvtModel[k] = dict(mle[k])#entitiesProb[k][:topK]
        
        self.eDisDic = self.probEvtModel['Topic']
        
        
        locToks = self.probEvtModel['LOCATION'].keys()
        locToks = eventUtils.getStemmedWords(locToks)
        self.locDic = dict(zip(locToks,self.probEvtModel['LOCATION'].values()))
        
    
        dToks = self.probEvtModel['DATE'].keys()
        dToks = eventUtils.getStemmedWords(dToks)
        self.dDic = dict(zip(dToks,self.probEvtModel['DATE'].values()))
        
        
        
        return docsEntities, entitiesProb
    
    def getMLEEventEntities(self,pem,topK):
        mleEnts = {}
        for k in pem:
            d = pem[k]
            ds = eventUtils.getSorted(d.items(), 1)
            if topK:
                mleEnts[k] = ds[:topK]
            else:
                mleEnts[k] = ds
        return mleEnts
    
    def getDocProb(self,docEnt):
        #docsProbs = []
        
        #for docEnt in docEnts:
        docProb = {}
        for k in docEnt:
            #total = 1
            total = 0.0
            docProb[k]={}
            for e in docEnt[k]:
                if e in self.probEvtModel[k]:
                    p = self.probEvtModel[k][e.lower()] # * (1 + math.log(docEnt[k][e]))
                    docProb[k][e.lower()] = p
                    #total = total * p
                    total = total + math.log(p) #p 
                
            docProb[k]['Total'] = total
            
        #finalDocProb = 1
        finalDocProb = 0.0
        for k in docProb:
            #finalDocProb = finalDocProb * docProb[k]['Total']
            finalDocProb = finalDocProb + docProb[k]['Total']
        docProb['Total'] = finalDocProb
        #docsProbs.append(docProb)
        return finalDocProb #docProb
    
    
    def getDocsProb(self,docEnts):
        docsProbs = []
        
        for docEnt in docEnts:
            docProb = self.getDocProb(docEnt)
            docsProbs.append(docProb)
        return docsProbs#finalDocProb
    
    def calculate_similarity(self,doc):
        '''
        eDisDic = self.probEvtModel['Topic']
        
        if self.locDic ==[]:
            locToks = self.probEvtModel['LOCATION'].keys()
            locToks = eventUtils.getStemmedWords(locToks)
            self.locDic = dict(zip(locToks,self.probEvtModel['LOCATION'].values()))
        
        if self.dDic == []:
            dToks = self.probEvtModel['DATE'].keys()
            dToks = eventUtils.getStemmedWords(dToks)
            self.dDic = dict(zip(dToks,self.probEvtModel['DATE'].values()))
        '''
        tokens = eventUtils.getTokens(doc)
        docProb = {}
        #tokensDic = eventUtils.getFreq(tokens)
        #wv = [1+math.log(e) for e in tokensDic.values()]
        docProb['Topic'] = {}
        total = 0.0
        for t in tokens:
            if t in self.eDisDic:
                p = self.eDisDic[t]
                total = total + math.log(p)
        if total == 0.0:
            return -100
        docProb['Topic']['Total'] = total
        
        docProb['LOCATION'] = {}
        total = 0.0
        for t in tokens:
            if t in self.locDic:
                p = self.locDic[t]
                total = total + math.log(p)
        docProb['LOCATION']['Total'] = total
        
        docProb['DATE'] = {}
        total = 0.0
        for t in tokens:
            if t in self.dDic:
                p = self.dDic[t]
                total = total + math.log(p)
        docProb['DATE']['Total'] = total
        
            
        #finalDocProb = 1
        finalDocProb = 0.0
        for k in docProb:
            #finalDocProb = finalDocProb * docProb[k]['Total']
            finalDocProb = finalDocProb + docProb[k]['Total']
        docProb['Total'] = finalDocProb
        #if finalDocProb == 0.0:
        #    finalDocProb = -100.0
        return finalDocProb*-1
    
    def calculate_score(self,doc,m):
        
        #docScore = 0.0
        
        
        if m == 'W':
            docEnt = eventUtils.getEntities(doc)[0]
            docEnt['Topic'] = eventUtils.getTokens(doc)
            score = self.getDocProb(docEnt)
        else:
            
            score = self.calculate_similarity(doc)
        return score
'''
if __name__ == '__main__':
    #'Output-walterScottShooting.txt','Output-boatCapsized.txt','Output-garissa attack.txt'
    #collectionURLsFile = 'Output-germanwings_crash.txt'
    collectionURLsFile = sys.argv[1]
    topK = 10
    docsList = getCollectionDocs(collectionURLsFile)
    #log.info(len(docsList))
    pem = ProbEventModel()
    docEnts, probEventModel = pem.buildProbEventModel(docsList)
    eventUtils.saveObjUsingPickle(docEnts, collectionURLsFile.split(".")[0]+"_docEnts.p")
    eventUtils.saveObjUsingPickle(probEventModel, collectionURLsFile.split(".")[0]+"_probEventModel.p")
    #log.info(probEventModel)
    #print probEventModel
    docsProb = pem.getDocsProb(docEnts,probEventModel)
    eventUtils.saveObjUsingPickle(docsProb, collectionURLsFile.split(".")[0]+"_docsProb.p")
    #print [d['Total'] for d in docsProb]
    print docsProb
    #log.info(docsProb)
    mleEnts = pem.getMLEEventEntities(probEventModel, 0)
    eventUtils.saveObjUsingPickle(mleEnts, collectionURLsFile.split(".")[0]+"_mleEnts.p")
    #log.info(mleEnts)
    for k in mleEnts:
        print k, mleEnts[k][:10]
    #print mleEnts
    #print probEventModel.getMLE_Entites()
'''