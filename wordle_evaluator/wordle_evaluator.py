from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Protocol, Tuple
import numpy as np

from scoreboard import Scoreboard, filter_scores_by_player, filter_scores_by_provider
from player import Player
from provider import Provider
from wordle_ui import WordleUI


@dataclass
class Rule(Protocol):
    def evaluate(self):
        ...


@dataclass
class MovingAverageRule:
    score_board: Scoreboard
    player: Player
    date: datetime | None = None
    provider: Provider | None = None
    window: int = 5

    def evaluate(self) -> Tuple[List[float], List[datetime]]:

        scores = filter_scores_by_player(
            scores=self.score_board.scores, player=self.player
        )

        if self.provider:
            scores = filter_scores_by_provider(scores=scores, provider=self.provider)

        if self.date:
            scores = [
                score for score in scores if score.date.date() <= self.date.date()
            ]

        points = [score.points for score in scores]
        days = [score.date for score in scores]
        average_points = np.convolve(
            points, np.ones(self.window) / self.window, mode="valid"
        )
        return days[-len(average_points) :], average_points.tolist()


@dataclass
class WordleEvaluator:
    title: str
    ui: WordleUI
    rules: List[Rule] = field(default_factory=list)
    to_list: bool = False

    def register_rule(self, rule: Rule) -> None:
        self.rules.append(rule)

    def show_results(self) -> None:
        data = [rule.evaluate() for rule in self.rules]
        self.ui.show(data=data, title=self.title, to_file=self.to_file)
