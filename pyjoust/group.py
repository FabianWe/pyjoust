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

from .utils import TwoPoints, JoustException


def get_group_num(group_size, num_participants, additional_group=True):
    """Returns the number of groups required.

    Args:
        group_size: The size each group should have.
        num_participants: The total number of participants (teams).
        additional_group: True if an additional group should be created for remaining teams.

    Returns:
        The number of groups required if groups should be of size group_size. If additional_group is True it is assumed
        that all remaining teams are packe into an additional group. Otherwise it is assumed that all remaning teams
        are inserted into other groups (those leading to groups of size > group_size).
    """
    res = num_participants // group_size
    if additional_group and num_participants % group_size != 0:
        res += 1
    return res


def group_sizes(group_size, num_participants, additional_group=True):
    """An iterator that yields for each group that should exist in the result the size of that group.

    This makes it easier to divide a list of participants in the groups, as done by groups_by_size and groups_by_number.
    Note that not all groups must be of the same size, especially not each group must be of size group_size.
    As an example consider 7 groups 1, 2, ..., 7. If we wish to create groups of size 2 we would get the following
    distribution (if additional group is true): [(1, 2), (3, 4), (5, 6), (7,)]. If additional_group is False
    no additional group for the remaining team is created, thus the distribution is [(1, 2, 3), (4, 5), (6, 7)].
    This iterator returns the size of those entries in the list. For the first distribution it would yield
    2, 2, 2, 1 and for the second distribution 3, 2, 2.

    Args:
        group_size: The size each group should have.
        num_participants: The total number of participants (teams).
        additional_group: True if an additional group should be created for remaining teams.

    Yields:
        For each group that should be created the number of teams in that group.
    """
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


def groups_by_size(group_size, participants, shuffle=False, additional_group=True):
    """Create a distribution of the participants into groups given the group size.

    The participants are divided into groups, the number of groups and group size depends on group_sizes which
    contains more details. participants can be a list of anything that can be used in dictionaries and compared with
    == and !=, like strings (team names) or ints (ids).

    Args:
        group_size: The size each group should have.
        participants: A list of unique team identifiers.
        shuffle: If true the participants is shuffled before distributing into groups, otherwise the order from the
            list is used. That is if the input is [1, 2, 3, 4] and groups of size 2 are created the default distribution
            is [[1, 2], [3, 4]]. If shuffle is true the order is random.
        additional_group: True if an additional group should be created for remaining teams.

    Returns:
        A list of list of identifiers. The participants are divided into groups and each list in the result describes
        such a group.
    """
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
    """Create a distribution of the participants into groups given the group size.

    participants can be a list of anything that can be used in dictionaries and compared with == and !=, like strings
    (team names) or ints (ids). It basically is a shortcut for groups_by_size with len(participants) // num_groups
    with additional_group=False.

    Args:
        num_groups: The number of groups to create.
        participants: A list of unique team identifiers.
        shuffle: If true the participants is shuffled before distributing into groups, otherwise the order from the
            list is used. That is if the input is [1, 2, 3, 4] and groups of size 2 are created the default distribution
            is [[1, 2], [3, 4]]. If shuffle is true the order is random.

    Returns:
         A list of list of identifiers. The participants are divided into groups and each list in the result describes
        such a group.
    """
    if num_groups <= 0:
        return []
    group_size = len(participants) // num_groups
    return groups_by_size(
        group_size,
        participants,
        shuffle=shuffle,
        additional_group=False)


def round_robin(group):
    """Returns an iterator over possible matches (each player plays once against each other player).

    Args:
        group: A list of unique team identifiers.

    Yields:
        Tuples of team identifiers, describing all matches if each team plays once against each other team.
    """
    return itertools.combinations(group, 2)


def toss_coin():
    """Simulates a coin toss with a 50% chance for heads / tails.

    Returns:
        True if toss result is heads and False if it is tails.
    """
    return random.randint(0, 1) == 0


class Table(object):
    """A class that connects teams to points and has methods to sort elements.

    It stores a mapping team identifier --> points. The points in the default implementation are just ints (number of
    points achieved by team). There are different ways to create such a table, and thus different subclasses exist.
    Not all subclasses store ints as points, for example it can also store TwoPoints objects.

    The easiest way to create a table is to just set the points by hand (set_points, increase_points). However often
    points are computed from different matches (for example each team plays each team). Subclasses implement this
    behavior.

    This class does not dictate subclasses on how to behave if a match is changed or added, not even how and if matches
    are stored. It only cares about points, possibly computed from certain matches. MatchTable is however a subclass
    that implements one way.

    Subclasses might want to check the following methods and overwrite them: empty_value() returns the initial points
    value, the default is the integer 0. sort_ranking that is used to sort the entries of the table and compute_ranks
    that is used to compute all ranks within the table (for example two teams sharing the first place).

    Args:
        group: A list of unique team identifiers.

    Attributes:
        points: A dictionary mapping each team identifier to a point value.
    """
    def __init__(self, group):
        super().__init__()
        self.points = dict()
        for team in group:
            self.points[team] = self.empty_value()

    def empty_value(self):
        """Returns the initial value for each team in the points mapping.

        Subclasses might want to overwrite this method if they use anything other than int for comparing entries.

        Returns:
            The integer 0.
        """
        return 0

    def set_points(self, team, points):
        """Set the points for the specified team, raising an error if the team doesn't exist.

        Args:
            team: A team identifier.
            points: The points, depending on what a specific implementation uses.

        Raises:
            JoustException: If the team doesn't exist in the points mapping.
        """
        if team not in self.points:
            raise JoustException('Invalid team name "%s"' % str(team))
        self.points[team] = points

    def increase_points(self, team, by):
        """Increase the points for the specified team by the given value.

        Args:
            team: A team identifier.
            by: Amount of points to increase points by (short: self.points[team] += by).

        Raises:
            JoustException: If the team doesn't exist in the points mapping.
        """
        if team not in self.points:
            raise JoustException('Invalid team name "%s"' % str(team))
        self.points[team] += by

    def check_exists(self, *args):
        """Check if a team / a list of teams exist(s).

        Args:
            *args: A list of team identifiers, if one of those identifiers is not found in points an exception is
                raised.

        Raises:
            JoustException: If one of the team identifiers in args is not contained in the points mapping.
        """
        for team in args:
            if team not in self.points:
                raise JoustException('Invalid team name "%s"' % str(team))

    def sort_ranking(self):
        """Sorts the ranking stored in points and returns it as a sorted list (sorted according to the entries).

        Entries are sorted according to the natural ordering (< / >) of the points values, that is for example the
        integer describing the number of achieved points.
        compute_ranks additionally divides the sorted ranking into ranks.
        A result might be: [("Team A", 42), ("Team B", 24)]

        Returns:
            A list of tuples (team_identifier, team_points) sorted according to team_points (highest points first).
        """
        ranking = []
        for team, points in self.points.items():
            ranking.append((team, points))
        ranking.sort(key=itemgetter(1, 0), reverse=True)
        return ranking

    def compute_ranks(self):
        """Sorts the ranking stored in points and divides it into ranks.

        The points dictionary is sorted according to sort_ranking and then divided into ranks. For example if
        both team A and team B have achieved 42 points they will end up in the same rank.
        Example (Team A and B achieved 42 points, Team C 24 points):
        [ (42, ["Team A", "Team B"]), (24, ["Team C"]) ]

        Returns:
            A list of tuples (points, [team1, ..., teamK]) where each entry describes all teams that achieved the
            number of points. The ranks are sorted according to points, highest first.
        """
        ranking = self.sort_ranking()
        ranks = []
        for value, r in itertools.groupby(ranking, key=itemgetter(1)):
            ranks.append((value, [ e[0] for e in r ]))
        return ranks

    def set_match_from_string(self, team_one, team_two, s):
        # TODO throw exception here or is it fine to ignore it?
        pass


def parse_score(s):
    """Parse a score string of the form "a:b" where a and b are ints.

    Args:
        s: The string representation.

    Returns:
        A tuple of ints, the parsed components.

    Raises:
        JoustException: If the syntax is invalid.
    """
    split = s.split(':')
    if len(split) != 2:
        raise JoustException('Must be of form "a:b", got ' + str(s))
    first, second = split[0], split[1]
    try:
        first, second = int(first), int(second)
    except ValueError:
        raise JoustException(
            'Must be of form "a:b" with valid integers, got ' + str(s))
    return first, second


class MatchTable(Table):
    """A table that also stores a dictionary of matches.

    MatchTable introduces three important new methods: set_match_from_string that parses a score string of the form
    "a:b" and adds the entry to the matches dictionary and then recomputes the whole ranking dictionary via the new
    compute_ranking method. This way whenever the matches dict is changed (new result, update of a result) the whole
    points are recomputed. This should be fine however. set_match does the same but without parsing the score from a
    string.

    Args:
        group: A list of unique team identifiers.

    Attributes:
        win: The amount of points awarded if a team wins.
        draw: The amount of points awarded to both teams on a draw.
        lose: The amount of points awarded to the loser team (that means it is usually a negative number or 0 when points
            are integers).
        matches: A dict mapping team pairs (matches identifiers) to tuples of int (score, for example goals).
            An entry in matches could be of the following form: matches[("Team A", "Team B")] = (42, 24) meaning
            that Team A won with 42 to 24 (goals) againsgt team B. Team A will be awarded self.win points, Team B
            self.lose points (usually a decrease or neutral element).
    """
    def __init__(self, group, matches_tuples, win, draw, lose):
        super().__init__(group)
        self.win, self.draw, self.lose = win, draw, lose
        self.matches = dict()
        for first, second in matches_tuples:
            self.matches[(first, second)] = None

    def _check_match_exists(self, *args):
        for t in args:
            if t not in self.matches:
                raise JoustException('Invalid match: "%s vs %s"' % (str(t[0]), str(t[1])))

    def compute_ranking(self):
        """Recomputes the points dictionary, called after a change to matches has been applied.

        This method actually creates a new dict and overwrites the old one.
        """
        # TODO make this more abstract? don't store pairs here but something like a score that tells us which one
        # wins?
        new_points = dict()
        for entry in self.points:
            new_points[entry] = self.empty_value()
        # set self.points to new dict so we can use increse method
        self.points = new_points
        for (team_one, team_two), entry in self.matches.items():
            if entry is None:
                continue
            first, second = entry
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

    def set_match(self, team_one, team_two, goals_one, goals_two):
        """The same as set_match_from_string but with explicit values (without parsing the score first).

        Args:
            team_one: Identifier of the first team s.t. (team_one, team_two) is a valid entry in the matches dict.
            team_two: Identifier of the second team s.t. (team_one, team_two) is a valid entry in the matches dict.
            goals_one: Number of "goals" for team one.
            goals_two: Number of "goals" for team two.

        Raises:
            JoustException: If teams are invalid.
        """
        self.check_exists(team_one, team_two)
        self._check_match_exists((team_one, team_two))
        self.matches[(team_one, team_two)] = (goals_one, goals_two)
        self.compute_ranking()

    def set_match_from_string(self, team_one, team_two, s):
        """Updates the matches dictionary with a score of the form "a:b" where a and b are ints, recomputes points.

        This method updates the matches dictionary and then uses compute_ranking to recompute the ranking.

        Args:
            team_one: Identifier of the first team s.t. (team_one, team_two) is a valid entry in the matches dict.
            team_two: Identifier of the second team s.t. (team_one, team_two) is a valid entry in the matches dict.
            s: The score string of the form "a:b".

        Raises:
            JoustException: If teams are invalid or if there is a syntax error in s.
        """
        # first check that teams are valid (before changing anything)
        first, second = parse_score(s)
        self.set_match(team_one, team_two, first, second)


class ThreePointsTable(MatchTable):
    """A class implementing a three points scheme.

    For a win 3 points are awarded to the winner and 0 to the loser. On a draw both teams receive one point.
    These values can be overwritten.
    """
    def __init__(self, group, matches_tuples, win=3, draw=1, lose=0):
        super().__init__(group, matches_tuples, win, draw, lose)


class TwoPointsTable(MatchTable):
    """A class implementing a two points scheme.

    Each entry consists of positive and negative points, so points become pairs of two ints and not two ints.
    The winner is awarded 2 plus points and 0 minus points, the loswer 0 plus points and 2 minus points. On a draw
    both teams receive one plus and one minus point. These values can be overwritten.
    """
    def __init__(self, group, matches_tuples, win=None, draw=None, lose=None):
        if win is None:
            win = TwoPoints(2, 0)
        if draw is None:
            draw = TwoPoints(1, 1)
        if lose is None:
            lose = TwoPoints(0, 2)
        super().__init__(group, matches_tuples, win, draw, lose)

    def empty_value(self):
        return TwoPoints(0, 0)
