# Filename: ext_unique_urls3.py
# Description: This file extracts shortened urls from a text file that is provided as 
#              the first argument. The extracted shortened urls are expanded. 
#              Unique urls are written to an output file, whose name is provided as the second argument.
# Usage: shell> python ext_unique_urls3.py inputfilename.txt outputfilename.txt
# Name: Seungwon Yang  <seungwon@vt.edu>
# Date: Jan. 25, 2012

import base64
import sys 
import string
import re
import urllib
import urllib2
import datetime
from operator import itemgetter # to sort dictionaries by the values in (key, value) pairs

# check start time -------------------------------------------
start_time = datetime.datetime.now()

# Open the input data file, and the output file --------------
ifd = open(sys.argv[1], "r")
ofd = open(sys.argv[2], "w+")

# data and headers are to bypass sites with web authentication
data = ''
headers = {'Authorization': 'Basic ' + base64.encodestring('admin:admin')}

line = ifd.readline() # read in the first tweet text
short_url_list = []

# extract short URLs from the tweets --------------------------
while line:
  url_li = re.findall("(?P<url>https?://[^\s]+)", line)  # find all short urls in a single tweet
  while (len(url_li) > 0): 
    short_url_list.append(url_li.pop()) # add the urls to a list for later use    
  line = ifd.readline() # read the next line of tweet
print "short Urls extracted"
expanded_url_list = []
expanded_url_dict = {}
ori_url = ""  
print len(short_url_list)
short_url_list = short_url_list[:400]
# Once we collect short urls, next step is to expand each url to its original form
# considering that two different short urls might point to the same webiste.
i = 1
for item in short_url_list:
  try:  
    #find original url of item (shortened url) ----------------
    print i
    #request = urllib2.Request(item, data, headers)
    #response = urllib2.urlopen(request)
    response = urllib2.urlopen(item)
    ori_url = response.url
    #print ori_url
    

    # add the expanded original urls to a python dictionary with their count
    if ori_url in expanded_url_dict:
      expanded_url_dict[ori_url] = expanded_url_dict[ori_url] + 1
    else:
      expanded_url_dict[ori_url] = 1
    i+=1

  except:  # ignore the exceptions/HTTP errors, and simply process the next tweet
    print "error"
  

print "urls expanded"
# sort expanded_url_dict in descending order of the url count
sorted_list = sorted(expanded_url_dict.iteritems(), key=itemgetter(1), reverse=True)
print "sorted"
# add the urls to a list, in descending order of their count
for expanded_url, count in sorted_list:
  #out_str = "%s\t%s" % (expanded_url, count)
  out_str = expanded_url
  ofd.write(out_str)
  ofd.write("\n")

# check end time ----------------------------------------------
end_time = datetime.datetime.now()
diff = end_time - start_time
print "Seconds to process tweets"
print diff.seconds
print "\nMinutes to process tweets"
print diff.seconds/60
print "\nHours to process tweets"
print diff.seconds/3600

ifd.close()
ofd.close()
  

