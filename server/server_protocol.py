import json

from gitgud_types import Json


def unpack(request: str) -> Json:
    try:
        result = json.loads(request)
    except json.JSONDecodeError:
        raise ValueError("Invalid json")

    if not isinstance(result, dict):
        raise ValueError("Value nees to be Json object")

    if "type" not in result.keys():
        raise ValueError("Every request needs type value")
    return result
