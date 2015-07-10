'''
Created on Mar 6, 2014

@author: mohamed
'''
# f = open("results-cleaned.txt","r")
# fw = open("results-output.txt","w")
# for line in f:
#     line = line[:-1]
#     parts = line.split(",")
#     if parts[1].strip() == "OTHER":
#         fw.write(parts[0]+ "\n") 
#     else:
#         fw.write(parts[0] + " " + parts[1]+"\n")
# f.close()
# fw.close()

import eventModel,eventUtils

#import sys, codecs
# sys.stdout.errors = 'replace'

'''
if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout, 'strict')
print u'\xad'
# print sys.stdout.encoding
# import locale
# print locale.getdefaultlocale()[1]
'''
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

def getEM_Sents(wps):
    docsEntities=[]
    docsEntitiesFreq = []
    entitiesProb = {}
    
    
    collSents = []
    #for i,wp in enumerate(wps):
    for wp in wps:
        if 'text' not in wp:
            continue
        wpContent = wp['text']+wp['title']
        wpSplit = wpContent.split('\n')
        wpFiltered = filter(None,wpSplit)
        wpContentf = '\n'.join(wpFiltered)
        sents = eventUtils.getSentences(wpContentf)
        collSents.append(sents)
    allSents = []
    for sents in collSents:
        allSents.extend(sents)
    fw = eventUtils.getFreqTokens(allSents)
    fw = [w[0] for w in fw]
    
    #collFilteredSents = []
    collEventModelInsts=[]
    for sents in collSents:
        filtEvtModelInsts = []
        for s in sents:
            sentToks = eventUtils.getTokens(s)
            cw = eventUtils.getIntersection(fw, sentToks)
            if len(cw) >= 2:
                emi = {}
                emi['TOPIC'] = list(cw)
                ents = eventUtils.getEntities(s)[0]
                if ents.has_key('LOCATION'):
                    emi['LOCATION'] = ents['LOCATION']
                    #filtEvtModelInsts.append(emi)
                if ents.has_key('DATE'):
                        #emi['TOPIC'] = cw
                    emi['DATE']=ents['DATE']
                filtEvtModelInsts.append(emi)
        collEventModelInsts.append(filtEvtModelInsts)
    '''
    #freqCollEnts={}
    words = [w for femi in collEventModelInsts for emi in femi for w in emi['TOPIC']]
    locs  = [l for femi in collEventModelInsts for emi in femi if 'LOCATION' in emi for l in emi['LOCATION']]
    dates  = [d for femi in collEventModelInsts for emi in femi if 'DATE' in emi for d in emi['DATE']]
    
    freqWords = eventUtils.getFreq(words)
    filtFreqWords = dict([(w,freqWords[w]) for w in freqWords if freqWords[w] >= 2])
    freqLocs = eventUtils.getFreq(locs)
    filtFreqLocs = dict([(w,freqLocs[w]) for w in freqLocs if freqLocs[w] >= 2])
    freqDates = eventUtils.getFreq(dates)
    filtFreqDates = dict([(w,freqDates[w]) for w in freqDates if freqDates[w] >= 2])
    
    sortedfiltFreqWords = eventUtils.getSorted(filtFreqWords.items(), 1)
    print sortedfiltFreqWords
    sortedfiltFreqLocs = eventUtils.getSorted(filtFreqLocs.items(), 1)
    print sortedfiltFreqLocs
    sortedfiltFreqDates = eventUtils.getSorted(filtFreqDates.items(), 1)
    print sortedfiltFreqDates
    '''

def getEM_Whole(wps):
    docsEntities=[]
    docsEntitiesFreq = []
    entitiesProb = {}
    
    # Convert each doc to tokens, locations, dates lists and their corresponding frequency distributions
    # Also produces the total frequency for each document of each list (tokens, locations, and dates)
    for doc in wps:
        
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
    
    mle =  getMLEEventEntities(entitiesProb,10)
    for k in mle:
        print k, mle[k]
        
    '''
    probEvtModel = {}
    for k in mle:
        probEvtModel[k] = dict(mle[k])#entitiesProb[k][:topK]
    
    eDisDic = probEvtModel['Topic']
    
    
    locToks = probEvtModel['LOCATION'].keys()
    locToks = eventUtils.getStemmedWords(locToks)
    locDic = dict(zip(locToks,probEvtModel['LOCATION'].values()))
    

    dToks = probEvtModel['DATE'].keys()
    dToks = eventUtils.getStemmedWords(dToks)
    dDic = dict(zip(dToks,probEvtModel['DATE'].values()))
    
    return docsEntities, entitiesProb
    '''
seedsFile = 'Output-boatCapsized.txt'#'Output-nepalEarthquake3.txt'#'Output-fifaArrests.txt'
seedURLs = eventUtils.readFileLines(seedsFile) 
#em = eventModel.EventModel(5,2)
#em.buildEventModel(20, seedURLs)

wps = eventUtils.getWebpageText(seedURLs)
#output = 'textContent.txt'

