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

from pyjoust.group import round_robin, TwoPointsTable, ThreePointsTable

if __name__ == '__main__':
    p = list(range(15))
    matches = round_robin(p)
    t = TwoPointsTable(p, matches)
    t.set_match_from_string(0, 1, "42:24")
    print(t.compute_ranks())
