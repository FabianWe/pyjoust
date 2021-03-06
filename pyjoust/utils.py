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
import functools
import re
import random
from collections import defaultdict


class JoustException(Exception):
    """The base class for all exceptions thrown by pyjoust.
    """
    pass


def toss_coin():
    """Simulates a coin toss with a 50% chance for heads / tails.

    Returns:
        True if toss result is heads and False if it is tails.
    """
    return random.randint(0, 1) == 0


def is_power_of_two(num):
    """Checks whether num is a power of two.

    Args:
        num: A positive integer.

    Returns:
        True if num is a power of two.
    """
    return ((num & (num - 1)) == 0) and num > 0


def next_power_of_two(num):
    """Returns the next power of two >= num.

    Args:
        num: A positive integer.

    Returns:
        The next power of two >= num.
    """
    val = 1
    while val < num:
        val *= 2
    return val


@functools.total_ordering
class TwoPoints(object):
    """Class representing a two points for a win entry. It consists of positive and negative points.

    Points are comparable with all rich comparison methods (such as >). We say that p1 > p2 if
    p1.plus > p2.plus or if p1.plus == p2.plus and p1.minus < p2.minus. In short: The one with the most plus points
    always wins, if they have the same number of plus points the one with the lowest number of minus points wins.

    Attributes:
        plus: The number of positive (plus) points, always a positive integer.
        minus: The number of negative (minus) points, always a positive integer.
    """

    def __init__(self, plus, minus):
        self.plus = plus
        self.minus = minus

    def __add__(self, other):
        """Adds another point and returns the result.

        Args:
            other: The point to add to this point.

        Returns:
            The new point, that is the componentwise sum of self and other.
        """
        return TwoPoints(self.plus + other.plus, self.minus + other.minus)

    def __iadd__(self, other):
        """Adds another point and returns the result.

        Args:
            other: The point to add to this point.

        Returns:
            The new point, that is the componentwise sum of self and other.
        """
        return self + other

    def __str__(self):
        return '%d:%d' % (self.plus, self.minus)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.plus == other.plus and self.minus == other.minus

    def __gt__(self, other):
        if self.plus == other.plus:
            return self.minus < other.minus
        elif self.plus > other.plus:
            return True
        else:
            return False


class MatchResult(abc.ABC):
    """An abstract base class for everything that can be used two compare a match between two teams.

    GoalScore implements this interface, it uses "goals" (like in soccer) and computes the winner. Other implementations
    can be provided for example for tennis.
    """

    @abc.abstractmethod
    def winner(self):
        """Method used to compute the winner.

        Subclasses must implement this abstract method.

        Returns:
            One of the strings 'draw' (both teams are equally successful), 'one' (team one wins) or 'two' (team two
            wins).
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def parse(str):
        pass


class GoalScore(MatchResult):
    """An implementation of MatchComparator used for games in which teams have a score (for example goals in soccer).

        Attributes:
            goals_one: An integer, the score (goals) for team one.
            goals_two: An integer, the score (goals) for team two.
        """

    rx = re.compile(r"^\s*(?P<first>\d+)\s*:\s*(?P<second>\d+)\s*$")

    def __init__(self, goals_one, goals_two):
        self.goals_one = goals_one
        self.goals_two = goals_two

    def __str__(self):
        return '%d:%d' % (self.goals_one, self.goals_two)

    def winner(self):
        """Implements the abstract winner method and returns the winner of the game.

        Returns:
            'draw' if both teams have the same number of goals, 'one' if team one has more goals and 'two' otherwise.
        """
        if self.goals_one == self.goals_two:
            return 'draw'
        elif self.goals_one > self.goals_two:
            return 'one'
        else:
            return 'two'

    @staticmethod
    def parse(s):
        """Parse a score string of the form "a:b" where a and b are ints.

        Args:
            s: The string representation.

        Returns:
            A GoalScore object with a and b.

        Raises:
            JoustException: If the syntax is invalid.
        """
        match = GoalScore.rx.match(s)
        if not match:
            raise JoustException('Must be of form "a:b", got ' + str(s))
        first, second = match.group('first'), match.group('second')
        try:
            first, second = int(first), int(second)
        except ValueError:
            raise JoustException(
                'Must be of form "a:b" with valid integers, got ' + str(s))
        return GoalScore(first, second)


class RankCriterion(abc.ABC):
    # TODO doc me

    @abc.abstractmethod
    def register_match(self, team_one, team_two, result):
        #may raise
        pass

    def keys(self, team):
        return ()

    @staticmethod
    def check_type(object, classinfo):
        if not isinstance(object, classinfo):
            raise JoustException("Can't register result: Expected instance of %s and got instance of %s" % (classinfo.__name__, type(object).__name__))


class GoalsCriterion(RankCriterion):
    def __init__(self):
        self.goal_count = defaultdict(int)

    def register_match(self, team_one, team_two, result):
        self.check_type(result, MatchResult)
        self.goal_count[team_one] += result.goals_one
        self.goal_count[team_two] += result.goals_two

    def keys(self, team):
        return -self.goal_count[team],
