from datetime import datetime

# region create_history_node
def create_history_node(value: str, nodes: list[dict]):
    """
    Create a history node and append it to the list of nodes if it doesn't exist.
    If the node exists, update its description.

    Args:
        value (str): The unique identifier for the node.
        date (str): The date of execution, formatted as a string.
        nodes (list[dict]): A list of existing nodes to which the history node will be added.

    Returns:
        None
    """
    date = datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
    node = {
                "icon": "history",
                "id": value,
                "description": f"Execution date: {date}.",
                "value": value,
            }

    existing_node = next((n for n in nodes if n["id"] == value), None)
    if existing_node:
        existing_node["description"] = node["description"]
    else:
        nodes.append(node)

    return
# endregion