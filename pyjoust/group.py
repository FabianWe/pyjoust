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

import itertools
from operator import itemgetter
import random


class UnregisteredGroupException(Exception):
    pass


class MatchException(Exception):
    pass

def get_group_num(group_size, num_participants, additional_group=True):
    res = num_participants // group_size
    if additional_group and num_participants % group_size != 0:
        res += 1
    return res


def group_sizes(group_size, num_participants, additional_group=True):
    if group_size <= 0:
        return
    # additional logic, not just calling get_group_num
    num_groups = num_participants // group_size
    rest = num_participants % group_size
    for i in range(num_groups):
        if additional_group:
            yield group_size
        else:
            if rest and i <= rest:
                yield group_size + 1
            else:
                yield group_size
    if additional_group and rest:
        yield rest


def groups_by_size(
        group_size,
        participants,
        shuffle=False,
        additional_group=True):
    if group_size <= 0:
        return []
    num_participants = len(participants)
    if shuffle:
        # don't use shuffle to avoid changing the input
        participants = random.sample(participants, num_participants)
    result = []
    start = 0
    for group_size in group_sizes(
            group_size,
            num_participants,
            additional_group):
        next_group = participants[start:start + group_size]
        result.append(next_group)
        start += group_size
    return result


def groups_by_number(num_groups, participants, shuffle=False):
    if num_groups <= 0:
        return []
    group_size = len(participants) // num_groups
    return groups_by_size(
        group_size,
        participants,
        shuffle=shuffle,
        additional_group=False)


def round_robin(group):
    return itertools.combinations(group, 2)


def toss_coin():
    return random.randint(0, 1) == 0


# match handler interface:
# must be able to:
# hold the actual matches
# compare results of a match (compute a reward for teams)
# sort the teams (given global score and internal information)
# how do we connect a GroupTournament to a match handler? input types might
# be different!
# provide a from_string method

# methods:
# from_string: string --> required representation for match result
# score: rep --> (int, int)
# compare: complicated

class Table(object):
    def __init__(self, group):
        super().__init__()
        self.points = dict()
        for team in group:
            self.points[team] = self.empty_value()

    def empty_value(self):
        # overwrite in sub classes
        return 0


    def set_points(self, team, points):
        if team not in self.points:
            raise MatchException('Invalid team name "%s"' % str(team))
        self.points[team] = points

    def increase_points(self, team, by):
        if team not in self.points:
            raise MatchException('Invalid team name "%s"' % str(team))
        self.points[team] += by

    def check_exists(self, *args):
        for team in args:
            if team not in self.points:
                raise MatchException('Invalid team name "%s"' % str(team))


    def sort_ranking(self):
        ranking = []
        for team, points in self.points.items():
            ranking.append((team, points))
        ranking.sort(key=itemgetter(1, 0))
        return ranking


    def compute_ranks(self):
        ranking = self.sort_ranking()
        ranks = []
        for _, r in itertools.groupby(ranking, key=itemgetter(1)):
            ranks.append(list(r))
        return ranks

    def set_match_from_string(self, team_one, team_two, s):
        # TODO throw exception here or is it fine to ignore it?
        pass


class ThreePointsTable(Table):
    def __init__(self, group, matches_tuples, win=3, draw=1, lose=0):
        super().__init__(group)
        self.win, self.draw, self.lose = win, draw, lose
        self.matches = dict()
        for first, second in matches_tuples:
            self.matches[(first, second)] = None

    def check_match_exists(self, *args):
        for t in args:
            if t not in self.matches:
                raise MatchException('Invalid match: "%s vs %s"' % (str(t[0]), str(t[1])))

    def set_match_from_string(self, team_one, team_two, s):
        # first check that teams are valid (before changing anything)
        self.check_exists(team_one, team_two)
        self.check_match_exists(team_one, team_two)
        split = s.split(':')
        if len(split) != 2:
            raise MatchException('Must be of form "a:b", got ' + str(s))
        first, second = split[0], split[1]
        try:
            first, second = int(first), int(second)
        except ValueError:
            raise MatchException('Must be of form "a:b" with valid integers, got ' + str(s))
        if first == second:
            # both get draw points
            self.increase_points(team_one, self.draw)
            self.increase_points(team_two, self.draw)
        elif first > second:
            # team one wins
            self.increase_points(team_one, self.win)
            self.increase_points(team_two, self.lose)
        else:
            # second team wins
            self.increase_points(team_one, self.lose)
            self.increase_points(team_two, self.win)


if __name__ == '__main__':
    p = ['Part. %d' % i for i in range(15)]
    matches = round_robin(p)
    t = ThreePointsTable(p, matches)
    print(t.points)
    print(t.sort_ranking())
    print(t.compute_ranks())
