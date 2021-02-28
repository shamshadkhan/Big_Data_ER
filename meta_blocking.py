from math import ceil
import json
from itertools import permutations
from itertools import product as cartesian_product


def block_collection_to_graph(block_collection):
    """
    Transforms a block collection to a block graph.

    Input: Block collection created from two clean datasets.
    Expected format is a three dimensional sequence:
    E.g. [[[d, pa], ..., [d, pz]]] where d refers to the originating
    dataset of the entites (p). Thus d can have two values (e.g. 1, 2)
    and it denotes an inner block.
    Entities pa, ..., pz refer to an index in the origin datasets.

    Output: nodes and edges
    nodes: [[d, pa], ..., [d, pz]]
    edges: [[[d, pa], [d, pb]], ..., [d, py], [d, pz]]]
    """
    nodes = []
    edges = []
    for entities in block_collection.values():
        inner_block_1 = []
        inner_block_2 = []
        for entity in entities:
            if entity not in nodes:
                nodes.append(entity)
            if entity[0] == 1:
                inner_block_1.append(entity)
            else:
                inner_block_2.append(entity)
        inner_block_edges = cartesian_product(inner_block_1, inner_block_2)
        for edge in inner_block_edges:
            if edge not in edges:
                edges.append(edge)
    return nodes, edges

def graph_to_block_collection(edges):
    return [edge for edge in edges if edge != "N/A"]

def directed_graph_to_block_collection(directed_edges):
    block_collection = dict()
    for edge in directed_edges:
        # The source node may point to more than one node,
        # i.e. the source node already has a block
        if tuple(edge[0]) in block_collection:
            block_collection[tuple(edge[0])].append(tuple(edge[1]))
        # Otherwise create a new block
        else:
            block_collection[tuple(edge[0])] = [tuple(edge[1])]
    return block_collection

def count_block_occurrence(entity, block_collection):
    return sum(1 for block in block_collection.values() if entity in block)

def count_common_blocks(entity_pair, block_collection):
    c = 0
    for block in block_collection.values():
        if entity_pair[0] in block and entity_pair[1] in block:
            c += 1
    return c

def common_blocks_weighting(edges, block_collection):
    weights = []
    for edge in edges:
        weights.append(count_common_blocks(edge, block_collection))
    return weights

def jaccard_weighting(edges, block_collection):
    weights = []
    for edge in edges:
        b_ij = count_common_blocks(edge, block_collection)
        b_i = count_block_occurrence(edge[0], block_collection)
        b_j = count_block_occurrence(edge[1], block_collection)
        jaccard_similarity = b_ij / (b_i + b_j - b_ij)
        weights.append(jaccard_similarity)
    return weights

def weight_edge_pruning(edges, weights):
    average_edge_weight = sum(weights)/len(weights)
    treshold = average_edge_weight
    return [edges[i] if w > treshold else "N/A" for i, w in enumerate(weights)]

def get_neighborhood(node, edges, weights):
    neighboring_nodes = []
    neighboring_edges = []
    neighboring_weights = []

    # Find out the neighboring nodes by scanning the endpoints of each edge
    for i, edge in enumerate(edges):
        if edge[0] == node:
            if edge[1] not in neighboring_nodes:
                neighboring_nodes.append(edge[1])
            if edge not in neighboring_edges:
                neighboring_edges.append(edge)
                neighboring_weights.append(weights[i])
        elif edge[1] == node:
            if edge[0] not in neighboring_nodes:
                neighboring_nodes.append(edge[0])
            if edge not in neighboring_edges:
                neighboring_edges.append(edge)
                neighboring_weights.append(weights[i])

    # Check if the neighboring nodes have edges between each other
    possible_edges = permutations(neighboring_nodes)
    for i, edge in enumerate(edges):
        if edge in possible_edges and edge not in neighboring_edges:
            neighboring_edges.append(edge)
            neighboring_weights.append(weights[i])

    # The central node is also part of the neighborhood
    neighboring_nodes.append(node)

    return neighboring_nodes, neighboring_edges, neighboring_weights

def cardinality_node_pruning(nodes, edges, weights):
    pruned_weights = []
    pruned_directed_edges = []
    for node in nodes:
        # This stack keeps the k-nearest entities of each node
        sorted_stack = []
        (neighboring_nodes,
        neighboring_edges,
        neighboring_weights) = get_neighborhood(node, edges, weights)
        # This treshold (k) is given in the paper[2]
        local_cardinality_treshold = ceil(0.1 * len(neighboring_edges))

        # Go through the neighboring edges and keep the k-nearest in the stack
        for nedges_nweights in zip(neighboring_edges, neighboring_weights):
            sorted_stack.append(nedges_nweights)
            if local_cardinality_treshold < len(sorted_stack):
                sorted_stack.sort(key=lambda item: item[1], reverse=True)
                sorted_stack.pop()

        # Generate directed edges based on the sorted stack
        for nedge in neighboring_edges:
            for stack_item in sorted_stack:
                if nedge == stack_item[0]:
                    if node == nedge[1]:
                        outgoing_edge = nedge[::-1]
                    else:
                        outgoing_edge = nedge
                    if outgoing_edge not in pruned_directed_edges:
                        pruned_directed_edges.append(outgoing_edge)
                        pruned_weights.append(stack_item[1])

    return nodes, pruned_directed_edges, pruned_weights

def measure_performance(block_collection, ground_truth):
    with open('dataset1.json') as f:
        d1 = json.load(f)
    with open('dataset2.json') as f:
        d2 = json.load(f)

    print(f"Dataset 1 has {len(d1)} entities.")
    print(f"Dataset 2 has {len(d2)} entities.")

    comparisons = []
    for entities in block_collection:
        inner_block_1 = []
        inner_block_2 = []
        for entity in entities:
            if entity[0] == 1:
                inner_block_1.append(entity)
            else:
                inner_block_2.append(entity)
        comparisons.append(cartesian_product(inner_block_1, inner_block_2))

    print("Ground truth (duplicates):", len(ground_truth))

    allcomps = [comp for comparison in comparisons for comp in comparison]
    print("Suggested comparisons:", len(allcomps))
    print("Reduction Ratio: 1 - (", len(allcomps), "/", len(d1)*len(d2), ") =", (1 - (len(allcomps)/(len(d1)*len(d2))))*100, "%")

    correct = 0
    for duplicate in ground_truth:
        if tuple(duplicate) in allcomps:
            correct += 1
    print("Duplicates found (PC):", correct, "/", len(ground_truth), "=", (correct/len(ground_truth)) * 100, "%")
    print("Precision (PQ):", correct, "/", len(allcomps), "=", (correct/len(allcomps)) * 100, "%")
