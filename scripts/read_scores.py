from datetime import datetime, date
import pathlib

from wordle_evaluator.scorereader import TextScoreReader
from wordle_evaluator.scoreboard import Scoreboard
from wordle_evaluator.whats_app_reader import MessageReader, TextMessageReader
from wordle_evaluator.provider import Provider
from wordle_evaluator.player import Player

from wordle_evaluator.soccer_table import SoccerTable

import yaml
import pickle

# from sqlalchemy import create_engine

# sqlite://<nohostname>/<path>
# where <path> is relative:
# engine = create_engine("sqlite:///foo.db")

JANUARY = {
    "wordle": range(561, 592),
    "wördl": range(561, 592),
    "6mal5.com": range(699, 730),
}
YEAR_2022 = {
    "wordle": range(196, 561),
    "wördl": range(196, 561),
    "6mal5.com": range(434, 699),
}

CONFIG_PATH = pathlib.Path("conf/config.yaml")


def ord(n):
    return "th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def providers_from_config(
    provider_configurations: list[dict[str, str]]
) -> list[Provider]:
    for provider_config in provider_configurations:
        # create the Wordle Provider
        provider = Provider(
            name=provider_config["name"],
            website=provider_config["website"],
            score_pattern=provider_config["score_pattern"],
        )
        yield provider


def players_from_config(player_configurations: list[dict[str, str]]) -> list[Player]:
    for player_config in player_configurations:

        # create player from config
        player = Player(
            name=player_config["name"],
            handle=player_config["handle"],
            color=player_config["color"],
        )
        yield player


def init_scoreboard(players: list[Player]) -> Scoreboard:
    score_board = Scoreboard()

    # register players to scoreboard
    for player in players:

        # register player to scoreboard
        score_board.register_players([player])

    return score_board


def main() -> None:

    with CONFIG_PATH.open("r", encoding="utf8") as f:
        cfg = yaml.safe_load(f)

    data_path = pathlib.Path(cfg["files"]["data_path"])
    with data_path.open("r", encoding="utf-8") as f:
        messages = f.read()
        # print(messages)

    whats_app_reader = TextMessageReader()
    whats_app_reader.read_messages(messages=messages, dialect="apple")

    providers = [
        p for p in providers_from_config(provider_configurations=cfg["providers"])
    ]
    players = [p for p in players_from_config(player_configurations=cfg["players"])]

    if cfg["files"]["scoreboard_pickle"]:
        # print("Reading Scoreboard from pickle!")
        sb_pickle = pathlib.Path(cfg["files"]["scoreboard_pickle"])
        with sb_pickle.open("rb") as f:
            score_board = pickle.load(f)
    else:
        score_board = init_scoreboard(players=players)

    # add scores to scoreboard
    for provider in providers:

        # create a score reader for the provider
        score_reader = TextScoreReader(
            provider=provider, message_reader=whats_app_reader
        )

        # read the scores for the provider from the messages
        score_reader.read_scores()

        # register Wordle Provider scores to the scoreboard
        score_board.register_scores(score_reader.get_scores())

    # save the scoreboard to a pickle
    with open("scoreboard.pickle", "wb") as f:
        pickle.dump(score_board, f)
    # return
    # soccer_table = SoccerTable(scoreboard=score_board)
    # date = datetime.now()

    # tables = [
    #     (
    #         "2022",
    #         date(2022, 12, 31),
    #         soccer_table.get_table_by_game_ids(games=YEAR_2022, providers=providers),
    #     ),
    #     (
    #         "January",
    #         date(2023, 1, 31),
    #         soccer_table.get_table_by_game_ids(games=JANUARY, providers=providers),
    #     ),
    # ]
    # for name, d, table in tables:
    #     name = f"soccer_table_{name}_{d.strftime('%b_%Y')}.md"
    #     with open(name, "w") as f:
    #         suffix = ord(d.day)
    #         f.write(f"## Wordle Standings {d.strftime('%b %Y')}\n")
    #         f.write(f"### {d.strftime('%A, %B')} {d.day}{suffix}\n")
    #         f.write(table.to_markdown())

    return


if __name__ == "__main__":
    main()
