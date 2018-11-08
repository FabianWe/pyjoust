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

from pyjoust.group import round_robin, TwoPointsTable
from pyjoust.ko import KOTree
from pyjoust.kubb import KubbResult
from pyjoust.utils import GoalScore

import pygubu
import tkinter as tk

# if __name__ == '__main__':
#     p = list(range(15))
#     matches = round_robin(p)
#     t = TwoPointsTable(p, matches)
#     t.set_match_from_string(0, 1, "42:24")
#     tree = KOTree(list(range(16)))
#     rows = tree.get_rows()
#     print(list(tree.get_matches(rows[0])))
#     print(GoalScore.parse("42:24"))
#
#     f = getattr(KubbResult, 'compute_ranks', None)
#     print(f)
#     print(callable(f))

class App(object):
    def __init__(self, master):
        self.builder = builder = pygubu.Builder()
        builder.add_from_file('pyjoust/wizard_welcome.ui')
        self.mainwindow = builder.get_object('team_frame', master)
        builder.connect_callbacks(self)

    def next(self, event=None):
        print(event)

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
