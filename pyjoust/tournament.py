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

import abc
import itertools
import uuid

from .utils import JoustException, toss_coin
from .group import ThreePointsTable, round_robin_circle
from .ko import KOTree

class AdditionalMatch(object):
    def __init__(self, team_one, team_two, result=None):
        self.team_one = team_one
        self.team_two = team_two
        self.result = result


class TieBreaker(abc.ABC):
    @abc.abstractmethod
    def break_tie(self):
        # TODO returns either 'one' or 'two' or raises JoustException
        pass

class RematchBreaker(TieBreaker):
    def __init__(self, team_one, team_two, result=None):
        self.team_one = team_one
        self.team_two = team_two
        self.result = result

    def break_tie(self):
        if self.result is None:
            raise JoustException('No result set for rematch')
        cmp = self.result.winner()
        if cmp == 'draw':
            raise JoustException('Result for rematch is draw')
        return cmp


class CoinTieBreaker(TieBreaker):
    def __init__(self, team_one, team_two):
        self.team_one = team_one
        self.team_two = team_two
        toss = toss_coin()
        if toss:
            self.result = 'one'
        else:
            self.result = 'two'

    def break_tie(self):
        return self.result


class GroupPhase(object):
    def __init__(self, groups, table_class=ThreePointsTable, scheduler=round_robin_circle):
        self.groups = groups
        self.tables = []
        self.rounds = []
        for group in groups:
            rounds = list(scheduler(group))
            self.rounds.append(rounds)
            match_tuples = itertools.chain.from_iterable(rounds)
            next_table = table_class(group, match_tuples)
            self.tables.append(next_table)


class KOPhase(object):
    def __init__(self, teams):
        self.teams = teams
        self.tree = KOTree(teams)


class TournamentPhase(object):
    def __init__(self, phase):
        self.phase = phase
        self.final_result = None
        self.tie_breakers = dict()
        self.additional_matches = dict()

    def add_tie_breaker(self, value, key=None):
        if key is None:
            key = uuid.uuid4()
        self.tie_breakers[key] = value
        return key

class Tournament(object):
    def __init__(self):
        self.rounds = dict()

    def add_phase(self, value, key=None):
        if key is None:
            key = uuid.uuid4()
        self.rounds[key] = value
        return key
