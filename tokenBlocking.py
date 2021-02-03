import json
import re

# Opening JSON file
file1 = open('dataset1.json')
file2 = open('dataset2.json')

# returns JSON object as a dictionary
dataset1 = json.load(file1)
dataset2 = json.load(file2)

# Tokens as block keys and the value is a list of information of entities that have the token.
# (dataset index and entity index in the dataset)
# where dataset index 0 = dataset1 ; 1 = dataset2
# where entity index is the entity profile index
blocks = dict()

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

#Create Blocks for each token in entity collection
def createTokenBlocks(dataset, dataset_index):
	index = 0
	while index < len(dataset):
		entity = dataset[index]
		for attribute in entity:
			extractTokens = []
			# A block is created for every token
			extractedTokens = extractTokensFromAttributeValue(entity[attribute])
			for token in extractedTokens:
				if token in blocks:
					blocks[token].append(dict(dataset=dataset_index, index=index))
				else:
					blocks[token] = [dict(dataset=dataset_index, index=index)]
		index += 1

#Filter Blocks that contain only 1 entity
def removeUnnecessaryBlocks():
	blocksToRemove = []
	for block in blocks:
		# If the block contains only single entity
		if len(block) == 1:
			blocksToRemove.append(block)
	for block in blocksToRemove:
		blocks.pop(block, None)

#Perfom Token Blocking
createTokenBlocks(dataset1, 0)
createTokenBlocks(dataset2, 1)
removeUnnecessaryBlocks()

# Output the blocks in to a json file
newBlocks = dict()
for block in blocks:
	blockList = []
	for entity in blocks[block]:
		blockList.append([entity['dataset'], entity['index']])
	newBlocks[block] = blockList

# Write blocks to json file
out_file = open('blocks.json', 'w')
json.dump(newBlocks, out_file)
out_file.close()



