# region cleanse_lora_tag
def cleanse_lora_tag(lora_tag: str, separator: str):
    """
    Cleanse the lora tag by removing unnecessary parts and extracting keywords.

    Args:
        lora_tag (str): The input lora tag string.
        separator (str): The separator used in the file name.

    Returns:
        str: The cleaned-up string with extracted keywords.
    """
    safetensors_info = lora_tag[len('<lora:'):][:-1]
    
    file_name_with_weight = safetensors_info.split(':')
    
    file_name = file_name_with_weight[0]
    
    file_name_with_folder = file_name.split('\\')
    file_name = file_name_with_folder[-1]
    
    file_name_with_extension = file_name.split('.safetensors')
    file_name = file_name_with_extension[0]
    
    if separator in file_name:
        keywords = ', '.join(file_name.split(separator))
    else:
        keywords = file_name
    
    if isinstance(keywords, str):
        keyword_str = keywords
    elif isinstance(keywords, list):
        keyword_str = ', '.join(keywords[:-1]) + ', ' + keywords[-1]
    else:
        raise ValueError("keywords must be a string or a list of strings")
    
    return keyword_str
# endregion