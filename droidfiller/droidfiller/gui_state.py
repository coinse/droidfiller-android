from collections import defaultdict
from copy import deepcopy

from droidfiller.gui_state_stem import GUIState_STEM
from droidfiller.gui_state_droidbot import GUIState_Droidbot

import json

class GUIState:
    def __init__(self, source='droidbot'):
        assert source in ['droidbot', 'stem'], f"Invalid source {source} (supported: ['droidbot', 'stem'])"

        self.source = source

        if source == 'droidbot':
            self.gui_state = GUIState_Droidbot()
        elif source == 'stem':
            self.gui_state = GUIState_STEM()

    def from_view_tree(self, view_tree):
        return self.gui_state.from_view_tree(view_tree)

    def describe_screen_NL(self):
        return self.gui_state.describe_screen_NL()

    def get_widget_by_uid(self, uid):
        return self.gui_state.get_widget_by_uid(uid)

    