from collections import defaultdict, OrderedDict
from .action import Action, initialize_possible_actions
from functools import cached_property

import json
from copy import deepcopy

class GUIState_Droidbot:
    def __init__(self):
        self.possible_actions = []
        
        self.root_widgets = []
        self.widgets = []

    def from_view_tree(self, droidbot_state):
        """
        Convert the view tree from DroidBot to a GUI state
        :param droidbot_state: DeviceState object from DroidBot
        """
        view_tree = minimize_view_tree(droidbot_state.view_tree)
        self.root_widgets = []
        self.widgets = []

        for root_elem in view_tree:
            self.root_widgets.append(traverse_widgets(root_elem, self.widgets, droidbot_state.views))

        return self

    def get_widget_by_uid(self, uid):
        """
        Get a widget by its UID
        """
        for widget in self.widgets:
            if widget.uid == uid:
                return widget

    def __str__(self):
        return self.describe_screen_NL()
        
    def describe_screen_NL(self):
        """
        natural language representation of the GUI state
        """
        widgets = sorted(self.widgets, key=lambda x: x.position)
        gui_state = 'I see the following widgets from top to bottom:\n'
        if len(widgets) == 0:
            return 'There are no widgets on this screen.'
        widget_descs = []

        for widget in widgets:
            desc = widget.stringify(include_children_text=False)
            if desc not in widget_descs:
                widget_descs.append(desc)
        
        gui_state += '\n'.join(widget_descs)
        
        return gui_state.strip()


class Widget:
    def __init__(self):
        self.view_id = None
        self.widget_type = None
        self.possible_action_types = []
        self.position = (0, 0)

    def from_dict(self, elem_dict):
        self.view_id = elem_dict.get('ID', None)
        self.widget_type = elem_dict['widget_type']
        self.possible_action_types = elem_dict.get('possible_action_types', [])
        self.children = elem_dict.get('children', [])
        self.position = elem_dict['bounds'][0]

        if 'children' in elem_dict:
            del elem_dict['children']
        
        self.elem_dict = elem_dict

        return self

    def to_dict(self, include_id=True, only_rep_property=True):
        children = [child.to_dict(include_id=include_id) for child in self.children]
        elem_dict = deepcopy(self.elem_dict)

        del elem_dict['class']
        del elem_dict['bounds']
        if not include_id and 'ID' in elem_dict:
            del elem_dict['ID']

        if only_rep_property:
            if 'text' in elem_dict:
                if 'resource_id' in elem_dict:
                    del elem_dict['resource_id']
                if 'content_description' in elem_dict:
                    del elem_dict['content_description']
            
        if 'view_str' in elem_dict:
            del elem_dict['view_str']

        if len(children) > 0:
            elem_dict['children'] = children

        return elem_dict

    @cached_property
    def bounds(self):
        return self.elem_dict['bounds']
        
    @cached_property
    def text(self):
        return self.elem_dict.get('text', None)

    @cached_property
    def resource_id(self):
        return self.elem_dict.get('resource_id', None)

    @cached_property
    def content_description(self):
        return self.elem_dict.get('content_description', None)

    @cached_property
    def all_text(self):
        texts = []
        if self.text is not None and len(self.text.strip()) > 0:
            if len(self.text) > 50:
                texts.append(self.text[:50] + '[...]')
            else:
                texts.append(self.text)

        for child in self.children:
            texts.extend(child.all_text)
        
        return texts

    @cached_property
    def state(self):
        return self.elem_dict.get('state', [])

    @cached_property
    def signature(self):
        immutable_props = ['content_description', 'resource_id']
        if 'set_text' not in self.possible_action_types:
            immutable_props.append('text')

        ingredients = []
        for prop in immutable_props:
            if prop in self.elem_dict and self.elem_dict[prop] is not None and len(self.elem_dict[prop].strip()) > 0:
                ingredients.append(self.elem_dict[prop])
        
        # also use concatenated children's signature
        ingredients.extend([child.signature for child in self.children])

        if len(ingredients) == 0:
            # non-describable widget...
            ingredients = [str(self.elem_dict['bounds'])]

        ingredients.insert(0, self.widget_type)

        return '-'.join(ingredients)

    @cached_property
    def uid(self):
        return f"{self.elem_dict.get('ID', '')}_{str(self.elem_dict['bounds'])}"

    def __repr__(self):
        return self.dump()

    def __str__(self):
        return self.stringify()

    def dump(self, indent=2):
        """
        Stringify the widget including its children
        {
            "ID": 10,
            "widget_type": "Spinner",
            "resource_id": "com.ichi2.anki:id/toolbar_spinner",
            "possible_action_types": [
                "touch",
                "long_touch",
                "scroll"
            ],
            "children": [
                {
                "widget_type": "TextView",
                "text": "My Filtered Deck",
                "resource_id": "com.ichi2.anki:id/dropdown_deck_name"
                },
                {
                "widget_type": "TextView",
                "text": "6 cards shown",
                "resource_id": "com.ichi2.anki:id/dropdown_deck_counts"
                }
            ]
        }
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def stringify(self, include_children_text=True):
        """
        natural language description of the widget
        """
        widget_type = self.widget_type
        widget_desc = ''

        if len(self.state) > 0:
            state = ', '.join(self.state)
            widget_desc = f'{state} '

        if self.elem_dict.get('is_password', False):
            widget_desc += 'password textfield'
        
        elif 'EditText' in widget_type:
            widget_desc += 'textfield'
        
        else:
            widget_desc += widget_type.split('.')[-1].lower()
        
        widget_desc = 'an ' + widget_desc if widget_desc[0] in ['a', 'e', 'i', 'o', 'u'] else 'a ' + widget_desc

        if include_children_text:
            if len(self.all_text) > 5:
                text = ', '.join(self.all_text[:5]) + f'[...and more]'
            else:
                text = ", ".join(self.all_text) if len(self.all_text) > 0 else None
        else:
            text = self.text
        content_description = self.elem_dict.get('content_description', None)
        resource_id = self.elem_dict.get('resource_id', None)

        text_desc = []
        if text is not None:
            text_desc.append(f'text "{text}"')
        elif content_description is not None:
            text_desc.append(f'content_desc "{content_description}"')
        elif resource_id is not None:
            text_desc.append(f'resource_id "{resource_id}"')

        if len(text_desc) > 0:
            text_desc = ' and '.join(text_desc)
            return f'{widget_desc} that has {text_desc}'
        
        return widget_desc



"""
Getters
"""

def __safe_dict_get(d, key, default=None):
    return d[key] if (key in d) else default


def __get_all_children(view_dict, views):
        """
        Get temp view ids of the given view's children
        :param view_dict: dict, an element of DeviceState.views
        :return: set of int, each int is a child node id
        """
        children = __safe_dict_get(view_dict, 'children')
        if not children:
            return set()
        children = set(children)
        for child in children:
            children_of_child = __get_all_children(views[child], views)
            children.union(children_of_child)
        return children


"""
Process DroidBot view tree
"""
def minimize_view_tree(view_tree):
    """
    Remove non-informative nodes from the view tree
    """
    view_tree = deepcopy(view_tree)
    
    return prune_elements(view_tree)

def prune_elements(elem):
    if is_meaningful_element(elem):
        # If the current node is interactable or has a text property, recursively prune its children
        if "children" in elem and isinstance(elem["children"], list):
            new_children = []
            for child in elem["children"]:
                new_children.extend(prune_elements(child))
            elem["children"] = new_children
        return [elem]
    else:
        # If the current node is either not interactable or doesn't have a text property, recursively prune its children and lift them
        if "children" in elem:
            lifted_children = []
            for child in elem["children"]:
                lifted_children.extend(prune_elements(child))
            return lifted_children
        return []

def is_meaningful_element(elem):
    if not elem.get('visible', False):
        return False

    if not elem.get('enabled', False):
        return False
    
    if elem.get('package') == 'com.android.documentsui': # hotfix for DocumentsUI (removed screenshot files are cached)
        file_picker_elem_text = elem.get('text')
        if file_picker_elem_text is not None:
            file_picker_elem_text = file_picker_elem_text.strip()
            if file_picker_elem_text.startswith('screen_') and file_picker_elem_text.endswith('.png'):
                elem['children'] = []
                del elem['text']
                return False

        file_picker_elem_content_desc = elem.get('content_description')
        if file_picker_elem_content_desc is not None and 'Photo taken on' in file_picker_elem_content_desc:
            elem['children'] = []
            del elem['content_description']
            return False

        if elem.get('resource_id') == 'android:id/title':
            elem['clickable'] = True
            return True

    if any(elem.get(property_name, False) for property_name in ['clickable', 'long_clickable', 'editable', 'scrollable', 'checkable']):
        return True 

    if elem.get('text') is not None and len(elem['text'].strip()) > 0:
        return True

    return False


def make_elem_map(view_list, elem_map=None):
    if elem_map is None:
        elem_map = {}
    for elem in view_list:
        elem_map[elem['temp_id']] = elem
    
    return elem_map


def substitute_child_index_to_elem(target_elem, elem_map):
    new_children = []
    new_target_elem = deepcopy(target_elem)

    for child_index in target_elem['children']:
        child_elem = substitute_child_index_to_elem(elem_map[child_index], elem_map)
        new_children.append(child_elem)
    
    new_target_elem['children'] = new_children

    return new_target_elem


def construct_view_tree_from_list(view_list, elem_map):
    root_elements = []

    # Add root elements
    for elem in view_list:
        if elem['parent'] == -1:
            root_elem = substitute_child_index_to_elem(elem, elem_map)
            root_elements.append(root_elem)

    return {
        'children': root_elements
    }


def traverse_widgets(elem, processed_widgets, original_views):
    """
    Traverse all child widgets so that all required properties are included
    """
    new_elem = OrderedDict()
    possible_action_types = []
    state_properties = []

    if elem.get('clickable', False) or elem.get('checkable', False):
        possible_action_types.append('touch')
    if elem.get('long_clickable', False):
        possible_action_types.append('long_touch')
    if elem.get('editable', False):
        possible_action_types.append('set_text')
    if elem.get('scrollable', False):
        possible_action_types.append('scroll')

    if elem.get('focused', False):
        state_properties.append('focused')
    if elem.get('checked', False):
        state_properties.append('checked')
    if elem.get('selected', False):
        state_properties.append('selected')

    if 'temp_id' in elem and len(possible_action_types) > 0:
        elem_ID = elem['temp_id']
        new_elem['ID'] = elem_ID
        new_elem['view_str'] = original_views[elem_ID]['view_str']
    if 'class' in elem:
        new_elem['widget_type'] = elem['class'].split('.')[-1]
        new_elem['class'] = elem['class']
    if 'text' in elem and elem['text'] is not None and len(elem['text'].strip()) > 0:
        new_elem['text'] = elem['text'] if len(elem['text']) < 100 else elem['text'][:100] + '[...]'
    if 'content_description' in elem and elem['content_description'] is not None:
        new_elem['content_description'] = elem['content_description']
    if 'resource_id' in elem and elem['resource_id'] is not None:
        new_elem['resource_id'] = elem['resource_id'].split('/')[-1]
    if 'is_password' in elem and elem['is_password']:
        new_elem['is_password'] = True
    if len(state_properties) > 0:
        new_elem['state'] = state_properties
    if len(possible_action_types) > 0:
        new_elem['possible_action_types'] = possible_action_types

    if 'view_str' in elem:
        new_elem['view_str'] = elem['view_str']

    new_elem['bounds'] = elem['bounds']

    children_widgets = []
    for child in elem.get('children', []):
        children_widgets.append(traverse_widgets(child, processed_widgets, original_views))
    
    new_elem['children'] = children_widgets

    widget = Widget().from_dict(new_elem)
    
    processed_widgets.append(widget)

    return widget