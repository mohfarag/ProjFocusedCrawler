import eventUtils as utils
class Document:
    ''' class for representing corpus document'''
    def __init__(self,url='',text=''):
        
        if url != '':
            self.URL = url.strip()
            if text == '':
                self.getText()
            else:
                self.text = text.strip()
        self.words = []
        self.sentences = []
    '''
    def __init__(self):
        self.URL = ''
        self.text = ''
        self.title = ''
        self.words = []
        self.sentences = []
    
    def __init__(self,url,text):
        self.URL = url.strip()
        self.text = text
        self.words = []
        self.sentences = []
        
    def __init__(self,url):
        self.URL = url.strip()
        self.text = ''
        self.getText()
        #self.text = ''
        self.words = []
        self.sentences = []
     '''   
    def getWords(self):
        if self.words:
            return self.words
        else:
            r = utils.getTokens(self.text)
            if r:
                self.words = r
                return self.words
    
    def getText(self):
        if self.text != '':
            return self.text
        else:
            r = utils.getWebpageText(self.URL)[0]
            if r:
                self.text = r['text']
                self.title = r['title']
            return self.text
    
    def getSentences(self):
        if self.sentences:
            return self.sentences
        else:
            r = utils.getSentences(self.text)
            if r:
                self.sentences = r
                return self.sentences