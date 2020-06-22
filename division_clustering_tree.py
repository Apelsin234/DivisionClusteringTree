import numpy as np
import homogeneity_measure
from tree_node import TreeNode


class DivisionClusteringTree:

    def __init__(self, division_rules, motivations_cols, max_depth=-1, min_size=-np.inf,
                 distance_method='mean_group_distance',
                 distance_metric='euclidean'):
        self.division_rules = division_rules
        self.max_depth = max_depth
        self.min_size = min_size
        if distance_method in ['nearest_neighbor_distance', 'most_distance_neighbor_distance',
                               'mean_group_distance', 'wards_distance', 'distance_centroid']:
            self.distance_method = distance_method
            self.distance_function = \
                lambda cluster: getattr(homogeneity_measure, distance_method)(cluster, motivations_cols,
                                                                              metric=distance_metric)
        else:
            raise Exception('this distance_method doesn\'t exist')

    def _number_features(self, data, feature):
        suffix = ""
        best_res = np.inf
        best_i = None
        for i in range(data[feature].max()):
            prt1 = data[(data[feature] > i)]
            prt2 = data[(data[feature] <= i)]
            if prt1.shape[0] == 0 or prt2.shape[0] == 0:
                current_similarity = np.inf
            else:
                current_similarity = prt1.shape[0] / data.shape[0] * self.distance_function(prt1) + \
                                     prt2.shape[0] / data.shape[0] * self.distance_function(prt2)
            if current_similarity != np.nan and current_similarity < best_res:
                best_res = current_similarity
                suffix = " >" + str(i)
                best_i = i
        return best_res, suffix, (data[feature] <= best_i), (data[feature] > best_i)

    def fit(self, data):
        x = self.__fit(data)
        x.build_id()
        return x

    def __fit(self, data, current_level=0):
        if current_level == self.max_depth or data.shape[0] <= self.min_size:
            node = TreeNode()
            node.is_leaf = True
            node.value = data
            node.amount_objects_in_subtree = data.shape[0]
            node.homogeneity_measure = self.distance_function(data)
            return node

        best_rule = None
        suffix = ""
        best_res = np.inf
        cond_1 = None
        cond_2 = None
        for rule in self.division_rules:
            ans = self._number_features(data, rule)

            if ans[0] != np.nan and ans[0] < best_res:
                best_res, suffix, cond_1, cond_2 = ans
                best_rule = rule

        if best_rule is None:
            node = TreeNode()
            node.is_leaf = True
            node.value = data
            node.amount_objects_in_subtree = data.shape[0]
            node.homogeneity_measure = self.distance_function(data)
            return node

        rule_label = best_rule + suffix

        left_tree = self.__fit(data[cond_1], current_level=current_level + 1)
        right_tree = self.__fit(data[cond_2], current_level=current_level + 1)

        node = TreeNode()
        node.left_node = left_tree
        node.right_node = right_tree
        left_tree.parent = node
        right_tree.parent = node
        node.amount_objects_in_subtree = data.shape[0]
        node.division_rule = rule_label
        node.homogeneity_measure = best_res
        return node
