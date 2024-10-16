from .util import __safe_dict_get, __get_all_children
from collections import defaultdict
import json

class Action:
    def __init__(self, source=None):
        self.source = source
        self.memory_id = None
        self.intent = None
        self.expected_change = None

        self.event_type = None
        self.target_widget = None
        self.text = None    # for set_text event
        self.direction = None  # for scroll event
        self.name = None    # for key event

    def from_props(self, event_type, text=None, direction=None, name=None, target_widget=None):
        self.event_type = event_type
        self.target_widget = target_widget
        if event_type == 'set_text' and text is not None:
            self.text = text
        if direction is not None:
            self.direction = direction.lower()
        if name is not None:
            self.name = name

        return self

    def to_dict(self):
        return {
            'event_type': self.event_type,
            'target_widget': str(self.target_widget) if self.target_widget is not None else None,
            'text': self.text,
            'direction': self.direction
        }

    def get_action_type(self):
        if self.event_type == 'scroll':
            return f'{self.event_type} {self.direction}'
        else:
            return self.event_type

    def set_source(self, source):
        self.source = source

    def set_memory_id(self, memory_id):
        self.memory_id = str(memory_id)

    def register_droidbot_event(self, event):
        self.droidbot_event = event

    def update_event_type(self, event_type):
        self.event_type = event_type

    def update_input_text(self, input_text):
        assert self.event_type == 'set_text', 'Cannot update input text for non-SetText event'
        self.text = input_text
        self.droidbot_event.text = input_text

    def add_context(self, intent, expected_change):
        self.intent = intent
        self.expected_change = expected_change

    def get_action_record_str(self):
        action_str = ''
        if self.event_type == 'start_app':
            action_str = f'I started the app'
        if self.event_type == 'stop_app':
            action_str = f'I stopped the app'

        if self.event_type == 'key' and self.name == 'BACK':
            action_str = f'I pressed the "BACK" key on my screen'
        if self.event_type in ['set_text', 'scroll', 'touch', 'long_touch']:
            if self.target_widget is not None:
                widget_info = str(self.target_widget)
            else:
                widget_info = 'the screen'
            if self.event_type == 'set_text':
                action_str = f'I sent the text "{self.text}" to {widget_info}'
            elif self.event_type == 'scroll':
                action_str = f'I scrolled {self.direction.lower()} on {widget_info}'
            elif self.event_type == 'touch':
                action_str = f'I touched on {widget_info}'

        return action_str

    def get_action_str(self):
        action_str = ''
        if self.event_type == 'start_app':
            action_str = f'Start app'
        if self.event_type == 'stop_app':
            action_str = f'Stop app'

        if self.event_type == 'key' and self.name == 'BACK':
            action_str = f'Press "BACK" key to go back'
        if self.event_type in ['set_text', 'scroll', 'touch', 'long_touch']:
            if self.target_widget is not None:
                widget_info = str(self.target_widget)
            else:
                widget_info = 'the screen'
            if self.event_type == 'set_text':
                action_str = f'Send text "{self.text}" to {widget_info}'
            elif self.event_type == 'scroll':
                action_str = f'Scroll {self.direction.lower()} on {widget_info}'
            elif self.event_type == 'touch':
                action_str = f'Touch on {widget_info}'

        return action_str

    def get_possible_action_str(self):
        action_str = ''
        
        if self.event_type == 'key' and self.name == 'BACK':
            action_str = f'You can go back to the previous screen by pressing the "BACK" key'
        if self.event_type == 'scroll':
            if self.target_widget is None:
                action_str = f'You can scroll on the screen'
            else:
                action_str = f'You can scroll on {self.target_widget} (Widget ID: W{self.target_widget.view_id})'
        if self.event_type == 'set_text':
            action_str = f'You can send text to {self.target_widget} (Widget ID: W{self.target_widget.view_id})'
        if self.event_type == 'touch':
            action_str = f'You can touch on {self.target_widget} (Widget ID: W{self.target_widget.view_id})'
        
        return action_str

    def __str__(self):
        return self.get_action_str()


def initialize_possible_actions(action_type, view_dict, target_widget):
    if action_type == 'touch':
        return [Action().from_props('touch', target_widget=target_widget)]
    elif action_type == 'scroll':
        possible_actions = []
        possible_actions.append(Action().from_props('scroll', direction="UP", target_widget=target_widget))
        possible_actions.append(Action().from_props('scroll', direction="DOWN",  target_widget=target_widget))
        possible_actions.append(Action().from_props('scroll', direction="LEFT", target_widget=target_widget))
        possible_actions.append(Action().from_props('scroll', direction="RIGHT", target_widget=target_widget))
        return possible_actions
    elif action_type == 'set_text':
        return [Action().from_props('set_text', text="test", target_widget=target_widget)]

def initialize_screen_scroll_action():
    return Action().from_props('scroll', direction="UP")

def initialize_go_back_action():
    return Action().from_props('key', name="BACK")