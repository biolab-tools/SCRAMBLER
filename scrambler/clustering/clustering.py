from collections import Counter, OrderedDict

import editdistance as ed
from tqdm import tqdm


def get_ordered_sequences_freq_dict(sequences, min_occurences):
    sequences_freq = Counter(sequences).most_common()
    return OrderedDict(
        (x, count) for x, count in sequences_freq if count > min_occurences
    )


def sequences_clustering(sorted_sequences, threshold):
    clusters_to_index = {}
    item_to_cluster_index = {}
    cluster_index = 0

    for item in tqdm(sorted_sequences, ncols=90):
        if len(clusters_to_index) == 0:
            clusters_to_index[item] = cluster_index
            item_to_cluster_index[item] = cluster_index
            cluster_index += 1
        else:
            min_edit_distance, reference_cluster = find_closest(
                list(clusters_to_index.keys()), item
            )
            if min_edit_distance <= threshold:
                item_to_cluster_index[item] = clusters_to_index[reference_cluster]
            else:
                clusters_to_index[item] = cluster_index
                item_to_cluster_index[item] = cluster_index
                cluster_index += 1

    return clusters_to_index, item_to_cluster_index


def find_closest(iterable, item):
    """
    Finds closest in iterable d to item
    :param iterable:
    :param item:
    :return:
    """
    if len(iterable) == 0:
        return len(item), -1

    min_ed = ed.eval(next(iter(iterable)), item)
    iterable_elements = set(iterable)

    for target_item in iterable_elements:
        dist = ed.eval(item, target_item)
        if dist <= min_ed:
            min_ed = dist
            answ_item = (min_ed, target_item)

    return answ_item
