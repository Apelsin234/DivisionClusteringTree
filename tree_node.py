import pandas as pd
import json


class TreeNode:
    def __init__(self):
        self.id = -1
        self.is_leaf = False
        self.value = None  # только в листах, для экономии места
        self.left_node = None
        self.right_node = None
        self.parent = None
        self.amount_objects_in_subtree = 0
        self.division_rule = None
        self.homogeneity_measure = None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def build_id(self):
        if self.parent is None:
            self.id = 0
        else:
            parent_id = self.parent.id
            if self.parent.left_node == self:
                self.id = parent_id * 2 + 1
            else:
                self.id = parent_id * 2 + 2

        if not self.is_leaf:
            self.left_node.build_id()
            self.right_node.build_id()

    def get_mean_homogeneity_measure_in_leaves(self):
        """
        Получить усредненную меру гомогенности из листьев
        """
        hm, amount_children = self.__get_sum_homogeneity_measure_in_leaves()
        return hm / amount_children

    def __get_sum_homogeneity_measure_in_leaves(self):
        if not self.is_leaf:
            ans_l = self.left_node.__get_sum_homogeneity_measure_in_leaves()
            ans_r = self.right_node.__get_sum_homogeneity_measure_in_leaves()
            hm = ans_l[0] + ans_r[0]
            amount_children = ans_l[1] + ans_r[1]
            return hm, amount_children
        else:
            return self.homogeneity_measure, 1

    def to_json(self):
        """
        Преобразовать дерево в json, при этом сохраняется только структура, а данные отбрасываются
        n - через запятую: идентификатор, правило разбиения(если это не лист), значение меры гомогенности
        d - количество объектов в данной вершине
        с - дети
        """
        return {"n": str(self.id) + ("" if self.is_leaf else ", " + self.division_rule) + ", " + str(self.homogeneity_measure),
                "d": self.amount_objects_in_subtree,
                # "h": self.homogeneity_measure,
                "c": ([] if self.is_leaf else [self.left_node.to_json(), self.right_node.to_json()])}

    def to_array(self, height=0):
        """
        Преобразует дерево в формат массива с доп информацией
        """
        cur = [(self.id, height, self.homogeneity_measure, ("" if self.is_leaf else self.division_rule),
                self.amount_objects_in_subtree)]
        if self.is_leaf:
            return cur
        l = self.left_node.to_array(height=height + 1)
        r = self.right_node.to_array(height=height + 1)

        return cur + l + r

    @staticmethod
    def from_json_file_and_data(data, filename='examples/test/result.json'):
        """
        Востанавливает из сохраненного ранее json файла дерево
        :param data: данные по которым производилось разбиение
        :param filename: файл куда сохранили преобразованное в json дерево
        :return: Дерево, построенное с помощью структуры из json и исходных данных
        """
        with open(filename) as f:
            d = json.load(f)
        return TreeNode.from_json_and_data(data, d)

    @staticmethod
    def from_json_and_data(data, json_tree):
        """
        Востанавливает из сохраненного ранее json дерево
        :param data: данные по которым производилось разбиение
        :param json_tree: структура дерева полученная при вызове метода to_json()
        :return: Дерево, построенное с помощью структуры из json и исходных данных
        """
        if data.shape[0] != json_tree['d']:
            raise Exception('WOW')
        node = TreeNode()
        node.is_leaf = len(json_tree['c']) == 0
        split_label = json_tree['n'].split(', ')
        node.id = int(split_label[0])
        # node.homogeneity_measure = float(json_tree['h'])
        node.amount_objects_in_subtree = int(json_tree['d'])
        if node.is_leaf:
            node.value = data
            node.homogeneity_measure = float(split_label[1])
        else:
            node.division_rule = split_label[1]
            node.homogeneity_measure = float(split_label[2])
            rule, num = node.division_rule.split(' >')
            num = int(num)

            l = TreeNode.from_json_and_data(data[data[rule] <= num], json_tree['c'][0])
            r = TreeNode.from_json_and_data(data[data[rule] > num], json_tree['c'][1])
            node.left_node = l
            node.right_node = r
            node.left_node.parent = node
            node.right_node.parent = node
        return node

    # получить данные в поддереве по TreeNode
    def get_data_in_subtree(self):
        """
        При вызове возвращает данные в этом узле
        """
        if self.is_leaf:
            return self.value

        return pd.concat([self.left_node.get_data_in_subtree(), self.right_node.get_data_in_subtree()],
                         ignore_index=True)

    def get_data_in_subtree_by_id(self, node_id):
        """
        Возвращает по идентификатору вершины данные которые дошли до этой вершины
        :param node_id: идентификатор вершины
        :return:
        """
        ind = []
        n = node_id
        tree = self
        while n != 0:
            n -= 1
            ind.append(n % 2)
            n //= 2
        for i in reversed(ind):
            tree = tree.left_node if i == 0 else tree.right_node
        if tree.id != node_id:
            raise Exception("WOW")
        return tree.get_data_in_subtree()

    def get_division_rules_by_id(self, node_id):
        """
        Получить список правил разделения для вершины по её идентификатору
        :param node_id: идентификатор вершины
        :return:
        """
        ind = []
        rules = []
        n = node_id
        tree = self
        while n != 0:
            n -= 1
            ind.append(n % 2)
            n //= 2
        for i in reversed(ind):
            rules.append(tree.division_rule + ' = ' + str(i != 0))
            tree = tree.left_node if i == 0 else tree.right_node
        if tree.id != node_id:
            raise Exception("WOW")
        return rules

    def export_data_in_subtree_by_id_to_xls(self, node_id, filename='result.xls'):
        """
        Экспортировать данные из вершины по идентификатору в файл xls формата
        :param node_id:  идентификатор вершины
        :param filename: имя файла
        """
        data_in_subtree = self.get_data_in_subtree_by_id(node_id)
        data_in_subtree.to_excel(filename, index=False)
