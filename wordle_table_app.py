import pathlib
import pickle
import streamlit as st
import yaml
from datetime import date
from wordle_evaluator.soccer_table import SoccerTable

from wordle_evaluator.scoreboard import Scoreboard

CONFIG_PATH = pathlib.Path("conf/config.yaml")


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
    soccer_table = SoccerTable(scoreboard=score_board)

    with st.container():
        st.title("Wordle Results")
        st.write(
            f"Last score from { score_board.last_score().strftime('%A, %B %d, %Y')}"
        )

    with st.container():
        st.header("Date Range Selection")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start", value=first)
        with col2:
            end_date = st.date_input("End", value=today)

    with st.container():
        st.header("Table")

        st.dataframe(
            soccer_table.get_table_by_date_range(start=start_date, end=end_date)
        )

    with st.container():
        st.header("Results Loader")

        st.file_uploader(label="Raw Results")


if __name__ == "__main__":
    main()
