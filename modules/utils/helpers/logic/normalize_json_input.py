import json
import re

# region normalize_json_input
def normalize_json_input(input):
    """
    Normalize input JSON-like data into a standard Python object.
    
    This function processes inputs of various types to ensure that JSON data is
    returned in a standard format, such as a dictionary, list, or other valid JSON structure. 
    It handles the following input scenarios:
    
    - **Dictionary:** If the input is already a dictionary (parsed JSON object), it is returned as-is.
    - **String:** If the input is a JSON-formatted string, it is parsed into a JSON object (dict or list).
    - **Single-Item List:** If the input is a list with one item that is a JSON string, that item is parsed 
      into a JSON object and returned directly.
    - **List of JSON Strings:** If the input is a list of JSON-formatted strings, each string is parsed individually 
      into a JSON object, and the result is returned as a list of dictionaries.
    - **List of Dictionaries:** If the input is a list of dictionaries, it is returned as-is, assuming it is already 
      in a valid JSON format.
    
    Parameters:
    input (dict, str, or list): The JSON input to be normalized. It can be:
        - A pre-parsed JSON object (dict).
        - A JSON string.
        - A list of JSON strings or dictionaries.
    
    Returns:
    dict or list: A parsed JSON object (dictionary) or a list of parsed JSON objects.
    
    Raises:
    TypeError: If the input type is unsupported, meaning it is neither a dictionary, a string, nor a list.
    
    Examples:
    ---------
    >>> normalize_json_input('{"key": "value"}')
    {'key': 'value'}
    
    >>> normalize_json_input([ '{"key1": "value1"}', '{"key2": "value2"}' ])
    [{'key1': 'value1'}, {'key2': 'value2'}]
    
    >>> normalize_json_input([ {"key": "value"} ])
    [{'key': 'value'}]
    
    >>> normalize_json_input([{"key1": "value1"}, {"key2": "value2"}])
    [{'key1': 'value1'}, {'key2': 'value2'}]
    
    """
    def convert_python_to_json(input_str):
        """Convert single quotes in Python-style strings to JSON-compatible double quotes."""
        return re.sub(r"(?<!\")'([^']*)'(?!\")", r'"\1"', input_str)
    
    if isinstance(input, dict) or input is None:
        return input
    
    elif isinstance(input, str):
        stripped = input.strip()
        if stripped == "":
            return {}
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            try:
                return json.loads(convert_python_to_json(stripped))
            except json.JSONDecodeError:
                return {}
    
    elif isinstance(input, list):
        if all(isinstance(i, dict) for i in input):
            return input
        elif len(input) == 1 and isinstance(input[0], str):
            candidate = input[0].strip()
            if candidate == "":
                return {}
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                return json.loads(convert_python_to_json(candidate))
        else:
            normalized_list = []
            for item in input:
                if isinstance(item, str):
                    candidate = item.strip()
                    if candidate == "":
                        normalized_list.append({})
                        continue
                    try:
                        normalized_list.append(json.loads(candidate))
                    except json.JSONDecodeError:
                        try:
                            normalized_list.append(json.loads(convert_python_to_json(candidate)))
                        except json.JSONDecodeError:
                            normalized_list.append({})
                else:
                    normalized_list.append(item)
            return normalized_list
    
    else:
        raise TypeError(f"Unsupported input type: {type(input)}") 
# endregion
