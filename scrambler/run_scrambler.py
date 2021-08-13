import argparse

import tomlkit

from experiment.experiment import *

import os


def main():
    parser = argparse.ArgumentParser(
        description="SCRAMBLER_dev. CRISPR array reconstruction pipeline"
    )
    parser.add_argument(
        "-p",
        "--param_file",
        help="Path to the file (*.toml) with pipelines' running parameters",
        required=True,  type=os.path.abspath
    )
    parser.add_argument(
        "-i",
        "--input_pairs",
        help="Path to spacer pairs file",
        required=True, type=os.path.abspath
    )
    parser.add_argument(
        "-o",
        "--output_path",
        help="Path to output file with arrays",
        required=True,  type=os.path.abspath
    )
    args = parser.parse_args()

    with open(args.param_file, "r") as f:
        config = tomlkit.loads(f.read())

    experiment_1 = Experiment(pairs_path=args.input_pairs, minimum_sp_occurrences=5,)

    experiment_1.spacer_clustering(
        sorted_sequences=experiment_1.spacers_to_occurrences.keys(),
        clust_edit_distance_threshold=5,
    )

    experiment_1.graph_from_pairs()

    for assembly in config["assembly"].values():  # TODO

        threshold = assembly["use_threshold_filter"]
        svm = bool(assembly["use_svm_filter"])

        if assembly["svm_after_threshold"] == 0:
            svm_after_threshold = None
        elif assembly["svm_after_threshold"] == 1:
            svm_after_threshold = True
        else:
            svm_after_threshold = None

        experiment_1.run_experiment_filter_assembly(
            threshold=threshold,
            svm=svm,
            svm_after_threshold=svm_after_threshold,
            assembly_type=assembly["assembler"],
        )

    experiment_1.dump_arrays_to_file(args.output_path)
    experiment_1.dump_arrays_to_fasta(args.output_path)

    print("Array reconstruction completed!\n")


if __name__ == "__main__":
    main()
