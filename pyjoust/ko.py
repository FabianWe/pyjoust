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
    val = 1
    i = 0
    while val < num:
        val *= 2
        i += 1
    return val == num, i


def _next_power_of_two(num):
    val = 1
    while val < num:
        val *= 2
    return val


def children(node_id):
    return 2 * node_id + 1, 2 * node_id + 2


def parent(node_id):
    return (node_id - 1) // 2


class KOTreeNode(object):
    def __init__(self, team, desc=None):
        self.team = team
        self.desc = desc


class KOTree(object):
    def __init__(self, teams):
        is_ok, log = _is_power_of_two(len(teams))
        if not is_ok:
            raise JoustException('KOTree most be initialized with a power of two pairings')
        nodes = [ None for _ in range(2 * len(teams) - 1) ]
        for i, team in enumerate(teams, len(nodes) - len(teams)):
            nodes[i] = KOTreeNode(team)
        self.nodes = nodes

    def to_root(self, node_id):
        result = None
        n = node_id
        while True:
            result.append(n)
            if n == 0:
                return result
            n = parent(n)
