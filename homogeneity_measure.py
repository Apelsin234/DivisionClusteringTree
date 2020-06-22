from scipy.spatial.distance import cdist
import numpy as np


def nearest_neighbor_distance(cluster, features, metric='euclidean'):
    cluster = cluster.loc[:, features]
    d = cdist(cluster, cluster, metric=metric)
    if d[d > 0].shape[0] == 0:
        return 0
    return d[d > 0].min() if d[d == 0].shape[0] <= cluster.shape[0] else 0


def most_distance_neighbor_distance(cluster, features, metric='euclidean'):
    cluster = cluster.loc[:, features]
    return cdist(cluster, cluster, metric=metric).max()


def mean_group_distance(cluster, features, metric='euclidean'):  # cluster -> pd.Dataframe
    cluster = cluster.loc[:, features]
    return np.mean(np.mean(cdist(cluster, cluster, metric=metric), axis=1))


def wards_distance(cluster, features, metric='euclidean'):
    cluster = cluster.loc[:, features]
    coef = cluster.shape[0] / 2
    return coef * distance_centroid(cluster, features, metric=metric)


def distance_centroid(cluster, features, metric='euclidean'):
    center = get_centroid(cluster, features)
    cluster = cluster.loc[:, features]
    return cdist(cluster, [center], metric=metric).sum()


def get_centroid(cluster, features):
    cluster = cluster.loc[:, features]
    return cluster.mean()
