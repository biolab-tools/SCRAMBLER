import numpy as np


class Node:
    visitedNodes = 0

    def __init__(self, node_id):
        self.node_id = node_id
        self.visited = False
        self.nextNodes = []


def dump_path(
    result, path, min_arr_len, node=False,
):
    new_path = path[:]
    if node:
        new_path += [node]
    new_patharr = []
    for node in new_path:
        new_patharr.append(node.node_id)
    if len(new_patharr) >= min_arr_len:
        result.append(new_patharr)


def manage_node(node, result, min_arr_len, path=None, used_nodes=None):
    if used_nodes is None:
        used_nodes = {}
    if path is None:
        path = []

    if not node.visited:
        Node.visitedNodes += 1
        node.visited = True
    if node.node_id in used_nodes:
        dump_path(result, path, min_arr_len, node)
        # dumpPath(result, path, node = False)
        # print('cycle')
        return
    if not node.nextNodes:
        dump_path(result, path, min_arr_len, node)
        return
    path.append(node)
    used_nodes[node.node_id] = True
    for nextNode in node.nextNodes:
        manage_node(nextNode, result, min_arr_len, path, used_nodes)
    path.pop()
    used_nodes.pop(node.node_id, None)


def soft_assembler(graph_init, min_arr_len):
    Node.visitedNodes = 0
    order = np.argsort(np.sum(graph_init, 0))
    graph_sorted = graph_init[:, order][order, :]
    nodes = dict(
        zip(
            np.arange(graph_sorted.shape[0]),
            [Node(k) for k in np.arange(graph_sorted.shape[0])],
        )
    )
    for k in np.arange(graph_sorted.shape[0]):
        for j in np.arange(graph_sorted.shape[1]):
            if graph_sorted[k, j] > 0:
                nodes[k].nextNodes.append(nodes[j])
    result = []
    i = 0
    graph_sorted_shape = graph_sorted.shape[0]
    while i < graph_sorted_shape and Node.visitedNodes < graph_sorted_shape:
        if not nodes[i].visited:
            manage_node(nodes[i], result, min_arr_len)
        i += 1
    for p in np.arange(len(result)):
        for n in np.arange(len(result[p])):
            result[p][n] = order[result[p][n]]
    return result
