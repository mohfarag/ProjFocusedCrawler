#import sys
#sys.path.append('/Users/mmagdy/Documents/workspace/General/src/scripts/')
import eventUtils as eu


def buildClassifier(eventName):
    classifierFileName = eventName+'_NBClassifier.p'    
    posURLsFileName = eventName+'Pos.txt'
    negURlsFileName = eventName+'Neg.txt'
    
    posURLs = eu.readFileLines(posURLsFileName)
    negURLs = eu.readFileLines(negURlsFileName)
    
    eu.train_SaveClassifier(posURLs, negURLs, classifierFileName)

if __name__ == '__main__':
	#eventName = 'bangkokBombing'
    eventName = 'charlestonShooting'
    buildClassifier(eventName)