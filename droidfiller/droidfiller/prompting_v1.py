
import os
import json
import logging

from .config import agent_config
from .model import get_next_assistant_message

MAX_RETRY = 5
LLM_MODEL = agent_config.llm_model

def prompt_text_input(screen_state, target_textfield, memory=None, num_generations=1):
    previous_text_list = []
    prompts = []
    for _ in range(MAX_RETRY):
        received_text, prompt = _prompt_text_input(screen_state, target_textfield, previous_text_list)
        
        previous_text_list.append(received_text)
        prompts.append(prompt)

        if len(previous_text_list) >= num_generations:
            break
    
    return previous_text_list, prompts

def _prompt_text_input(screen_state, target_textfield, previous_text_list=[]):
    if len(previous_text_list) > 0:
        previous_text_list = list(set(previous_text_list))
        previous_text_list_str = f'So far, you already generated and tried the following text contents: {json.dumps(previous_text_list)}.\nDo NOT generate the same text content again which is in the aforementioned list.\n\n'
    else:
        previous_text_list_str = ''
        
    system_message = f'''{agent_config.get_tester_description()}
Currently you are testing an android app named {agent_config.app_name}.

Here is the profile of the persona user you are going to adopt for testing:
{agent_config.profile}

From now on, act as if you are {agent_config.profile_dict['name']} and fill in the given textfield with the text content that {agent_config.profile_dict['name']} would likely to input to a specific textfield on the current GUI state.
'''
    context_query = f'''Fill in the given textfield based on the following information.
    
> Target textfield to fill in:
{target_textfield}

> Widgets on the current GUI state:
{screen_state}

{previous_text_list_str}
Provide the text content with the prefix "TEXT_CONTENT:" in a single line, and do not include anything else in your answer except the text content. (e.g., "TEXT_CONTENT: Hello world!")'''
    assistant_messages = []
    user_messages = [context_query]

    received_text = None
    retry = 0
    while received_text is None:
        retry += 1
        assistant_messages.append(get_next_assistant_message(system_message, user_messages, assistant_messages, model=LLM_MODEL))
        response = assistant_messages[-1]
        
        for l in response.split('\n'):
            if l.startswith('TEXT_CONTENT:'):
                received_text = l.removeprefix('TEXT_CONTENT:').strip()
                break

        if received_text is None:
            user_messages = [context_query]
            assistant_messages = []
        else:
            break

        if retry >= MAX_RETRY:
            print('Failed to get a valid response from the assistant')
            exit(1)

    prompt = {
        'system_message': system_message,
        'conversation': list(zip(user_messages, assistant_messages)),
    }
    
    return received_text, prompt
