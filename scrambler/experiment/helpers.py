def load_pairs(path):
    """
    Load pairs into list of lists
    :param path: Path to a file with spacer pairs
    :return: List of spacer pairs, where a spacer pair represent as a list of two spacers
    """
    with open(path) as f:
        lines = f.readlines()
    return [line.split() for line in lines]


def pairs_seq2id(spacer_pairs, spacer_to_cluster_index):  # TODO
    """
    Transform sequence representation of spacer pairs into clustering index representation
    :param spacer_pairs:
    :param spacer_to_cluster_index:
    :return:
    """
    pairs_idx = []
    for pair in spacer_pairs:
        if pair[0] in spacer_to_cluster_index and pair[1] in spacer_to_cluster_index:
            pairs_idx.append(
                [spacer_to_cluster_index[pair[0]], spacer_to_cluster_index[pair[1]]]
            )
    return pairs_idx
