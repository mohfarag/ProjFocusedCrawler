#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
'''
Created on Oct 10, 2014

@author: dlrl
'''
import nltk
import sys, os
import re
from bs4 import BeautifulSoup, Comment
import requests
from nltk.corpus import stopwords
from readability.readability import Document
from operator import itemgetter
from contextlib import closing
from hanzo.warctools import ArchiveRecord, WarcRecord
from warcunpack_ia import *
import logging
from NBClassifier import NaiveBayesClassifier
from SVMClassifier import SVMClassifier
import numpy as np
from sklearn import metrics
import ner
from gensim import corpora, models
import pickle
import random

#logging.getLogger('requests').setLevel(logging.WARNING)
#corpusTokens = []
#docsTokens = []
#allSents = []

stopwordsList = stopwords.words('english')
stopwordsList.extend(["news","people","said","comment","comments","share","email","new","would","one","world"])

'''
def train_SaveClassifier(posURLs,negURLs,classifierFileName):
    #posURLs = readFileLines(posURLsFile)
    #negURLs = readFileLines(negURLsFile)
    
    #random.shuffle(negURLs)
    
    posDocs = getWebpageText(posURLs)
    posDocs = [d['title'] + " " + d['text'] for d in posDocs if d]
    
    #negURLsList = []
    negDocsList = []
    for n in negURLs:
        negDocsList.append(getWebpageText(n))
    #negDocs = getWebpageText(negURLs)
    #negDocs = getWebpageText(negURLsList)
    
    negTraining = []
    negTesting =[]
    for nu in negDocsList:
        ns = int(len(nu)*0.7)
        negTraining.extend(nu[:ns])
        negTesting.extend(nu[ns:])
    #print len(negTraining)
    #print len(negTesting)
    negTraining = [d['title'] + " " + d['text'] for d in negTraining if d]
    negTesting = [d['title'] + " " + d['text'] for d in negTesting if d]
    
    posLen = len(posDocs)
    print posLen
    negLen = len(negTraining) + len(negTesting)
    print negLen
    posLabels = [1]* posLen
    #negLabels = [0]*negLen 
    posSep = int(posLen*0.7)
    #negSep = int(negLen*0.7)
    
    trainingDocs = posDocs[:posSep] + negTraining
    #trainingLabels = posLabels[:posSep] + negLabels[:negSep]
    trainingLabels = posLabels[:posSep] + [0]*len(negTraining)
    trainingSet = zip(trainingDocs,trainingLabels)
    random.shuffle(trainingSet)
    
    testDocs = posDocs[posSep:] + negTesting
    #test_labels=posLabels[posSep:] + negLabels[negSep:]
    test_labels=posLabels[posSep:] + [0]*len(negTesting)
    
    testSet = zip(testDocs,test_labels)
    random.shuffle(testSet)
    
    
    #trainingDocs = posDocs[:posSep] + negDocs[:negSep]
    
    #trainingLabels = posLabels[:posSep] + negLabels[:negSep]
    
    #testDocs = posDocs[posSep:] + negDocs[negSep:]
    #test_labels=posLabels[posSep:] + negLabels[negSep:]
    
    classifier = NaiveBayesClassifier()
    
    trainingLabels = [v for _,v in trainingSet]
    trainingDocs = [k for k,_ in trainingSet]
    
    trainingLabelsArr = np.array(trainingLabels)
    classifier.trainClassifier(trainingDocs,trainingLabelsArr)
    
    print classifier.score(trainingDocs, trainingLabelsArr)
    print metrics.classification_report(trainingLabelsArr, classifier.predicted)
    
    test_labels = [v for _,v in testSet]
    testDocs = [v for v,_ in testSet]
    
    test_labelsArr = np.array(test_labels)
    print classifier.score(testDocs, test_labelsArr)
    
    print metrics.classification_report(test_labelsArr, classifier.predicted)
    classifierFile = open(classifierFileName,"wb")
    pickle.dump(classifier,classifierFile)
    classifierFile.close()
    return classifier
'''

def train_SaveClassifier(posURLs,negURLs,classifierFileName):
        
    posDocs = getWebpageText(posURLs)
    posDocs = [d['title'] + " " + d['text'] for d in posDocs if d]
    
    negDocsList = []
    for n in negURLs:
        negDocsList.append(getWebpageText(n))
    
    negTraining = []
    negTesting =[]
    for nu in negDocsList:
        ns = int(len(nu)*0.7)
        negTraining.extend(nu[:ns])
        negTesting.extend(nu[ns:])
    
    negTraining = [d['title'] + " " + d['text'] for d in negTraining if d]
    negTesting = [d['title'] + " " + d['text'] for d in negTesting if d]
    
    
    posLen = len(posDocs)
    posSep = int(0.7*posLen)
    posTraining = posDocs[:posSep]
    posTest = posDocs[posSep:]
    
    trainingDocs = posTraining + negTraining
    trainingLabels = [1]* len(posTraining) + [0]*len(negTraining)
    
    testingDocs = posTest + negTesting
    testingLabels = [1]*len(posTest) + [0]*len(negTesting)
        
    classifier = NaiveBayesClassifier()
    #classifier = SVMClassifier()
    
    trainingLabelsArr = np.array(trainingLabels)
    classifier.trainClassifier(trainingDocs,trainingLabelsArr)
    
    print classifier.score(trainingDocs, trainingLabelsArr)
    print metrics.classification_report(trainingLabelsArr, classifier.predicted)
       
    test_labelsArr = np.array(testingLabels)
    print classifier.score(testingDocs, test_labelsArr)
    
    
    print metrics.classification_report(test_labelsArr, classifier.predicted)
    classifierFile = open(classifierFileName,"wb")
    pickle.dump(classifier,classifierFile)
    classifierFile.close()
    return classifier

def train_SaveClassifierRandom(posURLs,negURLs,classifierFileName):
        
    posDocs = getWebpageText(posURLs)
    posDocs = [d['title'] + " " + d['text'] for d in posDocs if d]
    
    negDocs = getWebpageText(negURLs)
    negDocs = [d['title'] + " " + d['text'] for d in negDocs if d]
    
    posLen = len(posDocs)
    print posLen
    negLen = len(negDocs)
    print negLen
    posLabels = [1]* posLen
    negLabels = [0]*negLen 
    
    
    
    dataSetDocs = posDocs + negDocs
    dataSetLabels = posLabels + negLabels
    
    dataDocLabels = zip(dataSetDocs,dataSetLabels)
    random.shuffle(dataDocLabels)
    
    sep = int(0.7*len(dataDocLabels))
    trainingDocLabels = dataDocLabels[:sep]
    testDocLabels = dataDocLabels[sep:]
    
    trainingLabels = [v for _,v in trainingDocLabels]
    trainingDocs = [k for k,_ in trainingDocLabels]
    
    testDocs = [d for d,_ in testDocLabels]
    test_labels=[l for _,l in testDocLabels]
    
    classifier = NaiveBayesClassifier()
    
    trainingLabelsArr = np.array(trainingLabels)
    classifier.trainClassifier(trainingDocs,trainingLabelsArr)
    
    print classifier.score(trainingDocs, trainingLabelsArr)
    print metrics.classification_report(trainingLabelsArr, classifier.predicted)
       
    test_labelsArr = np.array(test_labels)
    print classifier.score(testDocs, test_labelsArr)
    
    
    print metrics.classification_report(test_labelsArr, classifier.predicted)
    classifierFile = open(classifierFileName,"wb")
    pickle.dump(classifier,classifierFile)
    classifierFile.close()
    return classifier

def getEntities(texts):
        
        if type(texts) != type([]):
            texts = [texts]   
        """
        Run the Stanford NER in server mode using the following command:
        java -mx1000m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer -loadClassifier classifiers/english.muc.7class.distsim.crf.ser.gz -port 8000 -outputFormat inlineXML
        """
        
        tagger = ner.SocketNER(host='localhost',port=8000)
        entities = []
        for t in texts:
            sentence_entities = tagger.get_entities(t)
            entities.append(sentence_entities)
        return entities

def isListsDisjoint(l1,l2):
    s1 = set(l1)
    s2 = set(l2)
    return s1.isdisjoint(s2)

def getIntersection(l1,l2):
    s1 = set(l1)
    s2 = set(l2)
    return s1.intersection(s2)

def readFileLines(filename):
    f = open(filename,"r")
    lines = f.readlines()
    return lines

def getSorted(tupleList,fieldIndex):
    sorted_list = sorted(tupleList, key=itemgetter(fieldIndex), reverse=True)
    return sorted_list

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head']:
        return False
    return True

def getTokens(texts):
    #global corpusTokens
    #global docsTokens
    allTokens=[]
    #tokens=[]
    if type(texts) != type([]):
        texts = [texts]
    for s in texts:
        toks = nltk.word_tokenize(s.lower())
        allTokens.extend(toks)
        #corpusTokens.extend(toks)
        #docsTokens.append(toks)
    allTokens = [t.lower() for t in allTokens if len(t)>2]
    allTokens = [t for t in allTokens if t not in stopwordsList]
    return allTokens

def getFreq(tokens):
    return nltk.FreqDist(tokens)

def getSentences(textList =[]):
    #stopwordsList = stopwords.words('english')
    #stopwordsList.extend(["news","people","said"])
    if type(textList) != type([]):
        textList = [textList]
    sents = []
    for text in textList:
        sentences = nltk.sent_tokenize(text)
        newSents = []
        for s in sentences:
			if len(re.findall(r'.\..',s))>0:
				ns = re.sub(r'(.)\.(.)',r'\1. \2',s)
				newSents.extend(nltk.sent_tokenize(ns))
			else:
				newSents.append(s)

        
        newSents = [s for sent in newSents for s in sent.split("\n") if len(s) > 3]
        cleanSents = [sent.strip() for sent in newSents if len(sent.split()) > 3]
        sents.extend(cleanSents)
    return sents

def _cleanSentences(sents):
    sentences = [s for sent in sents for s in sent.split("\n") if len(s) > 3]
    cleanSents = [sent.strip() for sent in sentences if len(sent.split()) > 3]
    return cleanSents

def getUniqueEntities(sents):
    uniqueEntities = {}
    allEnts = getEntities(sents)
    for ent in allEnts:
        for k in ent:
            if k in uniqueEntities:
                uniqueEntities[k].extend(ent[k])
            else:
                uniqueEntities[k] = []
                uniqueEntities[k].extend(ent[k])
    #now you have a huge one dic with different entities as keys and list of values for each key
    # we need to get the unique values in each list
    entitiesCount= {}
    
    locDateEntities = {}
    for k in uniqueEntities:
        if k in ["LOCATION","DATE"]:
            #l = uniqueEntities[k]
            #s = set(l)
            #locDateEntities[k] = list(s)
            locDateEntities[k] = [].extend(uniqueEntities[k])
    for k in locDateEntities:
    	for ent in locDateEntities[k]:
    		if ent in entitiesCount:
    			entitiesCount[ent]+=1
    		else:
    			entitiesCount[ent]=1
    
    return locDateEntities

def getUniqueEntitiesWords(entities):
    words = []
    for k in entities:
        words.extend(entities[k])
    entitiesWords = []
    for w in words:
        p = w.split()
        if len(p)>1:
            entitiesWords.extend(p)
        else:
            entitiesWords.append(w)
    entitiesWords = [ew.lower() for ew in entitiesWords]
    return entitiesWords

def getPOS(words):
    tags = nltk.pos_tag(words)
    return tags

def getFilteredImptWords(texts,freqWords):
	#nltk.pos_tag(text)
    impWordsTuples = getIndicativeWords(texts,freqWords)
    impWordsList = [w[0] for w in impWordsTuples]
    
    wordsTags = nltk.pos_tag(impWordsList)
    nvWords = [w[0] for w in wordsTags if w[1].startswith('N') or w[1].startswith('V')]
    wordsDic = dict(impWordsTuples)
    nvWordsTuple = [(w,wordsDic[w]) for w in nvWords]
    return nvWordsTuple
    

def getLDATopics(documents):
	texts = []
	for doc in documents:
		docToks = getTokens(doc)
		texts.append(docToks)
		
		
	dictionary = corpora.Dictionary(texts)
	corpus = [dictionary.doc2bow(text) for text in texts]

	notopics = 3
	lda = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=notopics)


	outputTopics = []
	for i in range(0, lda.num_topics):
		
		#outputTopics.append( "Topic"+ str(i+1) + ":"+ lda.print_topic(i))
		t = lda.show_topic(i)
		#print type(t)
		t = [w for _,w in t]
		#for tu in t:
		#	print tu[1]
		outputTopics.append( "Topic"+ str(i+1) + ":"+ ", ".join(t))
	return "<br>".join(outputTopics)

def extractMainArticle(html):
    p = Document(html)
    readable_article = p.summary()
    readable_title = p.short_title()
    
    soup = BeautifulSoup(readable_article)
    text_nodes = soup.findAll(text=True)
    text = ''.join(text_nodes)
    
    #text = readable_title + " " + text
    #return text
    
    wtext = {"title":readable_title, "text": text}
    return wtext

def extractTextFromHTML(page):
    try:
        soup = BeautifulSoup(page)
        title = ""
        text = ""
        if soup.title:
            if soup.title.string:
                title = soup.title.string
        
        comments = soup.findAll(text=lambda text:isinstance(text,Comment))
        [comment.extract() for comment in comments]
        text_nodes = soup.findAll(text=True)
        
        visible_text = filter(visible, text_nodes)
        text = ''.join(visible_text)
        
        #text = title + text
        wtext = {"text":text,"title":title}
    except:
        print sys.exc_info()
        #text = ""
        wtext = {}
    #return text
    return wtext

def getWebpageText(URLs = []):
    webpagesText = []
    if type(URLs) != type([]):
        URLs = [URLs]
    for url in URLs:
        try:
            page = requests.get(url.strip()).content
            #text = extractMainArticle(page)
            text = extractTextFromHTML(page)
        except:
            print sys.exc_info()
            #text = ""
            text = {}
        webpagesText.append(text)
    return webpagesText



#Get Frequent Tokens
#moved
def getFreqTokens(texts):
	tokens = getTokens(texts)
	f = getFreq(tokens)
	tokensFreqs = f.items()
	sortedTokensFreqs = getSorted(tokensFreqs,1)
	return sortedTokensFreqs

def getIndicativeWords(texts,tokensFreqs):
	#global allSents
	#Get Indicative tokens
	toksTFDF = getTokensTFDF(texts,tokensFreqs)
	
	#sortedToksTFDF = sorted(filteredToksTFDF, key=lambda x: x[1][0]*x[1][1], reverse=True)
	sortedToksTFDF = sorted(toksTFDF.items(), key=lambda x: x[1][0]*x[1][1], reverse=True)
	return sortedToksTFDF
	
def getIndicativeSents(texts,sortedToksTFDF,topK,intersectionTh):
	# Get Indicative Sentences
	topToksTuples = sortedToksTFDF[:topK]
	topToks = [k for k,_ in topToksTuples]
	#allImptSents = []
	allSents = getSentences(texts)
	
	#impSentsF = {}
	impSents ={}
	for sent in allSents:
		if sent not in impSents:
			sentToks = getTokens(sent)
			if len(sentToks) > 100:
				continue
			intersect = getIntersection(topToks, sentToks)
			if len(intersect) > intersectionTh:
				impSents[sent] = len(intersect)
				#if sent not in impSentsF:
				#	impSentsF[sent] = len(intersect)
			#allImptSents.append(impSents)
	
	sortedImptSents = getSorted(impSents.items(),1)
	return sortedImptSents

def getEventModelInsts(sortedImptSents):
    '''    
    eventModelInstances = []
    for sent in sortedImptSents:
        sentEnts = getEntities(sent[0])[0]
        eventModelInstances.append(sentEnts)
    '''
    imptSents = [s[0] for s in sortedImptSents]
    eventModelInstances = getEntities(imptSents)
    return eventModelInstances

'''
def getTokensTFDF(texts):
	tokensTF = []
	#allTokensList=[]
	allTokens = []
	allSents = []
	for t in texts:
		sents = getSentences(t)
		toks = getTokens(sents)
		toksFreqs = getFreq(toks)
		allTokens.extend(toksFreqs.keys())
		#allTokensList.append(toks)
		allSents.append(sents)
		sortedToksFreqs = getSorted(toksFreqs.items(), 1)
		tokensTF.append(sortedToksFreqs)
	tokensDF = getFreq(allTokens).items()
	tokensTFDF = {}
	for t in tokensTF:
		for tok in t:
			if tok[0] in tokensTFDF:
				tokensTFDF[tok[0]] += tok[1]
			else:
				tokensTFDF[tok[0]] = tok[1]
	for t in tokensDF:
		tokensTFDF[t[0]] = (tokensTFDF[t[0]],t[1])
	
	return tokensTFDF,allSents
'''	

def getTokensTFDF(texts,termFreq):
    docsTokens=[]
    for t in texts:
        toks = getTokens(t)
        docsTokens.append(toks)
    #tokensTF = dict(getFreqTokens(texts))
    tokensTF = dict(termFreq)
    tokensDF = {}
    for te in tokensTF:
        
        df = sum([1 for t in docsTokens if te in t])
        tokensDF[te] = df
    
    tokensTFDF = {}
    for t in tokensDF:
        tokensTFDF[t] = (tokensTF[t],tokensDF[t])
    
    return tokensTFDF

def parseLogFileForHtml(log_file):
    htmlList = []
    
    with open(log_file, 'r+b') as f:
        for line in f:
            splitext = line.split('\t')
            if len(splitext) >= 9:
                content_type = splitext[6]
                if content_type.find("text/html") == 0:
                    htmlList.append({"file":splitext[7], "wayback_url":splitext[8], "url":splitext[5]})
                
    return htmlList

# Extracts text from a given HTML file and indexes it into the Solr Instance
def extractText(html_files):
    textFiles = []
    docsURLs = []
    titles = {}
    for f in html_files:
        html_file = f["file"].strip()
        file_url = f["url"].strip()
        wayback_url = f["wayback_url"].strip()

        try:   
        	html_fileh = open(html_file, "r")
        	html_string = html_fileh.read()

        except:
        	print "Error reading"
        	#logging.exception('')
        
        if len(html_string) < 1:
            print "error parsing html file " + str(html_file)
            continue
        try:   
            d = extractTextFromHTML(html_string)

        except:
            print "Error: Cannot parse HTML from file: " + html_file
            print sys.exc_info()
            #logging.exception('')
            continue    
        
        
        
        title = d['title']
        if title and title in titles:
            #print "Title already exists"
            continue
        else:
            titles[title]=1
        html_body = d['text']
        textFiles.append(html_body)
        docsURLs.append(file_url)
    return textFiles,docsURLs

#def main(argv):
def expandWarcFile(warcFile):
#     if (len(argv) < 1):
#         print >> sys.stderr, "usage: processWarcDir.py -d <directory> -i <collection_id> -e <event> -t <event_type>"
#         sys.exit()
#         
#     if (argv[0] == "-h" or  len(argv) < 4):
#         print >> sys.stderr, "usage: processWarcDir.py -d <directory> -i <collection_id> -e <event> -t <event_type>"
#         sys.exit()
    
    
    rootdir = os.path.dirname(warcFile)
    filename = os.path.basename(warcFile)
    filePath =warcFile
    if filename.endswith(".warc") or filename.endswith(".warc.gz"):# or filename.endswith(".arc.gz"):
		# processWarcFile(filePath, collection_id, event, event_type)
		splitext = filePath.split('.')
		output_dir = splitext[0] + "/"
		
		log_file = os.path.join(output_dir, filePath[filePath.rfind("/")+1:] + '.index.txt')
		
		# output_file = output_dir + filePath.split("/")[1] + ".index.txt"
		if os.path.exists(output_dir) == False:                    
		
			os.makedirs(output_dir)

			# unpackWarcAndRetrieveHtml(filePath, collection_id, event, event_type)
			# output_dir = filePath.split(".")[0] + "/"
			default_name = 'crawlerdefault'
			wayback = "http://wayback.archive-it.org/"
			collisions = 0
				
			#log_file = os.path.join(output_dir, filePath[filePath.rfind("/")+1:] + '.index.txt')
			
			log_fileh = open(log_file, 'w+b')
			warcunpack_ia.log_headers(log_fileh)
		
			try:
				with closing(ArchiveRecord.open_archive(filename=filePath, gzip="auto")) as fh:
					collisions += warcunpack_ia.unpack_records(filePath, fh, output_dir, default_name, log_fileh, wayback)
		
			except StandardError, e:
				print "exception in handling", filePath, e
				return
		else:
			print "Directory Already Exists"
		
			#print "Warc unpack finished"
		
		html_files = parseLogFileForHtml(log_file)
		#print "Log file parsed for html files pathes"
		#print len(html_files)
		
		# for i in html_files:
			# extractTextAndIndexToSolr(i["file"], i["url"], i["wayback_url"], collection_id, event, event_type)
		tf,urls = extractText(html_files)
		#print "extracting Text finished"
		return tf,urls