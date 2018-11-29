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

from .utils import MatchResult, JoustException

import itertools
from operator import itemgetter
import re


class KubbResult(MatchResult):

    rx = re.compile(r"^\s*(?P<timeout>timeout:)?\s*(?P<first>\d*):(?P<second>\d*)\s*$")

    def __init__(self, first, second, timeout=False):
        self.first = first
        self.second = second
        self.timeout = timeout

    def __str__(self):
        return 'KubbResult(timeout=%s, first=%s, second=%s)' % (self.timeout, self.first, self.second)

    @staticmethod
    def parse(s):
        match = KubbResult.rx.match(s)
        if not match:
            raise JoustException('Invalid syntax for Kubb result in "%s"' % s)
        timeout = bool(match.group('timeout'))
        first = match.group('first')
        second = match.group('second')
        if (not first) and (not second):
            raise JoustException('Invalid syntax for Kubb result in "%s", at least one team must have remaining Kubbs' % s)
        try:
            if first:
                first = int(first)
            else:
                first = None
            if second:
                second = int(second)
            else:
                second = None
        except ValueError:
            raise JoustException('Invalid syntax for Kubb result in "%s": Invalid int' % s)
        return KubbResult(first, second, timeout)

    def winner(self):
        if self.first == self.second:
            return 'draw'
        if self.first > self.second:
            return 'two'
        else:
            return 'one'

    @staticmethod
    def sort_ranking(match_table):
        # TODO test
        left_map = dict()
        for team in match_table.points():
            left_map[team] = 0
        # iterate over each match
        for (team_one, team_two), entry in match_table.matches:
            assert isinstance(entry, KubbResult)
            if entry.first is not None:
                left_map[team_one] += entry.first
            if entry.second is not None:
                left_map[team_two] += entry.second
        ranking = []
        for team, points in match_table.points.items():
            ranking.append((team, points, -left_map[team]))
        ranking.sort(key=itemgetter(1, 2, 0))
        return ranking

    @staticmethod
    def compute_ranks(match_table):
        # TODO test
        ranking = KubbResult.sort_ranking(match_table)
        ranks = []
        for (points, left), r in itertools.groupby(ranking, key=itemgetter(1, 2)):
            ranks.append((points, left), [ e[0] for e in r ])
        return ranks
