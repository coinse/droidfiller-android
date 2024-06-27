import os
import json

file_dir = os.path.dirname(os.path.realpath(__file__))

def load_profile(profile_file):
    with open(profile_file, 'r') as f:
        profile = f.read().strip()

    profile_dict = {}

    for l in profile.split('\n'):
        l = l.strip()
        property_name = l.split(':')[0].removeprefix('- ').strip()
        property_value = ':'.join(l.split(':')[1:]).strip()

        profile_dict[property_name] = property_value
    
    return profile, profile_dict


class LLMConfig:
    def __init__(self):
        self.app_name = None
        self.app_description = None
        self.agent_output_dir = None
        self.tester_type = None
        self.profile_id = "jade"
        self.profile = None
        self.profile_dict = {}
        self.llm_model = 'gpt-3.5-turbo-0613'

        # load all personas
        self.available_profiles = {}

        for profile_name in os.listdir(
            os.path.join(file_dir, '../../personas')
        ):
            if profile_name.endswith('.txt'):
                profile, profile_dict = load_profile(os.path.join(file_dir, '../../personas', profile_name))

                self.available_profiles[
                    profile_name.removesuffix('.txt')
                ] = (profile, profile_dict)

        self.profile = self.available_profiles[self.profile_id][0]
        self.profile_dict = self.available_profiles[self.profile_id][1]

    def set_llm_model(self, llm_model):
        if llm_model not in ['gpt-3.5-turbo-0613', 'gpt-4-0613']:
            print(
                f'LLM model {llm_model} not supported, using default LLM model {self.llm_model}'
            )
        else:
            self.llm_model = llm_model

    def set_app_name(self, app_name):
        self.app_name = app_name
        self.app_description = f'an app named {app_name}'

    def set_output_dir(self, output_dir):
        self.agent_output_dir = os.path.abspath(output_dir)
        os.makedirs(self.agent_output_dir, exist_ok=True)
        os.makedirs(
            os.path.join(self.agent_output_dir, 'text_inputs'), exist_ok=True
        )
        os.makedirs(
            os.path.join(self.agent_output_dir, 'prompts'), exist_ok=True
        )

    def set_tester(self, tester_type, profile_id):
        # load profile
        if profile_id in self.available_profiles:
            self.profile_id = profile_id
            self.profile, self.profile_dict = self.available_profiles[
                profile_id
            ]
        else:
            print(
                f'Profile {profile_id} not found, using default profile {self.profile}'
            )
            
        # load tester type
        self.load_possible_tester_types()
        if tester_type in self.tester_types:
            self.tester_type = tester_type
        else:
            self.tester_type = self.tester_types['default_tester'].strip()

    def load_possible_tester_types(self):
        with open(
            os.path.join(file_dir, '../../personas/testers.json'), 'r'
        ) as f:
            self.tester_types = json.load(f)

    def update_tester_type(self, new_tester_type):
        if new_tester_type in self.tester_types:
            self.tester_type = new_tester_type
        else:
            print(
                f'New tester type {new_tester_type} not found in possible tester types, using previous tester type {self.tester_type}'
            )

    def get_tester_description(self):
        return self.tester_types[self.tester_type]


agent_config = LLMConfig()
