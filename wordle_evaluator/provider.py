from dataclasses import dataclass


@dataclass(frozen=True)
class Provider:
    name: str
    website: str
    score_pattern: str
