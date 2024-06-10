from typing import Literal

import joblib
import numpy as np
import pandas as pd
import torch
import torch_geometric.utils
from networkit.nxadapter import nx2nk
from torch_geometric.data import Data, Dataset
from tqdm import tqdm

import numpy as np
from networkit.centrality import Betweenness
from networkit.distance import APSP
from networkit.graph import Graph
from networkit.linkprediction import JaccardIndex
from networkit.sparsification import LocalDegreeScore


# Custom scatter_min function
def scatter_min(src, index, dim_size):
    result = torch.full((dim_size,), float('inf'))
    for i in range(src.size(0)):
        result[index[i]] = min(result[index[i]], src[i])
    result[result == float('inf')] = 0
    return result

# Custom scatter_max function
def scatter_max(src, index, dim_size):
    result = torch.full((dim_size,), float('-inf'))
    for i in range(src.size(0)):
        result[index[i]] = max(result[index[i]], src[i])
    result[result == float('-inf')] = 0
    return result

# Custom scatter_mean function
def scatter_mean(src, index, dim_size):
    result = torch.zeros(dim_size)
    count = torch.zeros(dim_size)
    for i in range(src.size(0)):
        result[index[i]] += src[i]
        count[index[i]] += 1
    result = result / count
    result[count == 0] = 0
    return result

# Custom scatter_std function
def scatter_std(src, index, dim_size):
    mean = scatter_mean(src, index, dim_size)
    result = torch.zeros(dim_size)
    count = torch.zeros(dim_size)
    for i in range(src.size(0)):
        result[index[i]] += (src[i] - mean[index[i]]) ** 2
        count[index[i]] += 1
    result = torch.sqrt(result / count)
    result[count == 0] = 0
    return result

# Custom scatter_sum function
def scatter_sum(src, index, dim_size):
    result = torch.zeros(dim_size)
    for i in range(src.size(0)):
        result[index[i]] += src[i]
    return result


########


def calculate_shortest_paths(graph: Graph) -> np.array:
    # Networkit is faster than NetworkX for large graphs
    apsp = APSP(graph)
    apsp.run()
    path_lengths = apsp.getDistances(asarray=True)

    path_lengths = path_lengths.ravel()

    # filter out 0 length "paths" from node to itself
    path_lengths = path_lengths[np.nonzero(path_lengths)]

    # Networkit assigns extremely high values (~1e308) to mark infinite
    # distances for disconnected components, so we simply drop them
    path_lengths = path_lengths[path_lengths < 1e100]

    return path_lengths


def calculate_edge_betweenness(graph: Graph) -> np.ndarray:
    betweeness = Betweenness(graph, computeEdgeCentrality=True)
    betweeness.run()
    scores = betweeness.edgeScores()
    scores = np.array(scores, dtype=np.float32)
    return scores


def calculate_jaccard_index(graph: Graph) -> np.ndarray:
    jaccard_index = JaccardIndex(graph)
    scores = [jaccard_index.run(u, v) for u, v in graph.iterEdges()]
    scores = np.array(scores, dtype=np.float32)
    scores = scores[np.isfinite(scores)]
    return scores


def calculate_local_degree_score(graph: Graph) -> np.ndarray:
    local_degree_score = LocalDegreeScore(graph)
    local_degree_score.run()
    scores = local_degree_score.scores()
    return np.array(scores, dtype=np.float32)


########

def _extract_single_graph_features(
    data: Data,
    degree_sum: bool,
    shortest_paths: bool,
    edge_betweenness: bool,
    jaccard_index: bool,
    local_degree_score: bool,
) -> np.array:
    # adapted from PyTorch Geometric
    row, col = data.edge_index
    N = data.num_nodes

    deg = torch_geometric.utils.degree(row, N, dtype=torch.float)
    deg_col = deg[col]

    deg_min = scatter_min(deg_col, row, dim_size=N)
    deg_min[deg_min > 10000] = 0
    deg_max= scatter_max(deg_col, row, dim_size=N)
    deg_max[deg_max < -10000] = 0
    deg_mean = scatter_mean(deg_col, row, dim_size=N)
    deg_stddev = scatter_std(deg_col, row, dim_size=N)

    ldp_features = [
        deg.numpy(),
        deg_min.numpy(),
        deg_max.numpy(),
        deg_mean.numpy(),
        deg_stddev.numpy(),
    ]

    if degree_sum:
        deg_sum = scatter_sum(deg_col, row, dim_size=N)
        deg_sum = deg_sum.numpy()
        ldp_features.append(deg_sum)

    if any(
        [
            shortest_paths,
            edge_betweenness,
            jaccard_index,
            local_degree_score,
        ]
    ):
        graph = torch_geometric.utils.to_networkx(data, to_undirected=True)
        graph = nx2nk(graph)
        graph.indexEdges()

    if shortest_paths:
        sp_lengths = calculate_shortest_paths(graph)
        ldp_features.append(sp_lengths)

    if edge_betweenness:
        eb = calculate_edge_betweenness(graph)
        ldp_features.append(eb)

    if jaccard_index:
        ji = calculate_jaccard_index(graph)
        ldp_features.append(ji)

    if local_degree_score:
        lds = calculate_local_degree_score(graph)
        ldp_features.append(lds)

    # make sure that all features have the same dtype
    ldp_features = [feature.astype(np.float32) for feature in ldp_features]

    return ldp_features


def extract_features(
    dataset: Dataset,
    degree_sum: bool = False,
    shortest_paths: bool = False,
    edge_betweenness: bool = False,
    jaccard_index: bool = False,
    local_degree_score: bool = False,
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Calculates LDP features distributions for each graph, i.e. neighborhood
    degrees, mins, maxes, means and standard deviations. Optionally also
    calculates additional features.

    Returns Pandas DataFrame, where each column is of dtype np.ndarray, holding
    feature distribution.
    """
    if verbose:
        print("Extracting LDP features")

    iterable = tqdm(dataset) if verbose else dataset
    data = [
        _extract_single_graph_features(
            data,
            degree_sum,
            shortest_paths,
            edge_betweenness,
            jaccard_index,
            local_degree_score,
        )
        for data in iterable
    ]

    columns = [
        "deg",
        "deg_min",
        "deg_max",
        "deg_mean",
        "deg_stddev",
    ]
    if degree_sum:
        columns.append("deg_sum")
    if shortest_paths:
        columns.append("shortest_paths")
    if edge_betweenness:
        columns.append("edge_betweenness")
    if jaccard_index:
        columns.append("jaccard_index")
    if local_degree_score:
        columns.append("local_degree_score")

    return pd.DataFrame(data, columns=columns)


def process_row(
    row,
    columns: list[str],
    n_bins: int,
    normalization: Literal["none", "graph", "dataset"] = "graph",
    aggregation: Literal["histogram", "EDF"] = "histogram",
    log_degree: bool = False,
):
    x = np.empty(len(columns) * n_bins, dtype=np.float32)

    # features that use logarithm of values if log_degree is True
    log_features = [
        "deg",
        "deg_min",
        "deg_max",
        "deg_mean",
    ]

    col_start = 0
    col_end = n_bins

    for col_idx, col_name in enumerate(columns):
        values = row[col_idx]

        if log_degree is True and col_name in log_features:
            # add small value to avoid problems with degree 0
            values = np.log(values + 1e-3)

        density = True if normalization == "graph" else None

        # assume "histogram" aggregation by default, since we have to use some
        # aggregation, and EDF is just used on top of histogram
        values, _ = np.histogram(values, bins=n_bins, density=density)

        if aggregation == "EDF":
            # calculate empirical CDF from histogram bins
            values = np.cumsum(values)
            if density:
                # normalize again after summation if needed
                values /= values.max()

        x[col_start:col_end] = values
        col_start += n_bins
        col_end += n_bins

    return x


def calculate_features_matrix(
    ldp_features: pd.DataFrame,
    n_bins: int,
    normalization: Literal["none", "graph", "dataset"] = "graph",
    aggregation: Literal["histogram", "EDF"] = "histogram",
    log_degree: bool = False,
) -> np.ndarray:
    if normalization == "dataset":
        # turn off Pandas warning about setting with copy, we know what we're doing
        pd.options.mode.chained_assignment = None

        for col_name in ldp_features.columns:
            # select max absolute feature value among all values of that feature
            # in the dataset, and normalize using it
            feature_values = ldp_features[col_name].to_numpy()
            max_value = np.max([np.max(np.abs(vals)) for vals in feature_values])
            feature_values = [vals / max_value for vals in feature_values]
            ldp_features[col_name] = feature_values

        pd.options.mode.chained_assignment = "warn"

    args = dict(
        columns=ldp_features.columns,
        n_bins=n_bins,
        normalization=normalization,
        aggregation=aggregation,
        log_degree=log_degree,
    )

    n_jobs = joblib.cpu_count(only_physical_cores=True)
    parallel = joblib.Parallel(n_jobs=n_jobs, backend="loky")
    jobs = (joblib.delayed(process_row)(row, **args) for row in ldp_features.to_numpy())
    rows = parallel(jobs)

    X = np.stack(rows)

    return X