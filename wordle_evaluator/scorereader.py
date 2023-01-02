from dataclasses import dataclass, field
from datetime import date, datetime
from enum import unique
import re
from typing import List, Protocol, Set

from .player import Player
from .provider import Provider
from .whats_app_reader import Message, MessageReader

# ITEM_PATTERN = re.compile(r'(?P<date>\d{2}.\d{2}.\d{2}, \d{2}:\d{2}) - (?P<player_name>[\w ]+): (?P<provider_name>[\w\.]+)(?: 🇩🇪)? (?P<game_id>\d{3}) (?P<points>[\d|X|x]{1})/6')
PROVIDER_DICT = {
    "Wordle": "https://www.nytimes.com/games/wordle/index.html",
    "6mal5.com": "https://6mal5.com/",
    "Wördl": "https://wordle.at/",
}
# PROVIDER_NAMES = "|".join(PROVIDER_DICT.keys())
# SCORE_PATTERN = re.compile(
#     r"(?P<provider_name>Wordle|6mal5\.com|Wördl)(?: 🇩🇪)? +(?P<game_id>\d+) (?P<points>[\d|X|x]{1})/6"
# )
X_SCORE = 7


@dataclass(frozen=True)
class Score:
    player: Player
    points: int
    date: datetime
    provider: Provider
    game_id: int

    def __eq__(self, __o: object) -> bool:
        return all(
            [
                self.player == __o.player,
                self.points == __o.points,
                self.provider == __o.provider,
                self.game_id == __o.game_id,
            ]
        )


class ScoreReader(Protocol):
    def read_scores(self):
        ...

    def get_scores(self) -> List[Score]:
        ...


@dataclass
class TextScoreReader:
    provider: Provider
    message_reader: MessageReader
    scores: List[Score] = field(default_factory=list)

    def read_scores(self) -> None:
        for message in self.message_reader.get_messages():
            # print(message)
            score = self._convert_message_to_score(message)

            if score:
                self.scores.append(score)
        return

    def get_scores(self) -> List[Score]:
        return self.scores

    def _convert_message_to_score(self, message: Message) -> Score | None:  # type: ignore

        pattern = re.compile(self.provider.score_pattern)
        score_details = pattern.search(message.content)

        if score_details is None:
            print(
                f"NO SCORE_PATTERN in '{message}' for provider '{self.provider.name}'"
            )
            return

        # get player
        player_name = message.sender
        player = Player(name=player_name.split(" ")[0], handle=player_name)

        game_id = int(score_details.group("game_id"))

        if score_details.group("points") in ("x", "X"):
            points = X_SCORE
        else:
            points = int(score_details.group("points"))

        return Score(
            player=player,
            points=points,
            game_id=game_id,
            provider=self.provider,
            date=message.date,
        )


def filter_scores_by_player(scores: List[Score], player: Player) -> List[Score]:
    return [score for score in scores if player == score.player]


def filter_scores_by_provider(scores: List[Score], provider: Provider) -> List[Score]:
    return [score for score in scores if provider == score.provider]


def filter_scores_by_date(scores: List[Score], date: date) -> List[Score]:
    return [score for score in scores if score.date.date() == date]


def filter_scores_by_game_ids(scores: List[Score], game_ids: List[int]) -> List[Score]:
    return [score for score in scores if score.game_id in game_ids]


def get_providers_from_scores(scores: List[Score]) -> Set[Provider]:
    return set([score.provider for score in scores])


def get_players_from_scores(scores: List[Score]) -> Set[Player]:
    return set([score.player for score in scores])


def get_days_played_from_scores(scores: List[Score]) -> Set[datetime]:
    return set([score.date.date() for score in scores])
