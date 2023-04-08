import pathlib
import pickle
import streamlit as st
import yaml
from datetime import date
from wordle_evaluator.soccer_table import SoccerTable

from wordle_evaluator.scoreboard import Scoreboard

from wordle_evaluator.scorereader import filter_scores_by_date, filter_scores_by_player

CONFIG_PATH = pathlib.Path("conf/config.yaml")
DATE_FORMAT = "%d %B, %Y"


def load_score_board(file: pathlib.Path) -> Scoreboard:
    with file.open("rb") as f:
        score_board = pickle.load(f)
    return score_board


def main() -> None:

    with CONFIG_PATH.open("r", encoding="utf8") as f:
        cfg = yaml.safe_load(f)

    today = date.today()
    first = today.replace(day=1)

    sb_pickle = pathlib.Path(cfg["files"]["scoreboard_pickle"])
    score_board = load_score_board(sb_pickle)

    with st.sidebar:
        st.header("Daily Results", anchor=None, help=None)
        detail_date = st.date_input("Date", value=today)

    with st.container():
        st.title("Myrtle Wordle Team Scores")

        st.header(f"Points on {detail_date.strftime(DATE_FORMAT)}")
        st.dataframe(
            score_board.get_player_points_of_day(date=detail_date),
            use_container_width=False,
        )
        st.header("Winners of the day")
        st.text(
            "As single winner is awarded 3 points, multiple winners are awarded one points each!"
        )
        st.text(
            ", ".join(score_board.get_winners_of_day(day=detail_date, provider=None))
        )
    st.header(f"Documented Scores on {detail_date.strftime(DATE_FORMAT)}")
    players = score_board.players
    scores = filter_scores_by_date(scores=score_board.scores, date=detail_date)
    for player in players:
        st.subheader(player.name)
        player_scores = filter_scores_by_player(scores=scores, player=player)
        for score in player_scores:
            st.text(
                f"Provider: {score.provider.name}, Game ID: {score.game_id}, Points: {score.points}"
            )

    # with st.container():
    #     st.header("Results Loader")

    #     st.file_uploader(label="Raw Results")


if __name__ == "__main__":
    main()
