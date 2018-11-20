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

from pyjoust.group import TwoPointsTable
from pyjoust.ko import KOTree
from pyjoust.kubb import KubbResult
from pyjoust.utils import GoalScore
from pyjoust.description import RRAndKO

if __name__ == '__main__':
    x = RRAndKO([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])
    print(x.group_phase.rounds[0])
