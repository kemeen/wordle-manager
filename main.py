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

JUNE = {
    "wordle": range(347, 377),
    "wördl": range(347, 377),
    "6mal5.com": range(485, 515),
}
JULY = {
    "wordle": range(377, 408),
    "wördl": range(377, 408),
    "6mal5.com": range(515, 546),
}
AUGUST = {
    "wordle": range(408, 439),
    "wördl": range(408, 439),
    "6mal5.com": range(546, 577),
}
SEPTEMBER = {
    "wordle": range(439, 469),
    "wördl": range(439, 469),
    "6mal5.com": range(577, 607),
}
OCTOBER = {
    "wordle": range(469, 500),
    "wördl": range(469, 500),
    "6mal5.com": range(607, 638),
}
NOVEMBER = {
    "wordle": range(500, 530),
    "wördl": range(500, 530),
    "6mal5.com": range(638, 668),
}
DECEMBER = {
    "wordle": range(530, 561),
    "wördl": range(530, 561),
    "6mal5.com": range(668, 699),
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


# @hydra.main(config_path="conf", config_name="config")
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
        print("Reading Scoreboard from pickle!")
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

    soccer_table = SoccerTable(scoreboard=score_board)
    # date = datetime.now()

    tables = [
        # (
        #     "July",
        #     date(2022, 7, 31),
        #     soccer_table.get_table_by_game_ids(games=JULY, providers=providers),
        # ),
        # (
        #     "August",
        #     date(2022, 8, 31),
        #     soccer_table.get_table_by_game_ids(games=AUGUST, providers=providers),
        # ),
        # (
        #     "September",
        #     date(2022, 9, 30),
        #     soccer_table.get_table_by_game_ids(games=SEPTEMBER, providers=providers),
        # ),
        # (
        #     "October",
        #     date(2022, 10, 31),
        #     soccer_table.get_table_by_game_ids(games=OCTOBER, providers=providers),
        # ),
        # (
        #     "November",
        #     date(2022, 11, 30),
        #     soccer_table.get_table_by_game_ids(games=NOVEMBER, providers=providers),
        # ),
        (
            "December",
            date(2022, 12, 31),
            soccer_table.get_table_by_game_ids(games=DECEMBER, providers=providers),
        ),
        (
            "2022",
            date(2022, 12, 31),
            soccer_table.get_table_by_game_ids(games=YEAR_2022, providers=providers),
        ),
    ]
    for name, d, table in tables:
        name = f"soccer_table_{name}_{d.strftime('%b_%Y')}.md"
        with open(name, "w") as f:
            suffix = ord(d.day)
            f.write(f"## Wordle Standings {d.strftime('%b %Y')}\n")
            f.write(f"### {d.strftime('%A, %B')} {d.day}{suffix}\n")
            f.write(table.to_markdown())

    return


if __name__ == "__main__":
    main()
