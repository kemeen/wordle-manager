from datetime import datetime
import pathlib

from scorereader import TextScoreReader
from scoreboard import Scoreboard
from whats_app_reader import TextMessageReader
from provider import Provider
from player import Player
from wordle_evaluator import MovingAverageRule
from soccer_table import SoccerTable

from wordle_ui import BarChartWordleUI, MatPlotLibUI, PlayerTimeHistoryPlot
import hydra

# from hydra.core.config_store import ConfigStore


@hydra.main(config_path="conf", config_name="config")
def main(cfg) -> None:

    data_path = pathlib.Path(cfg.files.data_path)
    with open(data_path, "r", encoding="utf-8") as f:
        messages = f.read()

    whats_app_reader = TextMessageReader()
    whats_app_reader.read_messages(messages)

    score_board = Scoreboard()
    providers = []
    for provider_config in cfg.providers:
        # register US Wordle Provider to scoreboard
        provider = Provider(
            name=provider_config.name,
            website=provider_config.website,
            score_pattern=provider_config.score_pattern,
        )
        providers.append(provider)
        score_reader = TextScoreReader(
            provider=provider, message_reader=whats_app_reader
        )
        score_reader.read_scores()
        # score_board.register_reader(provider=provider, reader=score_reader)
        score_board.register_scores(score_reader.get_scores())

    for player_config in cfg.players:
        player = Player(
            name=player_config.name,
            handle=player_config.handle,
            color=player_config.color,
        )
        score_board.register_players([player])

    # title = "Moving Averages for"
    # for provider in providers:
    #     data = []
    #     for player in score_board.players:
    #         rule = MovingAverageRule(
    #             score_board=score_board, player=player, provider=provider, window=10
    #         )
    #         x, y = rule.evaluate()
    #         data.append((player, x, y))
    #     sub_title = f"{title} {provider.name}"
    #     ui = PlayerTimeHistoryPlot(data=data, title=sub_title, to_file=True)
    #     ui.show()

    # score_board.update_players_from_scores()
    # for player in score_board.players:
    #     print(player)

    # today = datetime.today().date()
    # yesterday = today - timedelta(days=1)

    # todays_scores = score_board.get_player_points_of_day(date=yesterday)
    # print(todays_scores)

    # todays_winners = score_board.get_winners_of_day(day=yesterday)
    # todays_loosers = score_board.get_loosers_of_day(day=yesterday)

    # print(todays_winners)
    # print(todays_loosers)

    # wordle_ui = MatPlotLibUI(score_board=score_board)
    # wordle_ui.show_results_over_time(title="Total wins over time", to_file=True)

    # title = "wins over time"
    # for provider in providers:
    #     wordle_ui.show_results_over_time(
    #         title=f"{provider.name} {title}", provider=provider, to_file=True
    #     )

    soccer_table = SoccerTable(scoreboard=score_board)
    # month = 5
    # year = 2022
    date = datetime.now()
    month = date.month
    year = date.year
    table = soccer_table.get_table(month=month, year=year)
    with open("soccer_table.md", "w") as f:
        f.write(f"## Wordle Standings - {date.strftime('%a %b %d')}\n")
        f.write(table.to_markdown())

    # table.to_html(f"soccer_table_{month}_{year}.html")
    # with open("soccer_table.md", "w") as f:

    # wordle_ui.plot_moving_average(
    #     title="Moving Average over total wins", to_file=True, window_size=10
    # )
    # wordle_ui.plot_moving_average(
    #     title="Moving Average over Wordle wins",
    #     to_file=True,
    #     provider="wordle",
    #     window_size=10,
    # )
    # wordle_ui.plot_moving_average(
    #     title="Moving Average over Wördl wins",
    #     to_file=True,
    #     provider="wördl",
    #     window_size=10,
    # )
    # wordle_ui.plot_moving_average(
    #     title="Moving Average over 6mal5.com wins",
    #     to_file=True,
    #     provider="6mal5.com",
    #     window_size=10,
    # )
    return
    print("Todays Wordle results")
    # for player, points in sorted(todays_scores.items(), key=lambda x: x[1]):
    #     if player in todays_winners:
    #         print(f"{player.name}: {points} {WINNER_EMOJI}")
    #         continue
    #     if player in todays_loosers:
    #         print(f"{player.name}: {points} {BOOBY_EMOJI}")
    #         continue
    #     print(f"{player.name}: {points}")

    # todays_winners = score_board.get_winners_of_day(day=today)
    # for player in todays_winners:
    #     print(player)
    # print(score_board.is_day_complete(day=today))
    # print(score_board.is_day_complete(day=yesterday))

    player_wins = score_board.get_wins_per_player()
    for player, wins in player_wins.items():
        print(f"{player.name} won {wins} times")

    wordle_ui = BarChartWordleUI(score_board=score_board)
    wordle_ui.show_total_results()
    # wordle_ui.show_total_results_seaborn()
    # for score in score_board.scores[:20]:
    #     print(score)

    # for score in todays_scores:
    #     print(score)


if __name__ == "__main__":
    main()

    # date_string = '17.03.22, 07:39'
    # day = datetime.strptime(date_string, DATE_FORMAT)
    # print(day)
