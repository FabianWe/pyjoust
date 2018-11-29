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

import pytest

from .. import group


@pytest.mark.parametrize("teams,expected", [
    ([0, 1, 2], {(0, 1), (0, 2), (1, 2)}),
    ([1, 2], {(1, 2)}),
    ([], set()),
    ([0], set())
])
def test_all_matches(teams, expected):
    assert set(group.all_matches(teams)) == expected


@pytest.mark.parametrize("teams,expected", [
    ([], set()),
    ([0], set()),
    ([1, 2], {(1, 2), (2, 1)}),
    ([0, 1, 2], {(0, 1), (0, 2), (1, 2), (1, 0), (2, 0), (2, 1)})
])
def test_all_matches_bidirect(teams, expected):
    assert set(group.all_matches_bidirect(teams)) == expected


def test_round_robin_circle():
    # example from https://en.wikipedia.org/wiki/Round-robin_tournament#Scheduling_algorithm
    teams = list(range(1, 15))
    res = list(group.round_robin_circle(teams))
    assert len(res) == 13
    first_round = res[0]
    assert set(first_round) == {(1, 14), (2, 13), (3, 12), (4, 11), (5, 10), (6, 9), (7, 8)}
    second_round = res[1]
    assert set(second_round) == {(1, 13), (14, 12), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7)}
    third_round = res[2]
    assert set(third_round) == {(1, 12), (13, 11), (14, 10), (2, 9), (3, 8), (4, 7), (5, 6)}
    last_round = res[-1]
    assert set(last_round) == {(1, 2), (3, 14), (4, 13), (5, 12), (6, 11), (7, 10), (8, 9)}


@pytest.mark.parametrize("teams,expected", [
    (0, []),
    (1, []),
    (2, [[(1, 2)]]),
    (4,
     [
         [(1, 4), (2, 3)],
         [(4, 3), (1, 2)],
         [(2, 4), (3, 1)],
     ]),
    ([1, 2, 3],
     [
         [(2, 3)],
         [(1, 2)],
         [(3, 1)],
     ]),
    (8,
     [
         [(1, 8), (2, 7), (3, 6), (4, 5)],
         [(8, 5), (6, 4), (7, 3), (1, 2)],
         [(2, 8), (3, 1), (4, 7), (5, 6)],
         [(8, 6), (7, 5), (1, 4), (2, 3)],
         [(3, 8), (4, 2), (5, 1), (6, 7)],
         [(8, 7), (1, 6), (2, 5), (3, 4)],
         [(4, 8), (5, 3), (6, 2), (7, 1)],
     ]),
])
def test_berger_table(teams, expected):
    # compare with: https://fr.wikipedia.org/wiki/Table_de_Berger
    assert list(group.berger_table(teams)) == expected
