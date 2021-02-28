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
