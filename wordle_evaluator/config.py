from dataclasses import dataclass
from typing import List

from provider import Provider


@dataclass
class Files:
    data_path: str


@dataclass
class Formats:
    date_format: str
    crown_emoji: str
    booby_emoji: str


@dataclass
class WordleEvaluatorConfig:
    files: Files
    formats: Formats
    providers: List[Provider]
