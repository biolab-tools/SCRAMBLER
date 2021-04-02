import numpy as np


class Component:
    def __init__(self):
        self.chain = []

    def add_edge(self, edge):
        if len(self.chain) == 0:
            self.chain.append(edge[0])
            self.chain.append(edge[1])
            return True
        elif edge[0] == self.chain[-1]:
            self.chain.append(edge[1])
            return True
        elif edge[1] == self.chain[0]:
            self.chain.insert(0, edge[0])
            return True
        else:
            return False

    def allow_edge(self, edge):
        if len(self.chain) == 0:
            return True
        elif (
            not edge[0] in self.chain[:-1]
            and not edge[1] in self.chain[1:]
            and not (edge[0] == self.chain[-1] and edge[1] == self.chain[0])
        ):
            return True
        else:
            return False

    def require_edge(self, edge):
        if not self.allow_edge(edge):
            return False
        if edge[0] == self.chain[-1]:
            return True
        if edge[1] == self.chain[0]:
            return True

    def merge(self, component):
        if component.chain[0] == self.chain[-1]:
            self.chain.extend(component.chain[1:])
            return True
        elif component.chain[-1] == self.chain[0]:
            new_chain = component.chain
            new_chain.extend(self.chain[1:])
            self.chain = new_chain
            return True
        else:
            return False

    def __str__(self):
        return str(self.chain)

    def __repr__(self):
        return str(self.chain)


def greedy_assembler(graph, min_arr_len):
    components = {}
    name = 0

    non_zero_num = np.sum(graph > 0)
    i = (-graph).argsort(axis=None, kind="mergesort")
    j = np.unravel_index(i, graph.shape)
    edges = np.vstack(j).T[:non_zero_num]

    for edge in edges:
        if len(components) == 0:
            c = Component()
            c.add_edge(edge)
            components[name] = c
            name += 1
            # break
        else:
            if all([comp.allow_edge(edge) for comp in components.values()]):
                require_names = [
                    name for name in components if components[name].require_edge(edge)
                ]
                # print("rn", require_names)
                if len(require_names) == 0:
                    c = Component()
                    c.add_edge(edge)
                    components[name] = c
                    name += 1
                    # break
                elif len(require_names) == 1:
                    components[require_names[0]].add_edge(edge)
                    # break
                elif len(require_names) == 2:
                    components[require_names[0]].add_edge(edge)
                    components[require_names[0]].merge(components[require_names[1]])
                    components.pop(require_names[1])
                    # break
    weights = []
    comps_as_list = []

    for comp in components.values():
        if len(comp.chain) >= min_arr_len:
            comps_as_list.append(comp.chain)
            curr_weights = []
            for a, b in zip(comp.chain, comp.chain[1:]):
                curr_weights.append(graph[a][b])
            weights.append(curr_weights)

    return comps_as_list, weights
