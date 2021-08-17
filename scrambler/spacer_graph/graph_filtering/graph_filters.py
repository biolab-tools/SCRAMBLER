import os
import pickle
from copy import deepcopy

from definitions import PRETRAINED_FILTERS_PATH
from spacer_graph.graph_filtering.embeddings_calculator import EmbeddingsCalculator


def threshold_filtering(graph, threshold):
    if graph.threshold > 0:
        raise NameError("The graph has been already filtered by threshold")
    else:
        new_graph = deepcopy(graph)
        new_graph.threshold = threshold
        new_graph.graph_adjmatrix[new_graph.graph_adjmatrix < threshold] = 0

        return new_graph


def logreg_filtering(graph):
    new_graph = deepcopy(graph)

    if graph.logreg:
        raise NameError("The graph has been already filtered with LogReg model")
    elif graph.threshold > 0:
        new_graph.logreg_after_threshold = True

    new_graph.logreg = True
    emb_calc = EmbeddingsCalculator()
    chimera_filter = LogRegFilter()
    embs_filt_logreg = emb_calc.fit_predict(graph.graph_adjmatrix)
    new_graph.graph_adjmatrix = chimera_filter.filter_graph(
        graph.graph_adjmatrix, embs_filt_logreg
    )

    return new_graph


class LogRegFilter:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(
                PRETRAINED_FILTERS_PATH, "lr_rep_to_rep_sklearn0.22"
            )

        self.filter = pickle.load(open(model_path, "rb"))

    def filter_graph(self, graph, embeddings=None):
        return self.filter.predict(embeddings).reshape(graph.shape) * graph
