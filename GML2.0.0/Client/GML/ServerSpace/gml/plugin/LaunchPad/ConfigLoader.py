import json
import os
import os.path as p

import yaml

BOOT = "boot"
PLAN = "plan"
PROJ = "proj"
JSON = "json"
YAML = "yaml"


def load_configs(search_dirs):
    boot_name_to_obj = {}
    plan_name_to_obj = {}
    proj_name_to_obj = {}

    for search_dir in search_dirs:
        for file in os.listdir(search_dir):
            file_lower = file.lower()
            if file_lower.startswith(BOOT) and file_lower.endswith(JSON):
                with open(p.join(search_dir, file_lower), "r") as f:
                    boot_name_to_obj[p.splitext(file)[0]] = json.load(f)
            if file_lower.startswith(PLAN) and file_lower.endswith(YAML):
                with open(p.join(search_dir, file_lower), "r") as f:
                    plan_name_to_obj[p.splitext(file)[0]] = yaml.load(f, Loader=yaml.FullLoader)
            if file_lower.startswith(PROJ) and file_lower.endswith(YAML):
                with open(p.join(search_dir, file_lower), "r") as f:
                    proj_name_to_obj[p.splitext(file)[0]] = yaml.load(f, Loader=yaml.FullLoader)

    inherit_nearest_parents(boot_name_to_obj, inheritor=inheritor_dict)
    inherit_nearest_parents(plan_name_to_obj, inheritor=inheritor_list)
    inherit_nearest_parents(proj_name_to_obj, inheritor=inheritor_list)

    return boot_name_to_obj, plan_name_to_obj, proj_name_to_obj


def inherit_nearest_parents(name_to_obj_dict, inheritor):
    name_in_order = sorted(name_to_obj_dict.keys())
    for name in name_in_order:
        nearest_parent = ""
        for possible_parent in name_in_order:
            if possible_parent == name:
                break
            elif name.startswith(possible_parent):
                nearest_parent = possible_parent

        if nearest_parent:
            name_to_obj_dict[name] = inheritor(parent=name_to_obj_dict[nearest_parent], child=name_to_obj_dict[name])


def inheritor_dict(parent, child):
    result = parent.copy()
    result.update(child)
    return result


def inheritor_list(parent, child):
    result = parent[:]
    result.extend(child)
    result = list(set(result))
    return result
