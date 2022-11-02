import datetime
import json
from typing import Any, Dict

"""
Subclass implementation of JSON that automatically converted created_at and timestamp fields to datetime formats
"""

# https://stackoverflow.com/a/69041655
class _JSONDecoder(json.JSONDecoder):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        ret = {}
        for key, value in obj.items():
            if key in {"created_at", "timestamp", "commence_time"}:
                ret[key] = datetime.datetime.fromisoformat(value)
            else:
                ret[key] = value
        return ret
