
import os
import json
import logging

from .config import agent_config
from .model import get_next_assistant_message

MAX_RETRY = 10
LLM_MODEL = agent_config.llm_model

"""
[Additional Components]
1. Promote function call
2. Generate N candidates
"""

functions = [
    {
        "name": "get_friend_profile",
        "description": f"Get one of your friend's profile information (including properties such as {', '.join(list(agent_config.profile_dict.keys()))}) when you are asked to fill in the textfield with other's profile information",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "enum": [agent_config.available_profiles[profile_id][1]["name"] for profile_id in agent_config.available_profiles if agent_config.profile_id != profile_id]
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "get_galaxy_store_coupon_code",
        "description": "Get an available galaxy store coupon code list when you are asked to fill in the coupon code textfield for the galaxy store app",
        "parameters": {
            "type": "object",
            "properties": {
            }
        }
    },
    {
        "name": "get_samsung_product_info",
        "description": "Get the Samsung product information of the given product type when you are asked to fill in the product information textfield",
        "parameters": {
            "type": "object",
            "properties": {
                "product_type": {
                    "type": "string",
                    "enum": ["monitor", "phone", "watch"],
                }
            },
            "required": ["product_type"]
        }
    }
]

def get_friend_profile(name=None):
    target_profile = None
    for profile_id in agent_config.available_profiles:
        if agent_config.available_profiles[profile_id][1]["name"] == name:
            target_profile = agent_config.available_profiles[profile_id][1]
            break

    if target_profile is None:
        return json.dumps({
            "error": "Profile not found",
        })

    return json.dumps(target_profile)

def get_galaxy_store_coupon_code():
    return json.dumps({
        "coupon_code": ["ref-gf8ff4", "ref-3iwi87", "ref-d5nzrs"],
    })

def get_samsung_product_info(product_type=None):
    product_info = {
        "monitor": {
            "product_name": "Odyssey G7",
            "model_name": "LC27G55TQWNXZA",
            "serial_number": "C32G75TQSI"
        },
        "phone": {
            "product_name": "Galaxy S21",
            "model_name": "SM-G991UZVAXAA",
            "serial_number": "R3CT40K3FAE"
        },
        "watch": {
            "product_name": "Galaxy Watch3",
            "model_name": "SM-R840NZKAXAR",
            "serial_number": "SMW9X20Y7K3Z"
        },
    }

    if product_type not in product_info:
        return json.dumps({
            "error": "Product not found",
        })

    return json.dumps(product_info[product_type])


function_definitions = {
    "get_friend_profile": get_friend_profile,
    "get_galaxy_store_coupon_code": get_galaxy_store_coupon_code,
    "get_samsung_product_info": get_samsung_product_info,
}

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

From now on, act as if you are {agent_config.profile_dict['name']} and you will be asked to provide the text content (or intermediate reasoning steps) that {agent_config.profile_dict['name']} would likely to input to a specific textfield on the current GUI state.

Pay attention to the provided function list, and prioritise calling a relevant function if the function will provide the information related to the target textfield and the current GUI state, rather than generating the random text content. For example, you can call the function "get_friend_profile" to get one of your friend's profile information for filling in a contact information textfield rather than a random person's profile information.
'''
    initial_user_message = f'''Refer to the below information and follow the provided steps to fill in the given textfield.
    
> Target textfield to fill in:
{target_textfield}

> Widgets on the current GUI state:
{screen_state}

{previous_text_list_str}
Now, either provide the actual text content to fill in the textfield or call a relevant function if you need additional information for the current textfield, and there is a function that can provide the information. If you are going to immediately generate the text content, provide the text content with the prefix "TEXT_CONTENT:" in a single line, and do not include anything else in your answer except the text content. (e.g., "TEXT_CONTENT: Hello world!")'''.strip()

    user_messages = [initial_user_message]
    assistant_messages = []
    received_text = None
    retry = 0
    while received_text is None:
        retry += 1
        assistant_messages.append(get_next_assistant_message(system_message, user_messages, assistant_messages, model=LLM_MODEL, functions=functions))
        response = assistant_messages[-1]
        if isinstance(response, dict): # function call
            try:
                function_to_call = function_definitions[response['name']]
                function_args = json.loads(response['arguments'])
                function_response = function_to_call(**function_args)
            except Exception as e:
                print(f'Invalid function call: {response}')
                print(e)
                user_messages = [initial_user_message]
                assistant_messages = []
                continue

            user_messages.append(f'''
Here is the response from the function call:
```json
{function_response}
```

Now, provide the actual text content for the textfield. Provide the text content with the prefix "TEXT_CONTENT:" in a single line, and do not include anything else in your answer except the text content. (e.g., "TEXT_CONTENT: Hello world!")
'''.strip())

        else:
            for l in response.split('\n'):
                l = l.strip()
                if l.startswith('TEXT_CONTENT:'):
                    received_text = l.removeprefix('TEXT_CONTENT:').strip().strip('"')
                    received_text = received_text.removeprefix('TEXT_CONTENT:').strip().strip('"')
                    break

            if received_text is None:
                user_messages = [initial_user_message]
                assistant_messages = []
                continue

        if retry >= MAX_RETRY:
            print(f'Failed to get the text content after {MAX_RETRY} retries')
            return '', {
                'system_message': system_message,
                'conversation': list(zip(user_messages, assistant_messages)),
            }


    prompt = {
        'system_message': system_message,
        'conversation': list(zip(user_messages, assistant_messages)),
    }
    
    return received_text, prompt
