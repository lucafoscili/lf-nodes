import random

# region randomize_from_history
def randomize_from_history(nodes: list[dict], seed: int) -> bool:
    """
    Randomly selects a previously used boolean value from the history using a given seed.
    
    Args:
        nodes (list[dict]): List of nodes containing the history.
        seed (int): Seed to control the randomness.

    Returns:
        bool: Randomly selected boolean value.
    """
    values = list({node["value"] for node in nodes})
    if not values:
        return False

    random.seed(seed)
    return random.choice([value for value in values])
# endregion