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


from .tournament import GroupPhase, KOPhase, Tournament, TournamentPhase
from .group import ThreePointsTable
from .utils import next_power_of_two


class RRTournament(Tournament):
    def __init__(self, groups, table_class=ThreePointsTable):
        super().__init__()
        group_phase = GroupPhase(groups, table_class)
        self.group_phase = group_phase
        self.group_phase_key = self.add_phase(TournamentPhase(group_phase))


class RRAndKO(Tournament):
    def __init__(self, groups, table_class=ThreePointsTable):
        super().__init__()
        group_phase = GroupPhase(groups, table_class)
        self.group_phase = group_phase
        self.group_phase_key = self.add_phase(TournamentPhase(group_phase))
        self.ko_phase = None
        self.ko_phase_key = None

    # def make_ko(self):
    #     num_teams = 2 * len(self.group_phase.groups)
    #     num_ko_teams = next_power_of_two(num_teams)
    #     num_byes = num_ko_teams - num_teams
    #     common = min(num_teams, )
    #     i, j = 0, 0
    #     pass
