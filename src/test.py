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
seedsFile = 'Output-nepalEarthquake-long.txt'
seedURLs = eventUtils.readFileLines(seedsFile) 
em = eventModel.EventModel(5,2)

em.buildEventModel(20, seedURLs)