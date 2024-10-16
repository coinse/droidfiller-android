import logging
from pathlib import Path

from droidbot.device import Device
from droidbot.app import App
from droidbot.input_event import SetTextEvent

from droidfiller import Agent

import argparse
import time

POST_EVENT_WAIT = 1

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--app_name', type=str, default='Calendar')
    parser.add_argument('--profile_name', type=str, default='jade')
    parser.add_argument('--tester_type', type=str, default='default_tester')
    parser.add_argument('--llm_model', type=str, default='gpt-4o-mini')
    args = parser.parse_args()

    output_dir = Path('test_output_droidbot')

    # Get the serial of connected android device
    device = Device(device_serial='emulator-5554', output_dir=output_dir, grant_perm=True, is_emulator=args.is_emulator)
    device.set_up()
    device.connect()

    # Initialize a testing agent 
    agent = Agent(app_name=args.app_name, tester_type=args.tester_type, profile_name=args.profile_name, llm_model=args.llm_model, output_dir=output_path)

    # Get the current state of the device.
    state = device.get_current_state()
    
    # Get list of possible input events for this state and search the 'SetTextEvent' and execute it.
    possible_inputs = state.get_possible_input()
    for possible_input in possible_inputs:
        if isinstance(possible_input, SetTextEvent):
            # Update state
            state = device.get_current_state()

            possible_input.text = agent.gen_text_input(state, possible_input.view, source='droidbot')  # Set text suggested by DroidFiller
            device.send_event(possible_input)
            time.sleep(POST_EVENT_WAIT)

    device.disconnect()
    device.tear_down()
