import re

class Url:
    def __init__(self,anchor_text,url_address,context=""):
        self.anchor = anchor_text
        self.address = url_address
        self.context = context

    def getAllText(self):
        parts = [s for s in re.findall(r'\w+',self.address) if s]
        parts = [s for s in parts if s not in ['https','http','www','com','htm','html','asp','jsp','aspx','php','org','net','pl','cgi']]
        return "%s %s %s" % (self.anchor,' '.join(parts),self.context)
