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


from .group import ThreePointsTable, all_matches_bidirect
from .utils import JoustException


class NoMatchException(JoustException):
    pass


class SwissMatchSet(object):
    def __init__(self):
        self.elements = set()

    @staticmethod
    def _get_entry(first, second):
        if first < second:
            return first, second
        else:
            return second, first

    def add(self, first, second):
        t = self._get_entry(first, second)
        self.elements.add(t)

    def __len__(self):
        return len(self.elements)

    def __contains__(self, item):
        first, second = item
        t = self._get_entry(first, second)
        return t in self.elements

    def __str__(self):
        return str(self.elements)

    def __repr__(self):
        return repr(self.elements)


class SwissRound(object):
    def __init__(self):
        self.results = dict()

    def add_match(self, team_one, team_two, result=None):
        self.results[(team_one, team_two)] = result
        self.results[(team_two, team_one)] = result


class SwissSystem(object):
    def __init__(self, teams, table_class=ThreePointsTable):
        self.teams = teams
        self.rounds = []
        self.by_count = dict()
        # TODO check if this is correct
        all_matches = all_matches_bidirect(teams)
        self.table = table_class(teams, all_matches)
        self.match_set = SwissMatchSet()
        for team in teams:
            self.by_count[team] = 0

    def next_round(self):
        ranking = self.table.sort_ranking()
        by = None
        if len(self.teams) % 2 != 0:
            by = self.select_by(ranking)
        round = []
        while ranking:
            # get next best player
            next = ranking.pop(0)
            next_team = next[0]
            if by is not None and by == next_team:
                continue
            # get candidate, that is the next player
            if not ranking:
                raise JoustException("Something went wrong, can't compute competitor for %s" % next)
            competitor_id = None
            for i, candidate in enumerate(ranking):
                # test if match already took place
                if (next, candidate) not in self.match_set:
                    competitor_id = i
                    break
            if competitor_id is None:
                raise NoMatchException("Can't find match for %s" % next)
            competitor = ranking.pop(competitor_id)
            round.append((next, competitor))
            self.match_set.add(next, competitor)
        return round

    def select_by(self, ranking=None):
        if ranking is None:
            ranking = self.table.sort_ranking()
        ranking_map = dict()
        for i, entry in enumerate(ranking):
            team = entry[0]
            ranking[team] = i
        min_by = []
        current_min = None
        for team, count in self.by_count:
            if current_min is None or count < current_min:
                current_min = count
                min_by = [team]
            elif count == current_min:
                min_by.append(team)
        if current_min is None:
            raise JoustException("Can't select by, no team given")
        assert len(min_by) > 0
        highest_rank = None
        selected = None
        for team in min_by:
            rank = ranking_map[team]
            if highest_rank is None or selected > highest_rank:
                highest_rank = team
        assert highest_rank is not None
        self.by_count[selected] += 1
        return selected

