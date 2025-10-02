import json
import os

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, get_usage_filename, get_usage_title, Input
from ...utils.helpers.comfy import get_comfy_dir
from ...utils.helpers.logic import normalize_json_input, normalize_list_to_value

# region LF_UpdateUsageStatistics
class LF_UpdateUsageStatistics:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "datasets_dir": (Input.STRING, {
                    "default": "Workflow_name", 
                    "tooltip": "The files are saved in the user directory of ComfyUI under LF_Nodes. This field can be used to add additional folders."
                }),
                "dataset": (Input.JSON, {
                    "tooltip": "Dataset including the resources (produced by CivitAIMetadataSetup)."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_CODE, {
                    "default": {}
                })
            },
            "hidden": { 
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_NODE = True
    RETURN_NAMES = ("dir", "dataset")
    RETURN_TYPES = (Input.STRING, Input.JSON)

    def on_exec(self, **kwargs: dict):
        def update_usage_json(resource_file: str, resource_name: str, resource_value: str):
            resource_value = os.path.splitext(resource_value)[0]
            template = {"columns": [{"id": "name", "title": resource_name}, {"id": "counter", "title": "Nr. of times used", "shape": "number"}], "nodes": []}
            if os.path.exists(resource_file):
                with open(resource_file, 'r') as file:
                    try:
                        json_data = json.load(file)
                    except json.JSONDecodeError:
                        json_data = template
            else:
                json_data = template
        
            for node in json_data["nodes"]:
                resource = node["cells"]["name"]["value"]
                if resource == resource_value:
                    counter = node["cells"]["counter"]
                    oldValue = int(counter["value"])
                    counter["value"] += 1
                    newValue = int(counter["value"])
                    break
            else:
                oldValue = 0
                newValue = 1
                new_id = len(json_data["nodes"])
                json_data["nodes"].append({
                    "cells": {
                        "name": {"value": resource_value},
                        "counter": {"value": 1}
                    },
                    "id": str(new_id)
                })
            
            os.makedirs(os.path.dirname(resource_file), exist_ok=True)
            with open(resource_file, 'w') as file:
                json.dump(json_data, file, indent=4)
            
            return f"\n**{resource_value}** count: {oldValue} => {newValue}\n"
        
        def process_list(input, type): 
            filename = get_usage_filename(type)
            file = os.path.join(actual_path, filename)
            log = get_usage_title(filename, "markdown")
            for i in input:
                log += update_usage_json(file, get_usage_title(filename), i)
            return log

        datasets_dir: str = normalize_list_to_value(kwargs.get("datasets_dir"))
        dataset: dict = normalize_json_input(kwargs.get("dataset"))
        
        actual_path = os.path.join(get_comfy_dir("base"), datasets_dir)

        log_title = "# Update summary\n"
        log = ""

        if dataset and isinstance(dataset, dict):
            if "nodes" in dataset and isinstance(dataset["nodes"], list):
                for node in dataset["nodes"]:
                    resource = node["id"]
                    resource_list = []
                    if isinstance(node, dict):
                        for child in node.get("children", []):
                            if isinstance(child, dict) and "id" in child:
                                resource_list.append(child["id"])
                    if len(resource_list) > 0:
                        log += process_list(resource_list, resource)
            else:
                print(f"Unexpected dataset structure, 'nodes' not found or not a list: {dataset}")
        else:
            print(f"Unexpected dataset format: {dataset}")

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}updateusagestatistics", {
            "node": kwargs.get("node_id"), 
            "value": log_title + log if log else log_title + "\nThere were no updates this run!"
        })

        return (actual_path, dataset)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_UpdateUsageStatistics": LF_UpdateUsageStatistics,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_UpdateUsageStatistics": "Update usage statistics",
}
# endregion