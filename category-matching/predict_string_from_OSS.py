import argparse
import glob
import os 
import json

from tqdm import tqdm

from extract_textfield_features import extract_tokens_from_textfields, extract_surrounding_text, extract_all_text_in_screen
from categories import primary_category_BoW, secondary_category_BoW, secondary_category_BoW_flattened
from utils.distutil import get_distance_btw_tokensets, get_distance_keyword_matching_baseline
from load_textfield_data import load_textfield_OSS


MAX_RANK = 5
PRUNE_COUNT = 3


def rank_categories_by_features(textfield_tokens, local_context, global_context, category_BoW=primary_category_BoW, prune=False, prune_count=3, weight_g=0.0, extend_local_ctx=True, baseline=False):
    local_ctx_tokens = textfield_tokens
    if len(local_ctx_tokens) == 0 and extend_local_ctx: # fallback to context mining
        local_ctx_tokens = local_context

    global_ctx_tokens = global_context # use global context

    categories_with_distance = []

    if baseline:
        dist_func = get_distance_keyword_matching_baseline
    else:
        dist_func = get_distance_btw_tokensets

    for category, tokenset in category_BoW.items():
        dist_l = dist_func(tokenset, local_ctx_tokens, prune=prune, prune_count=prune_count)

        dist_g = dist_func(tokenset, global_ctx_tokens, prune=prune, prune_count=prune_count)

        dist = (dist_g * weight_g) + (dist_l * (1 - weight_g))

        categories_with_distance.append((category, dist))

    return sorted(categories_with_distance, key=lambda x: x[1])


def rank_categories_JIT(tf: dict, view_tree: dict, category_BoW=primary_category_BoW, prune=False, prune_count=3, weight_g=0.0, extend_local_ctx=True):
    textfield_tokens = extract_tokens_from_textfields(tf)
    local_context = textfield_tokens
    if len(textfield_tokens) == 0 and extend_local_ctx: # fallback to context mining
        local_context = extract_surrounding_text(tf, view_tree)

    global_context = extract_all_text_in_screen(view_tree) # use global context

    return rank_categories_by_features(textfield_tokens, local_context, global_context, category_BoW=category_BoW, prune=prune, prune_count=prune_count, weight_g=weight_g, extend_local_ctx=extend_local_ctx)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--input-dir", help="Path to the input directory containing state json files", default="data/OSS")
    argparser.add_argument("-o", "--output-path", help="Path to save the result files", default="result/text_input_pred_OSS.json")
    argparser.add_argument("--predict-value", help="If set, predict textfield values instead of category", action="store_true")
    argparser.add_argument("--sample-value-file", "-f", help="Path to sample value pool dictionary", default="data/value_pool.json")
    argparser.add_argument("--max-rank", help="Top-N categories ranked to be shown", type=int, default=5)
    argparser.add_argument("--pruning-count", help="Pruning count when calculating pairwise distance", type=int, default=3)
    argparser.add_argument("--w-glob-primary", help="weight to the global context when predicting primary category", type=float, default=0.3)
    argparser.add_argument("--w-glob-secondary", help="weight to the global context when predicting secondary category", type=float, default=0.5)
    
    args = argparser.parse_args()

    MAX_RANK = args.max_rank
    PRUNE_COUNT = args.pruning_count

    result_dict = {}

    if args.predict_value:
        value_pool = json.load(open(args.sample_value_file))

    textfield_contexts_path = os.path.join(args.input_dir, 'textfield_contexts')
    screen_contexts_path = os.path.join(args.input_dir, 'snapshots')

    for dir_path in tqdm(glob.glob(os.path.join(textfield_contexts_path, '*/*'))):
        tf = load_textfield_OSS(dir_path, screen_contexts_path)
        k = tf['textfield_path']
        primary_rank_result = rank_categories_JIT(tf['textfield_info'], tf['view_tree'], category_BoW=primary_category_BoW, prune=True, prune_count=PRUNE_COUNT, weight_g=args.w_glob_primary, extend_local_ctx=True)[:MAX_RANK]

        pcat = primary_rank_result[0][0]
        concrete_category = None

        if pcat not in secondary_category_BoW:
            scat = None
            concrete_category = pcat
            secondary_rank_result = []

        else:
            secondary_rank_result = rank_categories_JIT(tf['textfield_info'], tf['view_tree'], category_BoW=secondary_category_BoW[pcat], prune=True, prune_count=PRUNE_COUNT, weight_g=args.w_glob_secondary, extend_local_ctx=True)[:MAX_RANK]
            scat = secondary_rank_result[0][0]
            concrete_category = scat

        result_dict[k] = {
            'app_name': tf['app_name'],
            'screenshot_path': tf['screenshot'],
            'best': [pcat, scat],
            'properties': tf['textfield_info'],
            'primary_categories_ranked': primary_rank_result,
            'secondary_categories_ranked': secondary_rank_result
        }

        if args.predict_value:
            assert concrete_category in value_pool

            texts = []
            if tf['app_name'] in value_pool[concrete_category]:
                texts = value_pool[concrete_category][tf['app_name']]
            else:
                texts = value_pool[concrete_category]['general']
            
            result_dict[k]['concrete_category'] = concrete_category

            result_dict[k]['predicted_inputs'] = texts

        json.dump(result_dict, open(args.output_path, 'w'), indent=4)