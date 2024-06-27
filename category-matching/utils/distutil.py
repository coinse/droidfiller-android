import os 
import json
import fasttext
import numpy as np
from scipy.spatial.distance import cosine


DISTANCE_THRESHOLD = 0.7

FASTTEXT_MODEL = fasttext.load_model('cc.en.300.bin')


def get_distance_btw_tokensets(tokens_A, tokens_B, model=FASTTEXT_MODEL, prune=True, prune_count=3):
    tokens_A = list(set(tokens_A))
    tokens_B = list(set(tokens_B))
    
    if len(tokens_A) == 0 or len(tokens_B) == 0:
        return 0
    
    dist_left_list = []
    for t_a in tokens_A:
        dists = []
        for t_b in tokens_B:
            v_a = model.get_word_vector(t_a)
            v_b = model.get_word_vector(t_b)
            
            if np.all((v_a == 0)) or np.all((v_b == 0)):
                dists.append(0)
            else:
                dists.append(cosine(v_a, v_b))
        dist_left_list.append(min(dists))
    
    if prune is True and len(dist_left_list) > prune_count:
        dist_left_list = sorted(dist_left_list)[:3]
    dist_left = sum(dist_left_list) / len(dist_left_list)
    
    dist_right_list = []
    for t_b in tokens_B:
        dists = []
        for t_a in tokens_A:
            v_a = model.get_word_vector(t_a)
            v_b = model.get_word_vector(t_b)
            
            if np.all((v_a == 0)) or np.all((v_b == 0)):
                dists.append(0)
            else:
                dists.append(cosine(v_a, v_b))
        dist_right_list.append(min(dists))
    
    if prune is True and len(dist_right_list) > prune_count:
        dist_right_list = sorted(dist_right_list)[:3]
    dist_right = sum(dist_right_list) / len(dist_right_list)
    
    return (dist_left + dist_right) / 2


def get_distance_keyword_matching_baseline(category_keywords, tokenset, prune=False, prune_count=0):
    category_keywords = set(category_keywords)
    tokenset = set(tokenset)

    if len(tokenset) == 0:
        return 1

    return 1 - (len(category_keywords.intersection(tokenset)) / len(category_keywords))
