from collections import defaultdict
from .action import Action, initialize_possible_actions

import json
from copy import deepcopy

class GUIState_STEM:
    def __init__(self):
        self.possible_actions = []
        self.interactable_widgets = []
        self.non_interactable_widgets = []

    def from_view_tree(self, _view_tree):
        """
        Convert the view tree from DroidBot to a GUI state
        :param _view_tree: dict, the view tree from DroidBot
        """
        visible_widgets = get_visible_widgets(_view_tree)
        interactable_widgets = get_interactable_widgets(visible_widgets)

        for view_id in visible_widgets:
            view_dict = visible_widgets[view_id]

            if view_id in interactable_widgets:
                text_description = get_description(view_dict, visible_widgets, consider_children=True, consider_resource_id=True)
            else:
                text_description = get_description(view_dict, visible_widgets, consider_children=False, consider_resource_id=False)

            uid = f'{view_dict["uid"]}_{view_dict["bounds"][0]}_{view_dict["bounds"][1]}_{view_dict["bounds"][2]}_{view_dict["bounds"][3]}'

            if len(text_description) > 0:
                _class = view_dict['class_']
                position = ((view_dict['bounds'][1] + view_dict['bounds'][3])/2, (view_dict['bounds'][0] + view_dict['bounds'][2])/2)
                is_password = True if 'is_password' in view_dict and view_dict['is_password'] else False
                self.non_interactable_widgets.append(Widget(_class, position, text_description, view_id=view_id, is_password=is_password, uid=uid))

        return self

    def get_widget_by_uid(self, uid):
        """
        Get a widget by its UID
        """
        for widget in self.interactable_widgets:
            if widget.uid == uid:
                return widget
        
        for widget in self.non_interactable_widgets:
            if widget.uid == uid:
                return widget

    def __str__(self):
        return self.describe_screen(list_possible_actions=True)
        
    def describe_screen(self, list_possible_actions=False):
        """
        From a given GUI state, creates a description of the GUI state including the list of interactable widgets and non-interactable widgets
        """
        widgets = sorted(self.interactable_widgets + self.non_interactable_widgets, key=lambda x: x.position)
        widget_dict = {}

        for widget in widgets:
            widget_info = widget.to_dict()
            del widget_info['ID']
            if 'possible_action_types' in widget_info:
                del widget_info['possible_action_types']
            widget_dict[f'W{widget.view_id}'] = widget_info

        widget_list = json.dumps(widget_dict, indent=2, ensure_ascii=False)

        if list_possible_actions:
            state_str = f'''
Widgets (Dictionary with view IDs as keys):
{widget_list}
Possible actions:
{self.describe_possible_actions()}'''.strip()
            return state_str

        else:
            return widget_list

    def describe_screen_NL(self):
        """
        natural language representation of the GUI state
        """
        widgets = sorted(self.interactable_widgets + self.non_interactable_widgets, key=lambda x: x.position)
        gui_state = 'I see the following widgets from top to bottom:\n'
        if len(widgets) == 0:
            return 'There are no widgets on this screen.'
        widget_descs = []

        for widget in widgets:
            desc = widget.stringify(include_interactable_properties=True)
            if desc not in widget_descs:
                widget_descs.append(desc)
        
        gui_state += '\n'.join(widget_descs)
        
        if len(gui_state) > 30000:
            gui_state = gui_state[:30000] + '[...truncated due to length...]'
        return gui_state.strip()

    def describe_possible_actions(self):
        description = ''
        for i, possible_action in enumerate(self.possible_actions):
            description += f'[Action ID: {i}] {possible_action.get_possible_action_str()}\n'

        return description.strip()


class Widget:
    def __init__(self, _class, position, text_description, view_id=None, is_password=False, interactable_properties=[], uid=None):
        self._class = _class
        self.position = position
        self.widget_description = None
        self.context_description = None
        self.view_id = view_id  # only valid for the current GUI state
        self.possible_action_types = []
        self.possible_actions = []
        self.is_password = is_password
        self.interactable_properties = interactable_properties
        self.uid = uid
        
        self.load_widget_description(text_description)

    def serialize(self):
        return {
            'class': self._class,
            'position': self.position,
            'widget_description': self.widget_description,
            'view_id': self.view_id,
            'possible_action_types': self.possible_action_types,
            'is_password': self.is_password,
            'interactable_properties': self.interactable_properties,
            'uid': self.uid
        }

    def to_dict(self):
        description = {
            'ID': self.view_id,
            'widget_type': self._class,
        }

        if self.widget_description is not None:
            description['description'] = self.widget_description
        
        elif self.context_description is not None:
            description['description'] = self.context_description

        if self.is_password:
            description['is_password'] = True

        if len(self.possible_action_types) > 0:
            description['possible_action_types'] = self.possible_action_types

        return description

    def register_possible_actions(self, action_type, view_dict):
        possible_actions = initialize_possible_actions(action_type, view_dict, self)
        self.possible_action_types.append(action_type)
        self.possible_actions.extend(possible_actions)
        return possible_actions

    def load_widget_description(self, text_description):
        content_desc = []
        text = []
        resource_id = []

        if 'content_desc' in text_description:
            content_desc = list(set(text_description['content_desc']))
        if 'text' in text_description and text_description['text'] is not None and len(text_description['text']) > 0:
            text = list(set(text_description['text']))
        if 'resource_id' in text_description:
            resource_id = text_description['resource_id']
            resource_id = list(set([rid.split('/')[-1] for rid in resource_id]))
        
        if len(text) > 0 or len(content_desc) > 0 or len(resource_id) > 0:
            self.widget_description = {}

        if len(text) > 0:
            if len(text) == 1:
                text = text[0]
            self.widget_description['text'] = text

        if len(content_desc) > 0:
            if len(content_desc) == 1:
                content_desc = content_desc[0]
            self.widget_description['content_desc'] = content_desc

        if len(resource_id) > 0:
            if len(resource_id) == 1:
                resource_id = resource_id[0]
            self.widget_description['resource_id'] = resource_id

        content_desc = []
        text = []
        resource_id = []

        if 'parent' in text_description:
            parent_desc = text_description['parent']
            if 'text' in parent_desc:
                text.extend(parent_desc['text'])

        if 'siblings' in text_description:
            siblings_desc = text_description['siblings']
            if 'text' in siblings_desc:
                text.extend(siblings_desc['text'])

        if len(text) > 0:
            self.context_description = {}

            if len(text) == 1:
                text = text[0]
            self.context_description['text'] = text


    def __repr__(self):
        """
        From a given widget, creates a (detailed) description of the widget including its type, resource ID, text, and content description, and possible action types
        {
            ID: 1,
            widget_type: "TextView",
            description: {
                text: "hello world",
                content_description: "hello world",
                resource_id: "com.example.app:id/hello_world",
            }
            possible_action_types: ["touch", "scroll", "set_text"]
        }
        """
        description = self.to_dict()
        
        return json.dumps(description, indent=2)

    def __str__(self):
        return self.stringify()


    def stringify(self, include_interactable_properties=False):
        """
        natural language description of the widget
        """
        # maybe we can use LLM to summarise the widget info as well? 
        widget_type = self._class
        if include_interactable_properties and len(self.interactable_properties) > 0:
            interactability = ', '.join(self.interactable_properties)
            widget_type_repr = f'{interactability} '
        else:
            widget_type_repr = ''
        
        if 'EditText' in widget_type:
            if self.is_password:
                widget_type_repr += 'password textfield'
            else: 
                widget_type_repr += 'textfield'
        elif 'Button' in widget_type:
            widget_type_repr += 'button'
        elif 'CheckBox' in widget_type:
            widget_type_repr += 'checkbox'
        elif 'RadioButton' in widget_type:
            widget_type_repr += 'radio button'
        elif 'TextView' in widget_type:
            widget_type_repr += 'textview'
        elif 'ImageView' in widget_type:
            widget_type_repr += 'image'
        else:
            widget_type_repr += 'widget'
        
        widget_type_repr = 'an ' + widget_type_repr if widget_type_repr[0] in ['a', 'e', 'i', 'o', 'u'] else 'a ' + widget_type_repr

        text = None
        content_description = None
        resource_id = None

        if self.widget_description is not None:
            text = self.widget_description.get('text', None)
            content_description = self.widget_description.get('content_desc', None)
            resource_id = self.widget_description.get('resource_id', None)
        
        if self.context_description is not None:
            if text is None or len(text) == 0:
                text = self.context_description.get('text', None)
            if content_description is None:
                content_description = self.context_description.get('content_desc', None)
            if resource_id is None:
                resource_id = self.context_description.get('resource_id', None)

        text_desc = []
        if text is not None and len(text) > 0:
            if isinstance(text, list):
                text_truncated = []
                for t in text:
                    if len(t) > 20:
                        t = t[:20] + '...'
                    text_truncated.append(t)
                
                text = ', '.join(f'"{t}"' for t in text_truncated)
            else:
                if len(text) > 20:
                    text = text[:20] + '...'
                text = f'"{text}"'
            text_desc.append(f'text {text}')
        if content_description is not None:
            text_desc.append(f'content description "{content_description}"')
        if resource_id is not None:
            text_desc.append(f'resource_id "{resource_id}"')

        if len(text_desc) > 0:
            text_desc = ' and '.join(text_desc)
            return f'{widget_type_repr} that has {text_desc} (Widget ID: {self.view_id})'
        
        return f'{widget_type_repr} (Widget ID: {self.view_id})'


class NodeIDGenerator:
    def __init__(self):
        self.node_id = 0

    def get_next_node_id(self):
        self.node_id += 1
        return self.node_id

def traverse_view_tree(node, parent_id, node_id_generator, tempid2node):
    node_id = node_id_generator.get_next_node_id()
    node['temp_id'] = node_id
    if node['bounds'] is None:
        node['bounds'] = [0, 0, 0, 0]
    uid = f'{node["uid"]}_{node["bounds"][0]}_{node["bounds"][1]}_{node["bounds"][2]}_{node["bounds"][3]}'
    tempid2node[node_id] = node
    if parent_id is not None:
        node['parent'] = parent_id

    for child in node['children']:
        traverse_view_tree(child, node_id, node_id_generator, tempid2node)
    

def get_visible_widgets(view_tree):
    tempid2node = {}
    view_id = 0
    root = view_tree['views']
    node_id_generator = NodeIDGenerator()

    traverse_view_tree(root, None, node_id_generator, tempid2node)

    visible_widgets = {}
    for temp_id, node in tempid2node.items():
        node_id = temp_id
        children_ids = [child["temp_id"] for child in node["children"]]
        node["children"] = children_ids
        visible_widgets[node_id] = node
    
    return visible_widgets


def get_interactable_widgets(visible_widgets):
    interactable_widgets = defaultdict(list)
    for view_id, view_dict in visible_widgets.items():
        # if 'enabled' in view_dict and not view_dict['enabled']:
        #     continue
        if view_dict['clickable']:
            interactable_widgets[view_id].append('touch')
        if view_dict['scrollable_horizontal'] or view_dict['scrollable_vertical']:
            interactable_widgets[view_id].append('scroll')
        if view_dict['checkable']:
            interactable_widgets[view_id].append('touch')
        if view_dict['editable']:
            interactable_widgets[view_id].append('set_text')

    return interactable_widgets


def get_description(view_dict, visible_widgets, consider_children=True, consider_resource_id=True):
    description = defaultdict(list)

    if consider_resource_id and 'resource_id' in view_dict and view_dict['resource_id'] is not None and len(view_dict['resource_id'].strip()) > 0:
        description['resource_id'].append(view_dict['resource_id'])
    if 'text' in view_dict and view_dict['text'] is not None and len(view_dict['text']) > 0:
        description['text'].append(view_dict['text'])
    if 'content_desc' in view_dict and view_dict['content_desc'] is not None and len(view_dict['content_desc']) > 0:
        description['content_desc'].append(view_dict['content_desc'])

    if len(description) > 0:
        return description

    if consider_children:
        for child in view_dict['children']:
            if child not in visible_widgets:
                continue
            child_desc = get_description(visible_widgets[child], visible_widgets) 
            if consider_resource_id and 'resource_id' in child_desc and child_desc['resource_id'] is not None and len(child_desc['resource_id']) > 0:
                description['resource_id'].extend(child_desc['resource_id'])
            if 'text' in child_desc and child_desc['text'] is not None and len(child_desc['text']) > 0:
                description['text'].extend(child_desc['text'])
            if 'content_desc' in child_desc and child_desc['content_desc'] is not None and len(child_desc['content_desc']) > 0:
                description['content_desc'].extend(child_desc['content_desc'])

    return description


def get_description_w_context(view_dict, visible_widgets):
    description = get_description(view_dict, visible_widgets)
    visited_ids = {view_dict['temp_id']}
    if 'children' in view_dict:
        visited_ids = visited_ids.union(view_dict['children'])
    
    if 'is_password' in view_dict and view_dict['is_password']:
        description['is_password'] = True
    if 'text' in description or 'content_desc' in description:
        return description, visited_ids
    
    # get parent/sibling descriptions instead
    cur_view_dict = visible_widgets[view_dict['parent']]
    while 'parent' in cur_view_dict and cur_view_dict['parent'] > 0:
        if cur_view_dict['temp_id'] in visited_ids:
            break
        parent_desc = get_description(cur_view_dict, visible_widgets, consider_children=False)
        visited_ids.add(cur_view_dict['temp_id'])
        if 'text' in parent_desc and len(parent_desc['text']) > 0:
            if 'text' not in description:
                description['text'] = []
            description['text'].extend(parent_desc['text'])
        elif 'content_desc' in parent_desc and len(parent_desc['content_desc']) > 0:
            if 'content_desc' not in description:
                description['content_desc'] = []
            description['content_desc'].extend(parent_desc['content_desc'])

        for sibling in cur_view_dict['children']:
            if sibling == cur_view_dict['temp_id']:
                continue
            if sibling not in visible_widgets:
                continue
            desc = get_description(visible_widgets[sibling], visible_widgets, consider_children=True)
            visited_ids.add(sibling)
            if 'text' in desc and len(desc['text']) > 0:
                if 'text' not in description:
                    description['text'] = []
                description['text'].extend(parent_desc['text'])
            elif 'content_desc' in desc and len(desc['content_desc']) > 0:
                if 'content_desc' not in description:
                    description['content_desc'] = []
                description['content_desc'].extend(parent_desc['content_desc'])
        
        if len(description) > 0:
            break
        else:
            cur_view_dict = visible_widgets[cur_view_dict['parent']]
    
    return description, visited_ids


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