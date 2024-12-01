from dataclasses import dataclass
import json
from typing import Optional


@dataclass
class SimplePublish:
    message: Optional[str] = None

    def to_json(self):
        return json.dumps(self.__dict__)
