'''
Created on Dec 25, 2014

@author: mmagdy
'''
import codecs

from eventUtils import getTokens, getFreq
from evaluate import Evaluate
def evaluateVSM(targeEvent, collFolder,k):
    return
def evaluate(collFolder,k):
    evalres = []
    for j in range(k):
        
        fn = collFolder+str(j)+'.txt'
        f = codecs.open(fn, encoding='utf-8')
        ftext = f.read()
        text =  ftext.split()#getTokens(ftext)
        text = [t.lower() for t in text]
        te = []
        for t in text:
            if t.endswith('.'):
                t = t[:-1]
            te.append(t)
        text = te
        textFreq = getFreq(text)
        '''
        if 'shoot' in text or 'shooter' in text or 'shooting' in text:
            if 'fsu' in text:
                evalres.append(1)
            elif 'florida' in text and 'state' in text :#and 'university' in text:
                evalres.append(1)
            else:
                evalres.append(0)
        else:
            evalres.append(0)
        '''
        '''
        if 'hagupit' in text or 'ruby' in text:
            if 'typhoon' in text:
                evalres.append(1)
            elif 'philippin' in text or 'philippines' in text:
                evalres.append(1)
            else:
                evalres.append(0)
            #evalres.append(1)
        else:
            evalres.append(0)
        '''
        '''
        if 'fire' in text:
            if 'la' in text:
                #if 'downtown' in text:
                evalres.append(1)
                #else:
                #    evalres.append(0)
            elif 'los' in text and 'angeles' in text:
                #if 'downtown' in text:
                evalres.append(1)
                #else:
                #    evalres.append(0)
            else:
                evalres.append(0)
        else:
            evalres.append(0)
        '''
        '''
        if 'charlie' in text and 'hebdo' in text or 'paris' in text:
            if 'shooting' in text or 'shoot' in text:
                evalres.append(1)
            elif 'attack' in text:
                evalres.append(1)
            else:
                evalres.append(0)
        else:
            evalres.append(0)
        '''
        '''
        if 'airasia' in text or 'qz8501' in text:
            if 'flight' in text and 'missing' in text:
                evalres.append(1)
            elif 'plane' in text and 'missing' in text:
                evalres.append(1)
            else:
                evalres.append(0)
            #evalres.append(1)
        else:
            evalres.append(0)
        '''
        th = 2
        if textFreq.get('qz8501',0)>th:
            evalres.append(1)
        elif textFreq.get('airasia',0)>th:
            if textFreq.get('flight',0) or textFreq.get('plane',0):
                if textFreq.get('missing',0) or textFreq.get('crash',0):
                    evalres.append(1)
                elif textFreq.get('8501',0) or textFreq.get('qz8501',0):
                    evalres.append(1)
                else:
                    evalres.append(0)
            else:
                evalres.append(0)
            #evalres.append(1)
        else:
            evalres.append(0)
        f.close()
    return evalres
class myObj(object):
    def __init__(self):
        self.text =""

def evaluateClassifier(classifierFile,cf,k):
    
    evaluator = Evaluate()
    evaluator.buildClassifier("posFile","negFolder",classifierFile)
    collFiles = []
    for j in range(k):
        
        fn = cf+str(j)+'.txt'
        f = codecs.open(fn, encoding='utf-8')
        ftext = f.read()
        o = myObj()
        o.text = ftext
        collFiles.append(o)
    res = evaluator.evaluateFC(collFiles)
    f = open(cf+'evaluationRes_Classf.txt','w')
    f.write('\n'.join([str(r) for r in res]))
    f.close()
    print sum(res)

def writeEvaluation(res,filename):
    f = open(filename,"w")
    #for p,e in zip(relevantPages,res):
    rel = 0
    tot = 0
    for r in res:
        rel = rel + r
        tot = tot + 1 
        #f.write(str(tot) + "," + str(rel) + "\n")
        f.write( str(rel) + "\n")
    f.close()
    
if __name__ == '__main__':
    ''' 
    classifierFiles = ["classifierFSU.p","classifierHagupit.p","classifierAirAsia.p"]
    #classifierFile = "classifierFSU.p"
    #classifierFile = "classifierHagupit.p"
    
    #collFiles = 'event-webpages/'
    n = ['/base-','/event-']
    for j in range(3):
        classifierFile = classifierFiles[j]
        for i in range(3):
        #i=0
            for t in n:
                collFiles = '/Users/mmagdy/fc results/'+str(j) + t +str(i)+t+'webpages/'
                print t +str(i)
                evaluateClassifier(classifierFile,collFiles,500)
    '''
    
    #j = 2
    #for i in range(3):
    #i=0
        #collFiles = '/Users/mmagdy/fc results/'+str(j)+'/event-'+str(i)+'/event-webpages/'
        #collFiles = '/Users/mmagdy/fc results/'+str(j)+'/base-'+str(i)+'/base-webpages/'
    
    collFiles = 'event-webpages/0/'
    #collFiles = 'base-webpages/'
    res = evaluate(collFiles,500)
    f = open(collFiles+'evaluationRes_Words.txt','w')
    #writeEvaluation(res, collFiles+ 'evalResults_2.txt')
    f.write('\n'.join([str(r) for r in res]))
    f.close()
    print sum(res)
        
    
    '''
    n = ['/base-','/event-']
    for j in range(1):
        for i in range(3):
        #i=0
            for t in n:
                resFile = '/Users/mmagdy/fc results/'+str(j) + t +str(i)+t+'webpages/'+'evaluationRes_Words.txt'
                res = open(resFile,'r').readlines()
                res = [int(r) for r in res]
                writeEvaluation(res, '/Users/mmagdy/fc results/'+str(j) + t +str(i)+ '/evalResults_2.txt')
                #res = evaluate(collFiles,500)
                #f = open(collFiles+'evaluationRes_Words.txt','w')
                #f.write('\n'.join([str(r) for r in res]))
                #f.close()
                #print sum(res)
    '''