import hashlib
import os

# region get_sha256
def get_sha256(file_path: str):
    """
    Calculate or retrieve the SHA-256 hash of a file.

    If a precomputed hash file exists, this function returns that value.
    Otherwise, it computes the hash, saves it to a file, and returns the result.

    Args:
        file_path (str): The path to the file whose SHA-256 hash is needed.

    Returns:
        str: The SHA-256 hash of the file.
    """
    hash_file_path = f"{os.path.splitext(file_path)[0]}.sha256"

    # Check if hash file exists and is valid
    if os.path.exists(hash_file_path):
        try:
            with open(hash_file_path, "r") as hash_file:
                cached_hash = hash_file.read().strip()
                if cached_hash and len(cached_hash) == 64:  # Valid SHA-256 length
                    return cached_hash
        except (IOError, OSError):
            pass  # If reading fails, recalculate hash

    # Calculate hash with larger buffer for better performance
    sha256_value = hashlib.sha256()
    buffer_size = 8 * 1024 * 1024  # 8MB buffer for even better performance on large files

    try:
        with open(file_path, "rb") as file:
            while True:
                chunk = file.read(buffer_size)
                if not chunk:
                    break
                sha256_value.update(chunk)
        
        hex_hash = sha256_value.hexdigest()
        
        # Save hash to cache file
        try:
            with open(hash_file_path, "w") as hash_file:
                hash_file.write(hex_hash)
        except (IOError, OSError):
            pass  # If writing fails, just return the hash without caching
        
        return hex_hash
    except (IOError, OSError) as e:
        raise RuntimeError(f"Error calculating hash for {file_path}: {e}")
# endregion