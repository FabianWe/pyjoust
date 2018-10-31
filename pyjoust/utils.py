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

import functools


class JoustException(Exception):
    pass

@functools.total_ordering
class TwoPoints(object):
    """Class representing a two points for a win entry. It consists of positive and negative points.

    Attributes:
        plus (int): The number of positive (plus) points, always a positive integer.
        minus (int): The number of negative (minus) points, always a positive integer.
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

    def __eq__(self, other):
        return self.plus == other.plus and self.minus == other.minus


    def __gt__(self, other):
        if self.plus == other.plus:
            return self.minus < other.minus
        elif self.plus > other.plus:
            return True
        else:
            return False
