import json
import re

# Opening JSON file
file1 = open('dataset1.json')
file2 = open('dataset2.json')

# returns JSON object as a dictionary
dataset1 = json.load(file1)
dataset2 = json.load(file2)

datasets = [dataset1,dataset2]

#prepositions to omit from token
prepositionList1=['a','an','the','aboard', 'about', 'above', 'across', 'after', 'against', 'along', 'amid', 'among', 'anti', 'around', 'as',
				 'at', 'before', 'behind', 'below', 'beneath', 'beside', 'besides', 'between', 'beyond', 'but', 'by', 'concerning',
				  'considering', 'despite', 'down','during','except','excepting','excluding','following','for','from','in','inside'
				  ,'into','like','minus','near','of','off','on','onto','opposite','outside','over','past','per','plus','regarding'
				  ,'round','save','since','than','through','to','toward','towards','under','underneath','unlike','until','up','upon'
				  ,'versus','via','with','within','without'
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
            #check if key exists in dictionary
            if (attributeName,datasetIndex) not in attributeNameDict:
                attributeNameDict[(attributeName, datasetIndex)] = list()
            # extract token from attribute name
            extractedTokens = extractTokensFromAttributeValue(entity[attributeName])
            for token in extractedTokens:
                attributeNameDict[(attributeName, datasetIndex)].append(token)
    print(attributeNameDict)
    return attributeNameDict



# extracting attribute names
attributeNames1 = extractAttributeNames(dataset1,1)
attributeNames2 = extractAttributeNames(dataset2,2)

