import json
from collections import OrderedDict


def from_json(json_string: str):
    """Convert a JSON string to a Python object."""
    return json.loads(json_string, object_pairs_hook=OrderedDict)


def to_json(json_object: dict):
    """Convert a Python object to a JSON string."""
    return json.dumps(json_object)
