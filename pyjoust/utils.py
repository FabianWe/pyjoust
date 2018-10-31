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

@functools.total_ordering
class TwoPoints(object):
    def __init__(self, plus, minus):
        self.plus = plus
        self.minus = minus

    def __add__(self, other):
        return TwoPoints(self.plus + other.plus, self.minus + other.minus)

    def __iadd__(self, other):
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
