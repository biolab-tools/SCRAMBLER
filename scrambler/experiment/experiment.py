import itertools

import clustering.clustering as clust
import spacer_graph.spacer_graph as sp_graph
from assembly.greedy_assembler import greedy_assembler
from assembly.soft_assembler import soft_assembler
from experiment.helpers import *
from spacer_graph.graph_filtering.graph_filters import *
from spacer_graph.spacer_graph import GraphKey


class Experiment:
    def __init__(self, pairs_path, minimum_sp_occurrences=5):
        print("- Loading spacer pairs...")

        # Parameters
        self.clust_edit_distance_threshold = None

        self.spacer_pairs = load_pairs(pairs_path)
        self.spacers = set(itertools.chain(*self.spacer_pairs))

        self.spacers_to_occurrences = clust.get_ordered_sequences_freq_dict(
            list(itertools.chain(*self.spacer_pairs)), minimum_sp_occurrences
        )

        # Clustering output variables
        self.cluster_to_index = None
        self.spacer_to_cluster_index = None
        self.pairs_idx = None

        self.index_to_cluster = None

        # Graphs
        self.graph_dict = {}

        # Assembly
        self.arrays_dict = {}

    def spacer_clustering(self, sorted_sequences, clust_edit_distance_threshold=5):
        print("- Clustering spacers...\n")
        self.clust_edit_distance_threshold = clust_edit_distance_threshold

        (
            self.cluster_to_index,
            self.spacer_to_cluster_index,
        ) = clust.sequences_clustering(
            sorted_sequences, self.clust_edit_distance_threshold
        )

        self.index_to_cluster = {v: k for k, v in self.cluster_to_index.items()}

        self.pairs_idx = pairs_seq2id(self.spacer_pairs, self.spacer_to_cluster_index)

    def graph_from_pairs(self):
        print("\n- Creating spacer pairs graph...")
        if self.pairs_idx is not None:
            graph = sp_graph.SpacerGraph(self.pairs_idx)
            self.graph_dict[graph.get_key()] = graph

    def filter_graph_logreg(self, graph):
        print("- Filtering graph using LogReg-filter...")
        logreg_graph = logreg_filtering(graph)
        self.graph_dict[logreg_graph.get_key()] = logreg_graph

    def filter_graph_threshold(self, graph, threshold):
        print("- Filtering graph using thresholding...")
        threshold_graph = threshold_filtering(graph, threshold)
        self.graph_dict[threshold_graph.get_key()] = threshold_graph

    def restore_arrays_soft(self, graph, min_arr_len):
        print("- Restoring CRISPR arrays (soft)...")
        self.arrays_dict[("soft", graph.get_key())] = soft_assembler(
            graph.graph_adjmatrix, min_arr_len
        )

    def restore_arrays_greedy(self, graph, min_arr_len):
        print("- Restoring CRISPR arrays (greedy)...")
        self.arrays_dict[("greedy", graph.get_key())] = greedy_assembler(
            graph.graph_adjmatrix, min_arr_len
        )[0]

    def dump_arrays_to_file(self, output_file_path):
        print("- Saving arrays to file...")
        with open(output_file_path + "/output_arrays.txt", "w") as file:
            dump_data = ""
            for group_key, arrs in self.arrays_dict.items():
                if len(arrs) > 0:
                    dump_data += "@ASSEMBLER\t" + group_key[0] + "\n"
                    dump_data += "@FILTERING_OPTIONS\n"
                    dump_data += "@THRESHOLD\t" + str(group_key[1].threshold) + "\n"
                    dump_data += "@LOGREG\t" + str(group_key[1].logreg) + "\n"
                    if group_key[1].logreg_after_threshold is None:
                        logreg_after_threshold = False
                    dump_data += (
                        "@LOGREG_AFTER_THRESHOLD\t" + str(logreg_after_threshold) + "\n\n"
                    )

                    i = 0
                    for arr_idx in arrs:
                        i += 1
                        arr_seq = [self.index_to_cluster[idx] for idx in arr_idx]
                        dump_data += (
                            "@ARRAY\t" + str(i) + "\t" + "\t".join(arr_seq) + "\n"
                        )

                    dump_data += "\n"

            file.write(dump_data)

    def dump_arrays_to_fasta(self, fasta_output_file_path):
        with open(fasta_output_file_path + "/output_arrays.fasta", "w") as file:
            dump_data = ""
            for group_key, arrs in self.arrays_dict.items():
                if len(arrs) > 0:
                    header = ">ASSEMBLER_" + group_key[0] + "|"
                    header += "THRESHOLD_" + str(group_key[1].threshold) + "|"
                    header += "LOGREG_" + str(group_key[1].logreg) + "|"
                    if group_key[1].logreg_after_threshold is None:
                        logreg_after_threshold = False
                    header += "LOGREG_AFTER_THRESHOLD_" + str(logreg_after_threshold) + "|"

                    for arr_num, arr_idx in enumerate(arrs, 1):
                        for sp_num, sp_idx in enumerate(arr_idx):
                            dump_data += (
                                header
                                + "ARRAY_"
                                + str(arr_num)
                                + "|SP_"
                                + str(sp_num)
                                + "\n"
                                + self.index_to_cluster[sp_idx]
                                + "\n"
                            )

            file.write(dump_data)

    def run_assembly_specified_by_type(self, graph, assembly_type, min_arr_len):
        if assembly_type == "soft":
            self.restore_arrays_soft(graph, min_arr_len)
        elif assembly_type == "greedy":
            self.restore_arrays_greedy(graph, min_arr_len)

    def run_experiment_filter_assembly(  # TODO
        self, threshold, logreg, logreg_after_threshold, assembly_type
    ):

        filter_params = GraphKey(
            threshold=threshold, logreg=logreg, logreg_after_threshold=logreg_after_threshold
        )

        if (assembly_type, filter_params,) in self.arrays_dict:
            return

        if filter_params not in self.graph_dict:
            if logreg_after_threshold is None:
                if logreg:
                    if (
                        GraphKey(threshold=0, logreg=True, logreg_after_threshold=None)
                        not in self.graph_dict
                    ):
                        self.filter_graph_logreg(
                            self.graph_dict[
                                GraphKey(
                                    threshold=0, logreg=False, logreg_after_threshold=None
                                )
                            ]
                        )

                if threshold > 0:
                    self.filter_graph_threshold(
                        self.graph_dict[
                            GraphKey(threshold=0, logreg=logreg, logreg_after_threshold=None)
                        ],
                        threshold,
                    )
            else:
                if threshold > 0:
                    self.filter_graph_threshold(
                        self.graph_dict[
                            GraphKey(threshold=0, logreg=False, logreg_after_threshold=None)
                        ],
                        threshold,
                    )

                self.filter_graph_logreg(
                    self.graph_dict[
                        GraphKey(
                            threshold=threshold, logreg=False, logreg_after_threshold=None
                        )
                    ]
                )

        self.run_assembly_specified_by_type(
            self.graph_dict[filter_params], assembly_type, min_arr_len=3
        )
