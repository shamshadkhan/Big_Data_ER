import json
import re

# Opening JSON file
file1 = open('dataset1.json')
file2 = open('dataset2.json')

# returns JSON object as a dictionary
dataset1 = json.load(file1)
dataset2 = json.load(file2)

datasets = [dataset1,dataset2]
clusterLinks1 = {}
clusterLinks2 = {}

#prepositions to omit from token
prepositionList1=['a','an','the','aboard', 'about', 'above', 'across', 'after', 'against', 'along', 'amid', 'among', 'anti', 'around', 'as',
				 'at', 'before', 'behind', 'below', 'beneath', 'beside', 'besides', 'between', 'beyond', 'but', 'by', 'concerning',
				  'considering', 'despite', 'down','during','except','excepting','excluding','following','for','from','in','inside'
				  ,'into','like','minus','near','of','off','on','onto','opposite','outside','over','past','per','plus','regarding'
				  ,'round','save','since','than','through','to','toward','towards','under','underneath','unlike','until','up','upon'
				  ,'versus','via','with','within','without','and','or'
]

#extract token from entity attribute values
def extractTokensFromAttributeValue(value):
	tokensFromAttributeValue = []
	extractTokens = re.split(':|;|,|#|%|-| ', value)
	for token in extractTokens:
		if token.lower() not in prepositionList1:
			tokensFromAttributeValue.append(token)
	return tokensFromAttributeValue

# create a list of attribute names, annotated with the occuring values
def extractAttributeNames(entitiesList, datasetIndex):
    # unique set of attribute Names
    attributeNames = set()
    # attributeDict are dictionaries with the attribute names, dataset index as keys (in a tuple) and
    # as value a list with the values that occur in this attribute
    attributeNameDict = dict()
    for entity in entitiesList:
        for attributeName in entity:
            attributeNames.add((attributeName,datasetIndex))
            #check if attribute name exists in dictionary
            if (attributeName,datasetIndex) not in attributeNameDict:
                attributeNameDict[(attributeName, datasetIndex)] = list()
            # extract token from attribute name
            extractedTokens = extractTokensFromAttributeValue(entity[attributeName])
            for token in extractedTokens:
                attributeNameDict[(attributeName, datasetIndex)].append(token)
    return attributeNameDict

def jaccardSimilarity(valueList1, valueList2):
    commontokens = list(set(valueList1).intersection(set(valueList2)))
    totaltokens = list(set(valueList1).union(set(valueList2)))
    return float(len(commontokens))  / float(len(totaltokens))

def extractMostSimilarAttribute(attributeName,attributeNames1, attributeNames2):
    similarAttributeName = 0
    mostSimilarity = 0
    for compareAttributeName in attributeNames2:
        similarity = jaccardSimilarity(attributeNames1[attributeName], attributeNames2[compareAttributeName])
        if similarity > mostSimilarity:
            mostSimilarity = similarity
            similarAttributeName = compareAttributeName
    return similarAttributeName

def createTransitiveClosure(clusterLinks1,clusterLinks2):
    clusterLists = []
    #clusterLinks1.update({('year', 1): ('knownFor', 2)})
    #clusterLinks2.update({('dataset2id', 2): ('birthYear', 1)})
    #print(clusterLinks1)
    #print(clusterLinks2)
    for source in clusterLinks1:
        target = clusterLinks1[source]
        switchClusterTarget = 1
        currentCluster = {source,target}
        while True:
            targetPlacedInCluster = 0
            if switchClusterTarget:
                target = clusterLinks2[target]
            else:
                target = clusterLinks1[target]
            for cluster in clusterLists:
                index = clusterLists.index(cluster)
                if target in cluster:
                    clusterLists[index] = cluster.union(currentCluster)
                    targetPlacedInCluster = 1
                    break
            if targetPlacedInCluster:
                break
            if target in currentCluster:
                clusterLists.append(currentCluster)
                break
            currentCluster.add(target)
            switchClusterTarget = not switchClusterTarget
    return clusterLists

def cleanClusterLists(clusterLists):
    for cluster in clusterLists:
        if len(cluster) == 1:
            clusterLists.remove(cluster)
    return clusterLists

def createTokenBlocksFromCluster(clusterLists,attributeNames1,attributeNames2):
    attributeNameList = attributeNames1.copy()
    attributeNameList.update(attributeNames2)
    blocks = dict()
    for cluster in clusterLists:
        for attributeName in cluster:
            for value in attributeNameList[attributeName]:
                for dataset in datasets:
                    for entity in dataset:
                        if attributeName[0] in entity:
                            currentExtractedToken = extractTokensFromAttributeValue(entity[attributeName[0]])
                            if value in currentExtractedToken:
                                key = 'C' + str(clusterLists.index(cluster) + 1) + '.' + value
                                value = (datasets.index(dataset) + 1, dataset.index(entity))
                                if key in blocks:
                                    if not value in blocks[key]:
                                        blocks[key].append(value)
                                # or create a new block
                                else:
                                    blocks[key]= [value]
    return blocks

def cleanTokenBlocks(blocks):
    blocksToRemove = []
    for block in blocks:
        # If the block contains only single entity
        if len(blocks[block]) == 1:
            blocksToRemove.append(block)
    for block in blocksToRemove:
        blocks.pop(block)
    return blocks

# extracting attribute names for each dataset
attributeNames1 = extractAttributeNames(dataset1,1)
attributeNames2 = extractAttributeNames(dataset2,2)

#get most similar Attribute for datatset1 from dataset2
for attributeName in attributeNames1:
    mostSimilarAttributeName = extractMostSimilarAttribute(attributeName,attributeNames1,attributeNames2)
    if not mostSimilarAttributeName == 0:
        clusterLinks1[attributeName] = mostSimilarAttributeName

#get most similar Attribute for datatset2 from dataset1
for attributeName in attributeNames2:
    mostSimilarAttributeName = extractMostSimilarAttribute(attributeName,attributeNames2,attributeNames1)
    if not mostSimilarAttributeName == 0:
        clusterLinks2[attributeName] = mostSimilarAttributeName

#creating the transitive closure
clusterLists = createTransitiveClosure(clusterLinks1,clusterLinks2)

#clean clusters
cleanClusterLists = cleanClusterLists(clusterLists)

#create blocks by applying token blocking
blocks = createTokenBlocksFromCluster(cleanClusterLists,attributeNames1,attributeNames2)

#clean token blocks
cleanBlocks = cleanTokenBlocks(blocks)

# Write blocks to json file
out_file = open('attributeClusteringBlocks.json', 'w')
json.dump(cleanBlocks, out_file)
out_file.close()
