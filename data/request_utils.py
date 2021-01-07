#  Copyright (c) 2020. AV Connect Inc.
from flask import request, jsonify


def check_get_args(args_list):
    """
    Make sure all required args are in get
    :return: True, None if OK, False, missing arg
    """
    missing_args = [arg for arg in args_list if not request.args.get(arg, False)]
    if len(missing_args) > 0:
        return False, jsonify ({"missing parameters":  str(missing_args)})
    return True, None


def check_json_post_args(args_list):
    """
    Make sure all required args are keys in posted json
    :return: True, None if OK, False, missing args
    """
    missing_args = [arg for arg in args_list if not arg in request.json.keys()]
    if len(missing_args) > 0:
        return {}, jsonify ({"missing parameters":  str(missing_args)})
    return request.json, None
