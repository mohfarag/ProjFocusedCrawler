'''
Created on Sep 8, 2015

@author: mmagdy
'''
import networkx as nx
import matplotlib.pyplot as plt
import eventUtils as eu
import matplotlib.colors as colors
import matplotlib.cm as cmx
#from _collections import defaultdict
import random

def draw_graph(graph,uniqDomsColorsDic,domsDic):

    # extract nodes from graph
    #colorLegend = {}
    nodes = set([n1 for n1, n2 in graph] + [n2 for n1, n2 in graph] )
    c = [uniqDomsColorsDic[domsDic[int(n)]] for n in nodes]
    # create networkx graph
    G=nx.Graph()

    # add nodes
    for node in nodes:
        G.add_node(node)

    # add edges
    for edge in graph:
        G.add_edge(edge[0], edge[1])

    # draw graph
    #pos = nx.shell_layout(G)
    #pos = nx.circular_layout(G)
    #pos = nx.random_layout(G)
    #pos = nx.spectral_layout(G)
    
    #pos = nx.spring_layout(G)
    pos = nx.graphviz_layout(G,prog='twopi',alpha=0.5,args='')
    #plt.axis('equal')
    
    #nx.draw(G, pos,node_color=c,with_labels=True)
    
    # Color mapping
    jet = plt.get_cmap('jet')
    cNorm  = colors.Normalize(vmin=0, vmax=max(uniqDomsColorsDic.values()))
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
    
    # Using a figure to use it as a parameter when calling nx.draw_networkx
    f = plt.figure(1)
    ax = f.add_subplot(1,1,1)
    for label in uniqDomsColorsDic:
        ax.plot([0],[0],color=scalarMap.to_rgba(uniqDomsColorsDic[label]),label=label)
    
    # Just fixed the color map
    #nx.draw_networkx(G,pos, cmap = jet, vmin=0, vmax= max(values),node_color=values,with_labels=True,ax=ax)
    nx.draw(G, pos,cmap = jet, vmin=0, vmax= max(uniqDomsColorsDic.values()),node_color=c,with_labels=True,ax=ax)
    
    # Setting it to how it was looking before.                                                                                                              
    plt.axis('off')
    f.set_facecolor('w')

    
    #plt.colorbar()
    plt.legend()
    # show graph
    plt.show()

def readGraphFile(graphFile):
    with open(graphFile) as f:
        lines = f.readlines()
    lines = [l.strip() for l in lines]
    #graph = [(int(l.split(",")[0])+1,int(l.split(',')[1])+1) for l in lines ]
    graph = [(l.split(",")[0],l.split(',')[1]) for l in lines ]
    return graph

# draw example
urlsFile = 'base-Output-URLs.txt'
urls = eu.readFileLines(urlsFile)

doms = [eu.getDomain(url) for url in urls]

uniqueDomsFreqDic = eu.getFreq(doms)
uDoms = uniqueDomsFreqDic.keys()
numDoms = len(uDoms)
uc=[random.random() for i in range(numDoms)]
uniqDomsColorsDic = dict(zip(uDoms,uc))
#c = [uniqDomsColorsDic[d] for d in doms]
#c = c[5:]

domsTuples = enumerate(doms)
domsDic = dict(domsTuples)
#domsDic = defaultdict(list)
#for i,d in domsTuples:
#    domsDic[d].append(i)
#print domsDic
graphFile = 'Output-CharlestonShooting/base-webpages/base-logData.txt'
graph = readGraphFile(graphFile)
domsGraph = []
for i,j in graph:
    if j == '-1':
        domsGraph.append((domsDic[int(i)],domsDic[int(i)]))
#print domsGraph

graph =[(i,i) for i,j in graph[:5]]+ graph[5:]
#graph = [(20, 21),(21, 22),(22, 23), (23, 24),(24, 25), (25, 20)]
draw_graph(graph,uniqDomsColorsDic,domsDic)