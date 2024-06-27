import os
import json
import time
import random
import requests
import guidance
import copy

import logging

from datetime import datetime
from collections import defaultdict

from .prompting_v4 import prompt_text_input as prompt_text_input_v4, initialize_tools
from .prompting_v3 import prompt_text_input as prompt_text_input_v3
from .prompting_v2 import prompt_text_input as prompt_text_input_v2

from .gui_state import GUIState
from .action import Action
from .config import agent_config
from .model import stringify_prompt

os.environ['TOKENIZERS_PARALLELISM'] = 'false'

class Agent:
    def __init__(self, app_name='UnknownApp', tester_type="default_tester", profile_name="jade", output_dir='droidagent_output', llm_model='gpt-3.5-turbo-0613'):
        agent_config.set_app_name(app_name)
        agent_config.set_llm_model(llm_model)
        agent_config.set_output_dir(output_dir)
        agent_config.set_tester(tester_type, profile_name)

        initialize_tools()

        self.text_input_record = {}
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.FileHandler(os.path.join(agent_config.agent_output_dir, f'agent_{time.strftime("%Y%m%d-%H%M%S")}.log'), mode='w'))        
    
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
    
    def request_text_input_LLM(self, current_gui_state, widget, state_tag, num_generations=1, prompt_version=4):
        if prompt_version == 4:
            prompt_text_input = prompt_text_input_v4
        elif prompt_version == 3:
            prompt_text_input = prompt_text_input_v3
        elif prompt_version == 2:
            prompt_text_input = prompt_text_input_v2
        else:
            raise Exception(f'Unknown prompt version (should be 2-4): {prompt_version}')

        widget_str = widget.stringify()
        state_str = current_gui_state.describe_screen_NL()
        llm_answer, prompts = prompt_text_input(state_str, widget_str, memory=None, num_generations=num_generations)
        self.logger.debug(f'[LLM Answer] {llm_answer}')

        for prompt in prompts:
            self.record_prompt(state_tag, widget.uid, prompt, state_str, widget_str)

        return llm_answer

    def get_text_input(self, view_tree, target_view, generate_all_tester_types=False, tag=None, num_generations=1, prompt_version=4):
        if isinstance(view_tree, str):
            view_tree = json.loads(view_tree)

        view_tree = copy.deepcopy(view_tree)

        if tag is not None:
            state_tag = tag
        else:
            state_tag = view_tree['tag']

        current_gui_state = GUIState().from_droidbot_state(view_tree)
        if state_tag not in self.text_input_record:
            self.text_input_record[state_tag] = defaultdict(dict)
        
        target_view_uid = f"{target_view['uid']}_{target_view['bounds'][0]}_{target_view['bounds'][1]}_{target_view['bounds'][2]}_{target_view['bounds'][3]}"

        widget = current_gui_state.get_widget_by_uid(target_view_uid)
        if widget is None:
            self.logger.warning(f'Widget {target_view_uid} not found in GUIState')
            return 'HelloWorld'
            # Fallback to random string
            
        self.text_input_record[state_tag][widget.uid]['widget_description'] = str(widget)

        original_tester_type = agent_config.tester_type
        effective_test_inputs = None
        
        if generate_all_tester_types:
            for tester_type in agent_config.tester_types:        
                agent_config.update_tester_type(tester_type)
                generated_text_inputs = self.request_text_input_LLM(current_gui_state, widget, state_tag, num_generations=num_generations, prompt_version=prompt_version)
                if tester_type == original_tester_type:
                    effective_test_inputs = generated_text_inputs

                if tester_type in self.text_input_record[state_tag][widget.uid]:
                    self.text_input_record[state_tag][widget.uid][tester_type].extend(generated_text_inputs)
                else:
                    self.text_input_record[state_tag][widget.uid][tester_type] = generated_text_inputs
            
            agent_config.tester_type = original_tester_type
        
        else:
            effective_test_inputs = self.request_text_input_LLM(current_gui_state, widget, state_tag, num_generations=num_generations, prompt_version=prompt_version)

            if agent_config.tester_type in self.text_input_record[state_tag][widget.uid]:
                self.text_input_record[state_tag][widget.uid][agent_config.tester_type].extend(effective_test_inputs)
            else:
                self.text_input_record[state_tag][widget.uid][agent_config.tester_type] = effective_test_inputs

        self.record_text_input_generations(state_tag)

        if len(effective_test_inputs) == 1:
            return effective_test_inputs[0]

        return effective_test_inputs