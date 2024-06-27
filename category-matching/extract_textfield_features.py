import json
import glob
import os
import re
import xmltodict
import argparse

from spiral import ronin
from regex import R
from spiral import ronin
from spiral.simple_splitters import elementary_split
from lxml import etree
from tqdm import tqdm
from load_textfield_data import load_OSS_textfields, load_samsung_textfields

import xmltodict
import xml.etree.ElementTree as ET


target_props = ['resource-id', 'content-desc', 'name', 'label', 'text', 'text_hint', 'content-desc']


def extract_tokens_from_textfields(tf, tokenization='ronin'):
    tf_tokens = []
    if 'sent_text' in tf:
        sent_text = tf['sent_text']
        if len(sent_text.strip()) > 0 and 'text' in tf and sent_text in tf['text']:
            tf['text'].replace(sent_text, ' ')

    for prop in tf:
        if prop == 'password' and tf[prop] == 'true':
            tf_tokens.append('password')

        if prop in target_props:
            if tf[prop] is None or tf[prop].lower() == 'none' or len(tf[prop].strip()) == 0:
                continue

            if prop == 'resource-id':
                tf[prop] = tf[prop].split('/')[-1]
            
            if tf[prop].strip().startswith('http://'):
                tf[prop] = 'http'

            if tf[prop].strip().startswith('https://'):
                tf[prop] = 'https'

            # TODO: try another tokenization methods
            for subtoken in ronin.split(tf[prop].strip()):
                subtoken = re.sub('[^0-9a-z]', '', subtoken.lower())
                if len(subtoken) > 0:
                    tf_tokens.append(subtoken)

    return list(set(tf_tokens))


def extract_surrounding_text(textfield_info, view_tree):
    if not isinstance(view_tree, ET.Element):
        xml = xmltodict.unparse(view_tree, pretty=True)
        view_tree = etree.fromstring(bytes(xml, encoding='utf8'))
    else:
        view_tree = etree.fromstring(ET.tostring(view_tree, encoding='utf8', method='xml'))
    
    if 'bounds' in textfield_info:
        target_elem = view_tree.findall(f".//*[@bounds='{textfield_info['bounds']}']")
        if len(target_elem) == 0:
            return []   # FIXME: bound property is not stable.. => verify with uid and types
        else:
            target_elem = target_elem[0]
    elif 'x' in textfield_info:
        target_elem = view_tree.findall(f".//*[@x='{textfield_info['x']}'][@y='{textfield_info['y']}']")
        if len(target_elem) == 0:
            return []
        else:
            target_elem = target_elem[0]

    direct_parent = target_elem.getparent()
    parent = direct_parent
    spatial_texts = []

    MAX_DEPTH=5
    for _ in range(MAX_DEPTH):
        spatial_texts.extend(extract_tokens_from_textfields(parent.attrib))
        for child in parent:
            spatial_texts.extend(extract_tokens_from_textfields(child.attrib))
            
        if len(spatial_texts) > 0:
            break
        
        parent = direct_parent.getparent()
        if parent is None:
            break
    
    return spatial_texts


def extract_all_text_in_screen(view_tree):
    if not isinstance(view_tree, ET.Element):
        xml = xmltodict.unparse(view_tree, pretty=True)
        view_tree = etree.ElementTree(etree.fromstring(bytes(xml, encoding='utf8')))

    all_tokens = []
    for e in view_tree.iter():
        all_tokens.extend(list(extract_tokens_from_textfields(e.attrib)))

    return list(set(all_tokens))



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', help='dataset (OSS or samsung)', default='OSS')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    if args.dataset == 'OSS':
        data = load_OSS_textfields()
    elif args.dataset == 'samsung':
        data = load_samsung_textfields()
    else:
        raise ValueError('Invalid dataset: ' + args.dataset)

    print(f'Loaded {len(data)} textfield contexts')

    textfield_features = {}

    for tf in tqdm(data):
        view_tree = tf['view_tree']
        tf_tokens = extract_tokens_from_textfields(tf['textfield_info'])
        local_context = extract_surrounding_text(tf['textfield_info'], view_tree)
        global_context = extract_all_text_in_screen(view_tree)

        tf_path = tf['textfield_path']
        if 'sent_text' in tf['textfield_info']:
            del tf['textfield_info']['sent_text']
    
        textfield_features[tf_path] = {
            'textfield_path': tf_path,
            'textfield_info': tf['textfield_info'],
            'app_name': tf['app_name'],
            'screenshot_path': tf['screenshot'],
            'textfield_tokens': tf_tokens,
            'local_context': local_context,
            'global_context': global_context
        }

    with open(f'data/textfield_features_{args.dataset}.json', 'w') as f:
        json.dump(textfield_features, f, indent=2)
