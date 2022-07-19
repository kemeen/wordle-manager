from datetime import datetime
import pathlib

from scorereader import TextScoreReader
from scoreboard import Scoreboard
from whats_app_reader import TextMessageReader
from provider import Provider
from player import Player

from soccer_table import SoccerTable

import hydra

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


def ord(n):
    return "th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


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

    soccer_table = SoccerTable(scoreboard=score_board)
    date = datetime.now()
    month = date.month
    year = date.year
    # table = soccer_table.get_table_by_date(month=month, year=year)
    table = soccer_table.get_table_by_game_ids(games=JULY, providers=providers)
    name = f"soccer_table_{date.strftime('%b_%Y')}.md"
    with open(name, "w") as f:
        suffix = ord(date.day)
        f.write(f"## Wordle Standings {date.strftime('%b %Y')}\n")
        f.write(f"### {date.strftime('%A, %B')} {date.day}{suffix}\n")
        f.write(table.to_markdown())

    return


if __name__ == "__main__":
    main()
