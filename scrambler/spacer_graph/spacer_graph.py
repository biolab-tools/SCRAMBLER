import itertools
from collections import namedtuple

import numpy as np

GraphKey = namedtuple("GraphKey", ["threshold", "svm", "svm_after_threshold"])


class SpacerGraph:
    def __init__(self, sp_lists, threshold=0, svm=False, svm_after_threshold=None):
        self.threshold = threshold
        self.svm = svm
        self.svm_after_threshold = svm_after_threshold

        self.graph_adjmatrix, _ = self.graph_from_sp_lists(sp_lists)

    @staticmethod
    def graph_from_sp_lists(sp_lists, spacers_num=None):  # TODO
        if spacers_num is None:
            spacers_num = len(set(itertools.chain(*sp_lists))) + 1

        graph = np.zeros((spacers_num, spacers_num), dtype=int)
        errors = 0

        for arr in sp_lists:
            for x, y in zip(arr, arr[1:]):
                if x < spacers_num and y < spacers_num:
                    graph[x, y] += 1
                else:
                    errors += 1

        return graph, errors

    def get_key(self):
        return GraphKey(self.threshold, self.svm, self.svm_after_threshold)
