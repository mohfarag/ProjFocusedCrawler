import re

class Url:
    def __init__(self,url_address,anchor_text="",context="",parentId=-1,score=0.0):
        self.anchor = anchor_text
        self.address = url_address
        self.context = context
        self.parentId = parentId
        self.score = score

    def getAllText(self):
        parts = [s for s in re.findall(r'\w+',self.address) if s]
        parts = [s for s in parts if s not in ['https','http','www','com','htm','html','asp','jsp','aspx','php','org','net']]
        return "%s %s %s" % (self.anchor,' '.join(parts),self.context)
