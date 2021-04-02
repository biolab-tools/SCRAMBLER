from multiprocessing import Pool

import numpy as np
import tqdm


class EmbeddingsCalculator:
    def __init__(self):
        self.embeddings = None
        self.argsort_gr_i = None
        self.argsort_gr_j = None

    def make_argsorts(self, gr):
        self.argsort_gr_i = np.zeros_like(gr)
        self.argsort_gr_j = np.zeros_like(gr)

        for i in range(gr.shape[0]):
            self.argsort_gr_i[i] = np.argsort(gr[i])
            self.argsort_gr_j[:, i] = np.argsort(gr[:, i])

    def fit_predict(self, graph, njobs=8):
        if self.argsort_gr_j is None or self.argsort_gr_i is None:
            self.make_argsorts(graph)

        if njobs > 1:
            p = Pool(njobs)
            inp = []
            for i in range(graph.shape[0]):
                for j in range(graph.shape[1]):
                    inp.append([graph, i, j])
            embs = p.map(self.get_vertex_emb, inp)
        else:
            embs = []
            for i in tqdm.tqdm(range(graph.shape[0])):
                for j in range(graph.shape[1]):
                    embs.append(self.get_vertex_emb((graph, i, j)))

        self.embeddings = np.stack(embs)
        return self.embeddings

    def get_vertex_emb(self, arg):
        gr, i, j = arg
        emb = []
        emb.extend(self.get_percentiles_fast(gr, i, j))
        emb.extend(self.get_ratios(gr, i, j))
        emb.extend(self.get_median_ratios_fast(gr, i, j))
        return np.array(emb)

    @staticmethod
    def get_percentiles(gr, i, j):
        return [
            np.where(np.argsort(gr[i]) == j)[0][0] / (gr.shape[0] - 1),
            np.where(np.argsort(gr[:, j]) == i)[0][0] / (gr.shape[0] - 1),
        ]

    def get_percentiles_fast(self, gr, i, j):
        return [
            np.where(self.argsort_gr_i[i] == j)[0][0] / (gr.shape[0] - 1),
            np.where(self.argsort_gr_j[:, j] == i)[0][0] / (gr.shape[0] - 1),
        ]

    @staticmethod
    def get_ratios(gr, i, j):
        return [gr[i, j] / max(1, gr[i].sum()), gr[i, j] / max(1, gr[:, j].sum())]

    @staticmethod
    def get_median_ratios(gr, i, j):
        return [
            np.log(gr[i, j] / max(1, np.median(gr[i])) + 1),
            np.log(gr[i, j] / max(1, np.median(gr[:, j])) + 1),
        ]

    def get_median_ratios_fast(self, gr, i, j):
        return [
            np.log(
                gr[i, j] / max(1, gr[i][self.argsort_gr_i[i][gr.shape[0] // 2]]) + 1
            ),
            np.log(
                gr[i, j] / max(1, gr[:, j][self.argsort_gr_j[:, j]][gr.shape[0] // 2])
                + 1
            ),
        ]
