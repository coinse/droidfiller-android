import logging
from pathlib import Path

from stem.app import PackageApp, ApkApp
from stem.device.adapter.adb import ADB
from stem.device.mobile import MobileDevice
from stem.input_event import SetTextEvent

from droidfiller import Agent

import argparse
import time

POST_EVENT_WAIT = 1

logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--app_name', type=str, default='Calendar')
    parser.add_argument('--profile_name', type=str, default='jade')
    parser.add_argument('--tester_type', type=str, default='default_tester')
    parser.add_argument('--llm_model', type=str, default='gpt-4o')
    args = parser.parse_args()

    # Get the serial of connected android device
    serial = ADB.get_available_devices()[0]

    output_path = Path('test_output_stem')

    # Connect to the device and install an agent for interacting with the device
    device = MobileDevice(device_serial=serial, output_dir=output_path)
    device.set_up()
    device.connect()

    # Initialize a testing agent 
    agent = Agent(app_name=args.app_name, tester_type=args.tester_type, profile_name=args.profile_name, llm_model=args.llm_model, output_dir=output_path)

    # Get the current state of the device.
    state = device.get_current_state()
    
    # Get screenshot and view_tree from the state.
    screenshot_path = state.screenshot_path
    view_tree_json = state.to_json()
    state.save2dir()    # Save state(view_tree) to file.

    # Get list of possible input events for this state and search the 'SetTextEvent' and execute it.
    possible_inputs = state.get_possible_input()
    for possible_input in possible_inputs:
        if isinstance(possible_input, SetTextEvent):
            # Update state
            state = device.get_current_state()
            screenshot_path = state.screenshot_path
            view_tree_json = state.to_json()
            state.save2dir()

            possible_input.text = agent.gen_text_input(view_tree_json, possible_input.view.to_dict())  # Set text suggested by DroidFiller
            device.dispatch_event(possible_input)
            time.sleep(POST_EVENT_WAIT)

    device.disconnect()
    device.tear_down()
