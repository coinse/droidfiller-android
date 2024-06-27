import json
import glob
import os
import mmh3
import utils.datautil as datautil


def load_textfield_OSS(dir_path, snapshot_dir_prefix):
    app_name = '_'.join(dir_path.split('/')[-2].split('_')[:-1])

    _context_info = os.path.join(dir_path, 'context_info.json')
    _textfield_info = os.path.join(dir_path, 'textfield_info.json')

    with open(_textfield_info) as f:
        textfield_info = json.load(f)
    with open(_context_info) as f:
        context_info = json.load(f)

    screen_id = context_info['current_screen']

    screenshot_file = os.path.join(snapshot_dir_prefix, f'{app_name}/{screen_id}/screenshot.png')
    view_tree_file = os.path.join(snapshot_dir_prefix, f'{app_name}/{screen_id}/view_tree.json')

    with open(view_tree_file) as f:
        view_tree = json.load(f)

    return {
        'app_name': app_name,
        'textfield_path': dir_path,
        'textfield_info': textfield_info,
        'screenshot': screenshot_file,
        'view_tree': view_tree
    }


def load_textfields_from_state(state_path, screen_path):
    app_name = os.path.dirname(state_path).split('/')[-1]

    with open(state_path) as f:
        raw_state = json.load(f)
        
    view_tree = datautil.json_obj_to_xml(None, 'hierarchy', raw_state['views'])
    processed_textfields = []
    
    for tf in datautil.get_textfields(view_tree):
        tf_id = str(mmh3.hash(json.dumps(tf, sort_keys=True)))
        bounds = json.loads(tf["bounds"])
        if 'resource_id' in tf and tf['resource_id'] is not None and tf['resource_id'] != 'None':
            tf_id = tf['resource_id'].split('/')[-1]
            tf_id = f'{tf_id}_{bounds[0]}_{bounds[1]}'

        elif 'content_desc' in tf and tf['content_desc'] is not None and tf['content_desc'] != 'None':
            tf_id = tf['content_desc']
            tf_id = f'{tf_id}_{bounds[0]}_{bounds[1]}'

        processed_textfields.append({
            'app_name': app_name,
            'textfield_path': f'{state_path}:{tf_id}',
            'textfield_info': tf,
            'screenshot': screen_path,
            'view_tree': datautil.xml_to_dict(view_tree)
        })

    return processed_textfields


def load_OSS_textfields(dir_path_pattern='data/OSS/textfield_contexts/*/*'):
    print(f'Total collected textfields: {len(glob.glob("data/OSS/textfield_contexts/*/*"))}')

    data = []

    snapshot_dir_prefix = 'data/OSS/snapshots'

    for dir_path in glob.glob(dir_path_pattern):
        data.append(load_textfield_OSS(dir_path, snapshot_dir_prefix))

    return data


def load_samsung_textfields(state_path_pattern='data/samsung_internal/*/state_*.json'):
    print(f'Total collected states: {len(glob.glob("data/samsung_internal/*/state_*.json"))}')

    data = []

    for state_path in glob.glob(state_path_pattern):
        screenshot_file = state_path.replace('state', 'screen').replace('.json', '.png')
        
        data.extend(load_textfields_from_state(state_path, screenshot_file))

    return data