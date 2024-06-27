import os
import json
import logging

from .config import agent_config

all_tools = {
    "get_ampache_server_info": {
        "type": "function",
        "function": {
            "name": "get_ampache_server_info",
            "description": f"Get dogmazic server URL, username and password when you are asked to fill in the login textfield with the server information for an ampache server",
            "parameters": {
                "type": "object",
                "properties": {
                },
            }
        },
    },
    "get_nextcloud_server_info": {
        "type": "function",
        "function": {
            "name": "get_nextcloud_server_info",
            "description": f"Get nextcloud server URL, username and password when you are asked to fill in the login textfield with the server information for a nextcloud server",
            "parameters": {
                "type": "object",
                "properties": {
                },
            }
        },
    },
    "get_friend_profile": {
        "type": "function",
        "function": {
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
    },
    "get_galaxy_store_coupon_code": {
        "type": "function",
        "function": {
            "name": "get_galaxy_store_coupon_code",
            "description": "Get an available galaxy store coupon code list when you are asked to fill in the coupon code textfield for the galaxy store app",
            "parameters": {
                "type": "object",
                "properties": {
                }
            }
        },
    },
    "get_samsung_product_info": {
        "type": "function",
        "function": {
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
        },
    }
}


def get_ampache_server_info():
    return json.dumps({
        "server_URL": "play.dogmazic.net",
        "username": "anony1016mous",
        "password": "Coinse713612@",
    })

def get_nextcloud_server_info():
    return json.dumps({
        "server_URL": "https://nextcloud.greenmon.dev",
        "username": "anony1016mous",
        "password": "Coinse713612@",
    })

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
    "get_ampache_server_info": get_ampache_server_info,
    "get_nextcloud_server_info": get_nextcloud_server_info,
}