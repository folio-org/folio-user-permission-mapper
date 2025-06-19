import gzip
import io
import json
from collections import OrderedDict


def from_json(json_string: str):
    """Convert a JSON string to a Python object."""
    return json.loads(json_string, object_pairs_hook=OrderedDict)


def to_json(json_object):
    """Convert a Python object to a JSON string."""
    return json.dumps(json_object)


def to_gz_json(json_object):
    """Convert a Python object to a JSON string."""
    gzip_buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=gzip_buffer, mode="w") as gzip_file:
        json_str = json.dumps(json_object)
        gzip_file.write(json_str.encode("utf-8"))

    gzip_buffer.seek(0)
    return gzip_buffer


def from_gz_json(response_body) -> dict:
    gzip_stream = io.BytesIO(response_body.read())
    gzip_stream.seek(0)

    with gzip.GzipFile(fileobj=gzip_stream, mode="r") as gzip_file:
        return json.loads(gzip_file.read().decode("utf-8"), object_pairs_hook=OrderedDict)


def to_formatted_json_file(json_object, file):
    """Convert a Python object to a JSON string."""
    with open(file, "w") as out_file:
        json.dump(json_object, out_file, indent=2)
