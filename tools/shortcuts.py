import json


def prettify(obj):
    """Prettify object"""
    return json.dumps(obj, ensure_ascii=False, indent=4)
