

import os
import logging
import json
import argparse
from droidfiller import Agent
from pathlib import Path

logging.basicConfig(level=logging.INFO)


def traverse_view_tree(node, editable_nodes):
    for i, child in enumerate(node['children']):
        if child['editable']:
            editable_nodes.append((node, i))   # Add parent node and child index instead of the child node itself
        traverse_view_tree(child, editable_nodes)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config.json', help='Path to the config file')
    parser.add_argument('--output', '-o', type=str, default='output', help='Path to the output directory')

    args = parser.parse_args()

    if os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        raise Exception('Config file not found: {}'.format(args.config))

    state_file_path = Path(config['state_path'])
    
    if 'output_dir' in config:
        output_dir = config['output_dir']
    else:
        output_dir = args.output

    # Initialize a testing agent 
    agent = Agent(app_name=config['app_name'], tester_type=config['tester_type'], profile_name=config['profile'], llm_model=config['llm_model'], output_dir=output_dir)

    with open(state_file_path, 'r') as f:
        view_tree_json = f.read()

    editable_nodes = []
    view_tree = json.loads(view_tree_json)
    traverse_view_tree(view_tree['views'], editable_nodes)

    print(f'Editable nodes: {len(editable_nodes)}')

    generated_texts = []

    for parent, child_idx in editable_nodes:
        text = agent.get_text_input(view_tree, parent['children'][child_idx])
        if isinstance(text, list):
            generated_texts.extend(text)
        else:
            generated_texts.append(text)

        parent['children'][child_idx]['text'] = generated_texts[-1]

    print('Generated texts:', generated_texts)