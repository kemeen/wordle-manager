from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Player:
    name: str
    handle: str
    color: Optional[str] = None

    def __eq__(self, other):
        return self.handle == other.handle
