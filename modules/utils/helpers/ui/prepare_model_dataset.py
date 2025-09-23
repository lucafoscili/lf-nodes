import json

from ....utils.constants import BASE64_PNG_PREFIX

# region prepare_model_dataset
def prepare_model_dataset (model_name, model_hash, model_base64, model_path):
    """
    Prepare a structured dataset for a model including metadata and configurations.

    Args:
        model_name (str): The name of the model.
        model_hash (str): The hash value of the model.
        model_base64 (str): Base64 encoded representation of the model image.
        model_path (str): The file path where the model is located.

    Returns:
        dict: A dataset containing nodes with structured metadata and configurations for the model.
    """
    dataset = {
                "nodes": [
                    {
                        "cells": {
                            "text1": {
                                "value": model_name
                            },
                            "text2": {
                                "value": model_hash
                            },
                            "text3": {
                                "value": "Selected checkpoint cover, hash and name." +
                                         ("" if model_path
                                             else "Note: to set the cover, create an image with the same name of the checkpoint in its folder.")
                            },
                            "lfCode": {
                                'shape': 'code',
                                'value': json.dumps({'hash': model_hash, 'path': model_path})
                            },
                            "lfImage": {
                                "lfStyle": "img {object-fit: cover;}",
                                "shape": "image",
                                "value": BASE64_PNG_PREFIX + model_base64 if model_base64 and model_path else "broken_image"
                            }
                        },
                        "id": model_name
                    }
                ]
            }

    return dataset
# endregion