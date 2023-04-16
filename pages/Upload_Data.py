from dataclasses import dataclass
from io import StringIO
import pathlib
import pickle
import streamlit as st
import yaml

# from datetime import date
from scripts.read_scores import (
    init_scoreboard,
    players_from_config,
    providers_from_config,
)
from wordle_evaluator.whats_app_reader import TextMessageReader

# from wordle_evaluator.soccer_table import SoccerTable

from wordle_evaluator.scoreboard import Scoreboard

from wordle_evaluator.scorereader import (
    Score,
    TextScoreReader,
    filter_scores_by_date,
    filter_scores_by_player,
    get_days_played_from_scores,
    get_players_from_scores,
)

CONFIG_PATH = pathlib.Path("conf/config.yaml")
DATE_FORMAT = "%d %B, %Y"


@dataclass
class ScoreCard:
    score: Score

    def render(self):
        with st.container():
            st.markdown(f"**{self.score.provider.name}**")
            st.text(f"Game ID: {self.score.game_id}")
            st.text(f"Points: {self.score.points}")
            st.text(f"Date: {self.score.date.strftime('%Y-%m-%d')}")


def update_data(score_board: Scoreboard):
    with open("scoreboard.pickle", "wb") as f:
        pickle.dump(score_board, f)


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
            stringio = StringIO(wordle_chat_file.getvalue().decode("utf-8"))
            messages = stringio.read()

        else:
            messages = None

        # print(messages)

        if messages is None:
            st.text("No new messages uploaded")
            return

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
        all_new_scores = []
        for provider in providers:

            # create a score reader for the provider
            score_reader = TextScoreReader(
                provider=provider, message_reader=whats_app_reader
            )

            # read the scores for the provider from the messages
            score_reader.read_scores()

            # register Wordle Provider scores to the scoreboard
            new_scores = score_board.register_scores(score_reader.get_scores())

            if new_scores:
                # st.header(provider.name)
                # for score in new_scores:
                #     score_card = ScoreCard(score=score)
                #     score_card.render()
                all_new_scores.extend(new_scores)
                # st.divider()

        if all_new_scores:
            dates = sorted(list(get_days_played_from_scores(all_new_scores)))
            for date in dates:
                st.divider()
                st.header(date.strftime("%a %d %b %Y"))
                st.divider()
                date_scores = filter_scores_by_date(scores=all_new_scores, date=date)
                players = sorted(
                    list(get_players_from_scores(date_scores)), key=lambda x: x.name
                )
                for player in players:
                    with st.container():
                        st.subheader(player.name)
                        cols = st.columns(3)
                        player_scores = filter_scores_by_player(
                            scores=date_scores, player=player
                        )
                        for i, score in enumerate(player_scores):
                            with cols[i]:
                                score_card = ScoreCard(score=score)
                                score_card.render()
                        st.divider()

            st.button(
                "Update Results",
                on_click=lambda: update_data(score_board=score_board),
            )
        else:
            st.text("No new scores found in the provided data!")


if __name__ == "__main__":
    main()
