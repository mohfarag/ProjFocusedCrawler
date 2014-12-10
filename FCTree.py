#!/usr/local/bin/python
import sys  
    
def getDomain(url):
    domain = ""
    ind = url.find("//")
    if ind != -1 :
        domain = url[ind+2:]
        ind = domain.find("/")
        domain = domain[:ind]
    return domain  

if __name__ == "__main__":
    
    inputFile = "event-logData.txt" 
    #inputFile = sys.argv[1]
    inf = inputFile.split("-")
    urlFile = inf[0] + "-Output-URLs.txt"
    outf = inf[0] + "-FCTree.txt"
    
    domains = []
    furls = open(urlFile,"r")
    for line in furls:
        line = line.strip()
        domains.append(getDomain(line))
    furls.close()
    
    f = open(inputFile,"r")
    nodes = []
    roots = {}
    for line in f:
        line = line.strip()
        p = line.split(",")
        node = p[0]
        nodes.append(node)
        parent = p[1]
        if parent ==-1:
            roots[node] = []
        else:
            if parent in roots:
                roots[parent].append(node)
            else:
                roots[parent] = [node]

    f.close()
    sortedList = sorted(roots.items(), key=lambda x: int(x[0]))
    fw = open(outf,"w")
    for n,childs in sortedList:
        fw.write("Node "+str(n)+": "+",".join(childs)+"\n")
    fw.close()
    nodes_domains = dict(zip(nodes,domains))
    domainsTree = {}
    
    for root,chs in sortedList:
        if root != "-1":
            domain = nodes_domains[root]
            doms = []
            for node in chs:
                dom = nodes_domains[node]
                doms.append(dom)
            
            domainsTree[root] = (domain,doms) 
    
    sortedTree = sorted(domainsTree.items(), key=lambda x: int(x[0]))
    fw = open("domainsTree.txt","w")
    for n,childs in sortedTree:
        fw.write("Node "+ str(n) + "--" + childs[0]+": "+",".join(childs[1])+"\n")
    fw.close()
    
    
    
    
    #connCompts = roots.keys()
    #sortedKeys = sorted(roots, key=lambda x: int(x[0]))
    sortedKeys = [x[0] for x in sortedList]
    connCompts ={}
    for root in sortedKeys:
        l = roots[root]
        connCompts[root] = [root,l]


    for root in sortedKeys:
        if root != "-1":
            root = connCompts[root]
            p = root[0]
            for l in root[1]:
                if l in connCompts:
                    connCompts[l][0] = p
        
   
    
    
    
    domainsRoots = {}
    
    connComptsList = {}
    for root in connCompts:
        p = connCompts[root][0]
        if p in connComptsList:
            connComptsList[p].extend(connCompts[root][1])
        else:
            connComptsList[p] = connCompts[root][1]
    
    fw = open("nodesConnCompts.txt","w")
    for n in connComptsList:
        fw.write("Node "+str(n)+": "+",".join(connComptsList[n])+"\n")
    fw.close()
    
    for root in connComptsList:
        if root != "-1":
            domain = nodes_domains[root]
            domainsRoots[domain] = []
            for node in connComptsList[root]:
                dom = nodes_domains[node]
                domainsRoots[domain].append(dom)

    fw = open("domainsConnCompts.txt","w")
    for n in domainsRoots:
        fw.write("Node "+str(n)+": "+",".join(set(domainsRoots[n]))+"\n")
    fw.close()
    '''
    fd = open("domainsTree.txt","w")
    for d in domainsRoots:
        fd.write(d + ":-- \n" + ",".join(domainsRoots[d])+"\n")
    fd.close()
    '''
    #for n in roots:
    #	fw.write("Node "+str(n)+": "+",".join(roots[n])+"\n")
    
    
