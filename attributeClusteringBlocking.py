import json
import tokenBlocking

# import function from tokenblocking file
extractTokensFromAttributeValue = tokenBlocking.extractTokensFromAttributeValue
cleanTokenBlocks = tokenBlocking.cleanTokenBlocks

# Opening JSON file
file1 = open('dataset1.json')
file2 = open('dataset2.json')

# returns JSON object as a dictionary
dataset1 = json.load(file1)
dataset2 = json.load(file2)

datasets = [dataset1,dataset2]
clusterLinks1 = {}
clusterLinks2 = {}
blocks = dict()

# create a list of attribute names, with the occuring values
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

#find the jaccard similarity between two set of attributes names values
#|token(attributenames1) ∩ token(attributenames2)| / |token(attributenames1) ∪ token(attributenames2)|
def jaccardSimilarity(valueList1, valueList2):
    commontokens = list(set(valueList1).intersection(set(valueList2)))
    totaltokens = list(set(valueList1).union(set(valueList2)))
    return float(len(commontokens))  / float(len(totaltokens))

#return the most similar attribute comparing the attribute value of dataset1 with all attribute values in dataset2
def extractMostSimilarAttribute(attributeName,attributeNames1, attributeNames2):
    similarAttributeName = 0
    mostSimilarity = 0
    for compareAttributeName in attributeNames2:
        similarity = jaccardSimilarity(attributeNames1[attributeName], attributeNames2[compareAttributeName])
        if similarity > mostSimilarity:
            mostSimilarity = similarity
            similarAttributeName = compareAttributeName
    return similarAttributeName

#create clusters of attribute names based on the links between the attribute names in two dataset
def createTransitiveClosure(clusterLinks1,clusterLinks2):
    clusterLists = []
    #clusterLinks1.update({('year', 1): ('knownFor', 2)})
    #clusterLinks2.update({('dataset2id', 2): ('birthYear', 1)})
    #print(clusterLinks1)
    #print(clusterLinks2)
    for source in clusterLinks1:
        target = clusterLinks1[source]
        #flag tp switch between the cluster
        switchClusterTarget = 1
        currentCluster = {source,target}
        while True:
            targetPlacedInCluster = 0
            #switch direction for searching the target
            if switchClusterTarget:
                target = clusterLinks2[target]
            else:
                target = clusterLinks1[target]
            for cluster in clusterLists:
                index = clusterLists.index(cluster)
                #if attribute name found in existing cluster add the current cluster to it
                if target in cluster:
                    clusterLists[index] = cluster.union(currentCluster)
                    targetPlacedInCluster = 1
                    break
            if targetPlacedInCluster:
                break
            # if attribute name found in current cluster then add the cluster to cluster list
            if target in currentCluster:
                clusterLists.append(currentCluster)
                break
            #if not in any cluster add to current cluster
            currentCluster.add(target)
            switchClusterTarget = not switchClusterTarget
    return clusterLists

#Filter Clusters that contain only 1 attribute name
def cleanClusterLists(clusterLists):
    for cluster in clusterLists:
        if len(cluster) == 1:
            clusterLists.remove(cluster)
    return clusterLists

#apply token blocking on each clusters
def createTokenBlocksFromCluster(clusterLists,attributeNames1,attributeNames2):
    attributeNameList = attributeNames1.copy()
    attributeNameList.update(attributeNames2)
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

# extracting attribute names for each dataset
attributeNames1 = extractAttributeNames(dataset1,1)
attributeNames2 = extractAttributeNames(dataset2,2)

#get most similar Attribute for datatset1 from dataset2 and create link
for attributeName in attributeNames1:
    mostSimilarAttributeName = extractMostSimilarAttribute(attributeName,attributeNames1,attributeNames2)
    if not mostSimilarAttributeName == 0:
        clusterLinks1[attributeName] = mostSimilarAttributeName

#get most similar Attribute for datatset2 from dataset1 and create link
for attributeName in attributeNames2:
    mostSimilarAttributeName = extractMostSimilarAttribute(attributeName,attributeNames2,attributeNames1)
    if not mostSimilarAttributeName == 0:
        clusterLinks2[attributeName] = mostSimilarAttributeName

#creating the transitive closure
clusterLists = createTransitiveClosure(clusterLinks1,clusterLinks2)

#clean clusters
cleanClusterLists = cleanClusterLists(clusterLists)

#create blocks by applying token blocking
createTokenBlocksFromCluster(cleanClusterLists,attributeNames1,attributeNames2)

#clean token blocks
cleanBlocks = cleanTokenBlocks(blocks)

# Write blocks to json file
out_file = open('attributeClusteringBlocks.json', 'w')
json.dump(cleanBlocks, out_file)
out_file.close()
