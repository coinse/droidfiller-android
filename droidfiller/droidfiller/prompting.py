
import os
import json

from .config import agent_config
from .model import get_next_assistant_message


MAX_RETRY = 10


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
        previous_text_list_str = f'So far, you already generated and tried the following text contents: {json.dumps(previous_text_list)}.\nDo NOT generate the duplicated text content again which is already in the aforementioned list.\n\n'
    else:
        previous_text_list_str = ''
        
    system_message = f'''{agent_config.get_tester_description()}
Currently you are testing an Android app named {agent_config.app_name}.

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
I am going to provide a template for your answer to let you think about the text content step by step. Fill out the <...> parts in the template with your own words. Preserve the formatting and overall template. Do NOT include anything else in your answer except the text to fill out the template, and do not repeat the lines of the template (e.g., do not include the line starting with "FUNCTIONALITY:" more than once in your answer).

=== Below is the template for your answer ===
FUNCTIONALITY: <briefly describe the functionality of the {agent_config.app_name} that the current GUI state is about>
TEXTFIELD_ROLE: <briefly describe the role of the target textfield>
REASONING: <briefly describe the reasoning process (1-2 sentences) to fill in the textfield. Consider following questions: What is the textfield for? In what language the textfield should be filled? Is there any function that can provide relevant information for the textfield?>'''.strip()

    action_query = f'''Now, either provide the actual text content to fill in the textfield or call a relevant function if you need additional information for the current textfield, and there is a function that can provide the information. If you are going to immediately generate the text content, provide the text content with the prefix "TEXT_CONTENT:" in a single line, and do not include anything else in your answer except the text content. (e.g., "TEXT_CONTENT: Hello world!")'''.strip()

    user_messages = [initial_user_message]
    assistant_messages = []
    assistant_messages.append(get_next_assistant_message(system_message, user_messages, assistant_messages, model=agent_config.llm_model, tools=agent_config.tools, tool_choice="none"))

    response = assistant_messages[-1]

    user_messages.append(action_query)
    received_text = None
    retry = 0
    while received_text is None:
        retry += 1
        assistant_messages.append(get_next_assistant_message(system_message, user_messages, assistant_messages, model=agent_config.llm_model, tools=agent_config.tools))
        response = assistant_messages[-1]
        if not isinstance(response, str): # function call
            try:
                function_to_call = agent_config.tool_functions[response['function']['name']]
                function_args = json.loads(response['function']['arguments'])
                function_response = function_to_call(**function_args)
                print(function_response)
            except Exception as e:
                print(f'Invalid function call: {response}')
                print(e)
                user_messages = [initial_user_message, action_query]
                assistant_messages = [assistant_messages[0]]
                continue

            user_messages.append({
                'tool_call_id': response['id'],
                'name': response['function']['name'],
                'return_value': function_response,
            })

        else:
            for l in response.split('\n'):
                l = l.strip()
                if l.startswith('TEXT_CONTENT:'):
                    received_text = l.removeprefix('TEXT_CONTENT:').strip().strip('"')
                    received_text = received_text.removeprefix('TEXT_CONTENT:').strip().strip('"')
                    break

            if received_text is None:
                user_messages = [initial_user_message, action_query]
                assistant_messages = [assistant_messages[0]]
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
