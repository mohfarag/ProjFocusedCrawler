sourcesFile = 'seedURLs.txt'
seedURLs = []
with open(sourcesFile,'r') as f:
	for l in f:
		seedURLs.append(l.strip())

targetEventKeywords = ['charleston','church','shooting']

