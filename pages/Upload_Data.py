import pathlib
import pickle
import streamlit as st
import yaml
from datetime import date
import zipfile
from wordle_evaluator.soccer_table import SoccerTable

from wordle_evaluator.scoreboard import Scoreboard

from wordle_evaluator.scorereader import filter_scores_by_date, filter_scores_by_player

CONFIG_PATH = pathlib.Path("conf/config.yaml")
DATE_FORMAT = "%d %B, %Y"


def main() -> None:

    with CONFIG_PATH.open("r", encoding="utf8") as f:
        cfg = yaml.safe_load(f)

    with st.sidebar:
        st.header("Upload Data")
        wordle_chat_file = st.file_uploader(
            "Wordle chat data: ",
            type=["txt"],
            help="Zip file exported from wordle chat",
        )

    with st.container():
        st.title("Uploaded Chat Data")

        if wordle_chat_file:
            st.header(wordle_chat_file.read())

    # with data_path.open("r", encoding="utf-8") as f:
    #     messages = f.read()
    #     # print(messages)

    # whats_app_reader = TextMessageReader()
    # whats_app_reader.read_messages(messages=messages, dialect="apple")

    # providers = [
    #     p for p in providers_from_config(provider_configurations=cfg["providers"])
    # ]
    # players = [p for p in players_from_config(player_configurations=cfg["players"])]

    # if cfg["files"]["scoreboard_pickle"]:
    #     # print("Reading Scoreboard from pickle!")
    #     sb_pickle = pathlib.Path(cfg["files"]["scoreboard_pickle"])
    #     with sb_pickle.open("rb") as f:
    #         score_board = pickle.load(f)
    # else:
    #     score_board = init_scoreboard(players=players)

    # # add scores to scoreboard
    # for provider in providers:

    #     # create a score reader for the provider
    #     score_reader = TextScoreReader(
    #         provider=provider, message_reader=whats_app_reader
    #     )

    #     # read the scores for the provider from the messages
    #     score_reader.read_scores()

    #     # register Wordle Provider scores to the scoreboard
    #     score_board.register_scores(score_reader.get_scores())

    # # save the scoreboard to a pickle
    # with open("scoreboard.pickle", "wb") as f:
    #     pickle.dump(score_board, f)


if __name__ == "__main__":
    main()
