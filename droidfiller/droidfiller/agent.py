import os
import json
import time
import random
import requests
import copy
import yaml

import logging

from datetime import datetime
from collections import defaultdict

from .prompting import prompt_text_input

from .gui_state import GUIState
from .config import agent_config
from .model import stringify_prompt

os.environ['TOKENIZERS_PARALLELISM'] = 'false'

class Agent:
    def __init__(self, app_name='UnknownApp', tester_type="default_tester", profile_name="jade", tool_config_file_path='./example_tool_config.yml', output_dir='droidagent_output', llm_model='gpt-4o'):
        agent_config.set_app_name(app_name)
        agent_config.set_llm_model(llm_model)
        agent_config.set_output_dir(output_dir)
        agent_config.set_tester(tester_type, profile_name)

        self.initialize_tools(tool_config_file_path)

        self.text_input_record = {}
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.FileHandler(os.path.join(agent_config.agent_output_dir, f'agent_{time.strftime("%Y%m%d-%H%M%S")}.log'), mode='w'))

    def initialize_tools(self, tool_config_file_path):
        assert os.path.exists(tool_config_file_path), f'Tool config file {tool_config_file_path} not found'

        with open(tool_config_file_path, 'r') as f:
            tool_config = yaml.safe_load(f)

        agent_config.tools = []
        agent_config.tool_functions = {}
        for tool_name in tool_config['tools']:
            agent_config.tools.append(tool_config['tools'][tool_name]['description'])
            import json
            local_namespace = {}
            exec(tool_config['tools'][tool_name]['implementation'], globals(), local_namespace)

            agent_config.tool_functions[tool_name] = local_namespace[tool_name]
            
    def record_text_input_generations(self, state_tag):
        save_path = os.path.join(agent_config.agent_output_dir, 'text_inputs', f'text_input_{state_tag}.json')
        with open(save_path, 'w', encoding='UTF-8') as f:
            json.dump(self.text_input_record[state_tag], f, indent=2, ensure_ascii=False)
    
    def record_prompt(self, state_tag, widget_uid, prompt, state_str, widget_str):
        save_path = os.path.join(agent_config.agent_output_dir, 'prompts', f'prompt_{state_tag}_{widget_uid}_{agent_config.tester_type}.json')
        save_path_txt = os.path.join(agent_config.agent_output_dir, 'prompts', f'prompt_{state_tag}_{widget_uid}_{agent_config.tester_type}.txt')
        i = 1
        while os.path.exists(save_path):
            save_path = os.path.join(agent_config.agent_output_dir, 'prompts', f'prompt_{state_tag}_{widget_uid}_{agent_config.tester_type}_{i}.json')
            save_path_txt = os.path.join(agent_config.agent_output_dir, 'prompts', f'prompt_{state_tag}_{widget_uid}_{agent_config.tester_type}_{i}.txt')
            i += 1
        
        with open(save_path, 'w', encoding='UTF-8') as f:
            json.dump({'prompt': prompt, 'state_str': state_str, 'widget': widget_str}, f, indent=2, ensure_ascii=False)

        with open(save_path_txt, 'w', encoding='UTF-8') as f:
            f.write(stringify_prompt(prompt))
    
    def request_text_input_LLM(self, current_gui_state, widget, state_tag, num_generations=1):
        widget_str = widget.stringify() 
        state_str = current_gui_state.describe_screen_NL()
        llm_answer, prompts = prompt_text_input(state_str, widget_str, memory=None, num_generations=num_generations)
        self.logger.info(f'[LLM Answer] {llm_answer}')

        for prompt in prompts:
            self.record_prompt(state_tag, widget.uid, prompt, state_str, widget_str)

        return llm_answer

    def gen_text_input(self, view_tree, target_view, tag=None, num_generations=1, source='droidbot'):
        if source == 'droidbot':
            state_tag = view_tree.tag

        elif source == 'stem':
            if isinstance(view_tree, str):
                view_tree = json.loads(view_tree)
            else:
                view_tree = copy.deepcopy(view_tree)

            state_tag = view_tree['tag']

        if tag is not None:
            state_tag = tag

        current_gui_state = GUIState(source=source).from_view_tree(view_tree)
        
        if state_tag not in self.text_input_record:
            self.text_input_record[state_tag] = defaultdict(dict)
        
        if source == 'stem':
            target_view_uid = f"{target_view['uid']}_{target_view['bounds'][0]}_{target_view['bounds'][1]}_{target_view['bounds'][2]}_{target_view['bounds'][3]}"
        elif source == 'droidbot':
            target_view_uid = f"{target_view.get('temp_id', '')}_{str(target_view['bounds'])}"

        widget = current_gui_state.get_widget_by_uid(target_view_uid)
        if widget is None:
            self.logger.warning(f'Widget {target_view_uid} not found in GUIState')
            return 'HelloWorld' # Fallback to random string
            
        self.text_input_record[state_tag][widget.uid]['widget_description'] = str(widget)

        gen_input_list = self.request_text_input_LLM(current_gui_state, widget, state_tag, num_generations=num_generations)

        if agent_config.tester_type in self.text_input_record[state_tag][widget.uid]:
            self.text_input_record[state_tag][widget.uid][agent_config.tester_type].extend(gen_input_list)
        else:
            self.text_input_record[state_tag][widget.uid][agent_config.tester_type] = gen_input_list

        self.record_text_input_generations(state_tag)

        if len(gen_input_list) == 1:
            return gen_input_list[0]

        return gen_input_list