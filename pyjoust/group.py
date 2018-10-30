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

import random


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


def groups_by_size(group_size, participants, shuffle=False, additional_group=True):
    if group_size <= 0:
        return []
    num_participants = len(participants)
    if shuffle:
        # don't use shuffle to avoid changing the input
        participants = random.sample(participants, num_participants)
    result = []
    start = 0
    for group_size in group_sizes(group_size, num_participants, additional_group):
        next_group = participants[start:start+group_size]
        result.append(next_group)
        start += group_size
    return result

def groups_by_number(num_groups, participants, shuffle=False):
    if num_groups <= 0:
        return []
    group_size = len(participants) // num_groups
    return groups_by_size(group_size, participants, shuffle=shuffle, additional_group=False)


if __name__ == '__main__':
    p = ['Part. %d' % i for i in range(15)]
    print(p)
    print(groups_by_size(4, p, additional_group=True))
    print(groups_by_number(2, p))
