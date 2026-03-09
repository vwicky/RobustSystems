import json
import os
from typing import Any

def read_json(filepath: str) -> dict:
    """Reads a JSON file and returns its dictionary representation."""
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json(filepath: str, data: dict) -> None:
    """Writes a dictionary to a JSON file, creating directories if needed."""
    # Ensure the directory structure exists before writing
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)
        
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


class Cache:
    def __init__(self, var_id: str):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.filepath = os.path.join(project_root, "compute_cache", str(var_id), "cache.json")

        self.data = self._load_if_exists()

    def _load_if_exists(self) -> dict:
        """Loads the cache file if it exists, otherwise returns an empty dict."""
        if os.path.exists(self.filepath):
            try:
                return read_json(self.filepath)
            except json.JSONDecodeError:
                # Fallback if the file exists but is empty or corrupted
                return {}
        return {}

    def _update_cache(self) -> None:
        """Overwrites the JSON file with the current state of self.data."""
        write_json(self.filepath, self.data)

    def add(self, key: str, info: Any) -> bool:
        """ Adding something to cache """
        try:
            self.data[key] = info
            self._update_cache()

            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        
    def find(self, key: str) -> Any:
        """ Retrieves an item from the cache by key. """
        return self.data.get(key, None)

    def clear(self) -> bool:
        """Clears in-memory and on-disk cache for the current variant."""
        try:
            self.data = {}
            self._update_cache()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False