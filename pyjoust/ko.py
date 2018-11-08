# -*- coding: utf-8 -*-

# Copyright 2018 Fabian Wenzelmann <fabianwen@posteo.eu>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .utils import JoustException


def _is_power_of_two(num):
    return ((num & (num - 1)) == 0) and num > 0


def _next_power_of_two(num):
    val = 1
    while val < num:
        val *= 2
    return val


class KOTreeNode(object):
    def __init__(self, team, desc=None, is_bye=False):
        self.team = team
        self.desc = desc
        self.is_bye = is_bye
        self.result = None

    def __str__(self):
        return 'Node: Team="%s" desc="%s" is_bye="%s"' % (self.team, self.desc, self.is_bye)

    def __repr__(self):
        return str(self)


class KOTree(object):
    def __init__(self, teams):
        is_ok = _is_power_of_two(len(teams))
        if not is_ok:
            raise JoustException('KOTree most be initialized with a power of two pairings')
        self.num_teams = len(teams)
        nodes = [ None for _ in range(2 * len(teams) - 1) ]
        for i, team in enumerate(reversed(teams), len(nodes) - len(teams)):
            if team is None:
                nodes[i] = KOTreeNode(team, is_bye=True)
            else:
                nodes[i] = KOTreeNode(team)
        self.nodes = nodes
        self.matches = dict()

    def set_match(self, first_node_id, second_node_id, result):
        first_node, second_node = self.nodes[first_node_id], self.nodes[second_node_id]
        if (first_node is None) or (second_node is None):
            raise JoustException('Invalid node id (no teams set yet)')
        first_node.result = result
        second_node.result = result
        self.matches[(first_node_id, second_node_id)] = result

    def get_match_result(self, first_node_id, second_node_id):
        return self.matches.get((first_node_id, second_node_id), None)

    def get_rows(self):
        n = self.num_teams
        next = 0
        num = len(self.nodes)
        result = []
        while n:
            row = []
            for _ in range(n):
                row.append(num - next - 1)
                next += 1
            result.append(row)
            n = n // 2
        return result

    def get_row(self, row_id):
        # probably nicer ways, but should be fine
        return self.get_rows()[row_id]

    @staticmethod
    def to_root(node_id):
        if node_id < 0:
            return []
        result = None
        n = node_id
        while True:
            result.append(n)
            if n == 0:
                return result
            n = KOTree.parent(n)

    @staticmethod
    def children(node_id):
        if node_id < 0:
            return None
        return 2 * node_id + 1, 2 * node_id + 2

    @staticmethod
    def parent(node_id):
        if node_id == 0:
            return None
        return (node_id - 1) // 2

    def get_matches(self, row):
        if type(row) == int:
            row = self.get_row(row)
        i, n = 0, len(row)
        while i < n:
            if i + 1 >= n:
                break
            yield row[i], row[i+1]
            i += 2
