# region handle_response
def handle_response(response: dict, method: str = "GET"):
    """
    Handles the response from a Language Model (LLM) endpoint.

    Args:
    - response (dict): The response dictionary from the LLM endpoint.
    - method (str): The HTTP method used for the request. Defaults to "GET".

    Returns:
    - tuple: A tuple containing the status code, method, and the content of the response.
    """
    if response.status_code == 400:
        return response.status_code, method, "Bad Request"
    elif response.status_code == 401:
        return response.status_code, method, "Unauthorized"
    elif response.status_code == 403:
        return response.status_code, method, "Forbidden"
    elif response.status_code == 404:
        return response.status_code, method, "Not Found"
    elif response.status_code == 500:
        return response.status_code, method, "Internal Server Error"
    else:
        if response.status_code == 200:
            llm_result = response.json()
            if 'choices' in llm_result and len(llm_result['choices']) > 0:
                first_choice = llm_result['choices'][0]
                if 'message' in first_choice and 'content' in first_choice['message']:
                    answer = first_choice['message']['content']
                    return response.status_code, method, answer
                
        return response.status_code, method, "Whoops! Something went wrong."
# endregion