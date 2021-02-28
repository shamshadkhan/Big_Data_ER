import json
import re
from itertools import product as cartesian_product

# Opening JSON file
file1 = open('dataset1.json')
file2 = open('dataset2.json')
file3 = open('ground_truth.json')

# returns JSON object as a dictionary
dataset1 = json.load(file1)
dataset2 = json.load(file2)
ground_truth = json.load(file3)

# Tokens as block keys and the value is a list of information of entities that have the token.
# (dataset index and entity index in the dataset)
# where dataset index 1 = dataset1 ; 2 = dataset2
# where entity index is the entity profile index
blocks = dict()

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
		if token and token.lower() not in prepositionList1:
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
					blocks[token].append([dataset_index, index])
				else:
					blocks[token] = [[dataset_index, index]]
		index += 1

#Filter Blocks that contain only single dataset entity
def cleanTokenBlocks(blockList):
	blocksToRemove = []
	for block in blockList:
		datasetsInBlock = []
		for entity in blockList[block]:
			if entity[0] not in datasetsInBlock:
				datasetsInBlock.append(entity[0])
		# If the block contains only single dataset entity
		if len(datasetsInBlock) == 1:
			blocksToRemove.append(block)
	for block in blocksToRemove:
		blockList.pop(block)
	return blockList

#measure RR, PC, PQ
def measure_performance(block_collection, ground_truth):
	print(f"Dataset 1 has {len(dataset1)} entities.")
	print(f"Dataset 2 has {len(dataset2)} entities.")
	comparisons = []
	for block in block_collection:
		inner_block_1 = []
		inner_block_2 = []
		for entity in block_collection[block]:
			if entity[0] == 1:
				inner_block_1.append(entity)
			else:
				inner_block_2.append(entity)
		comparisons.append(cartesian_product(inner_block_1, inner_block_2))

	print("Ground truth (duplicates):", len(ground_truth))

	allcomps = [comp for comparison in comparisons for comp in comparison]
	print("Suggested comparisons:", len(allcomps))
	print("Reduction Ratio: 1 - (", len(allcomps), "/", len(dataset1)*len(dataset2), ") =", (1 - (len(allcomps)/(len(dataset1)*len(dataset2))))*100, "%")

	correct = 0
	for duplicate in ground_truth:
		if tuple(duplicate) in allcomps:
			correct += 1
	print("Duplicates found (PC):", correct, "/", len(ground_truth), "=", (correct/len(ground_truth)) * 100, "%")
	print("Precision (PQ):", correct, "/", len(allcomps), "=", (correct/len(allcomps)) * 100, "%")

def main():
	#Perfom Token Blocking
	createTokenBlocks(dataset1, 1)
	createTokenBlocks(dataset2, 2)
	cleanBlocks = cleanTokenBlocks(blocks)

	# Output the blocks in to a json file
	# Write blocks to json file
	print("Writing token block collection to 'tokenBlocks.json'")
	out_file = open('tokenBlocks.json', 'w')
	json.dump(cleanBlocks, out_file)
	out_file.close()
	print("Done.\n")

	#running performance
	print("Running performance measurements for the token block collection...")
	measure_performance(cleanBlocks, ground_truth)

if __name__ == "__main__":
    main()

