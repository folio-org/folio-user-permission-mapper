import gzip
import io
import json
from collections import OrderedDict


class JsonUtils:

    @staticmethod
    def from_json(json_string: str):
        return json.loads(json_string, object_pairs_hook=OrderedDict)

    @staticmethod
    def to_json(json_object):
        return json.dumps(json_object)

    @staticmethod
    def to_json_gz(json_object):
        gzip_buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=gzip_buffer, mode="w") as gzip_file:
            json_str = json.dumps(json_object)
            gzip_file.write(json_str.encode("utf-8"))

        return gzip_buffer

    @staticmethod
    def from_json_gz(response_body) -> dict:
        gzip_stream = io.BytesIO(response_body.read())
        gzip_stream.seek(0)
        with gzip.GzipFile(fileobj=gzip_stream, mode="r") as gzip_file:
            return json.loads(gzip_file.read().decode("utf-8"), object_pairs_hook=OrderedDict)

    @staticmethod
    def to_formatted_json_file(json_object, file):
        with open(file, "w") as out_file:
            json.dump(json_object, out_file, indent=2)
