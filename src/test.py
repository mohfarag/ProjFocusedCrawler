'''
Created on Mar 6, 2014

@author: mohamed
'''
f = open("results-cleaned.txt","r")
fw = open("results-output.txt","w")
for line in f:
    line = line[:-1]
    parts = line.split(",")
    if parts[1].strip() == "OTHER":
        fw.write(parts[0]+ "\n") 
    else:
        fw.write(parts[0] + " " + parts[1]+"\n")
f.close()
fw.close()
