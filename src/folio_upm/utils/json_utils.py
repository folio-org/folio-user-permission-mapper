import gzip
import io
import json


class JsonUtils:

    @staticmethod
    def read_file(file_path: str):
        with open(file_path, "r") as file:
            return json.load(file)

    @staticmethod
    def from_json(json_string: str):
        return json.loads(json_string)

    @staticmethod
    def to_json(json_object, remove_none_values: bool = False):
        _to_json_value = json_object
        if remove_none_values:
            _to_json_value = JsonUtils.delete_none(json_object)
        return json.dumps(_to_json_value)

    @staticmethod
    def to_formatted_json(json_object):
        return json.dumps(json_object, indent=2)

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
            return json.loads(gzip_file.read().decode("utf-8"))

    @staticmethod
    def to_formatted_json_file(json_object, file):
        with open(file, "w") as out_file:
            json.dump(json_object, out_file, indent=2)

    @staticmethod
    def clone_dict(_dict):
        return JsonUtils.from_json(json.dumps(_dict))

    @staticmethod
    def delete_none(_dict):
        """Delete None values recursively from all of the dictionaries, tuples, lists, sets"""
        cloned_value = JsonUtils.clone_dict(_dict)
        if isinstance(cloned_value, dict):
            for key, value in list(cloned_value.items()):
                if isinstance(value, (list, dict, tuple, set)):
                    cloned_value[key] = JsonUtils.delete_none(value)
                elif value is None or key is None:
                    del cloned_value[key]

        elif isinstance(cloned_value, (list, set, tuple)):
            cloned_value = type(cloned_value)(JsonUtils.delete_none(item) for item in cloned_value if item is not None)

        return cloned_value
