from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import List, Protocol

RE_EMOJI = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)
MESSAGE_PATTERN = re.compile(
    r"(\d{2}\.\d{2}\.\d{2}), (\d{2}:\d{2}) ([^:]+): (.*?)(?=\[\d{2}\.\d{2}\.\d{2}, \d{2}:\d{2}])"
)
# SCORE_PATTERN = re.compile(r'(?P<date>\d{2}.\d{2}.\d{2}, \d{2}:\d{2}) - (?P<player_name>[\w ]+): (?:[\U00010000-\U0010ffff\w .\n]*)?(?P<provider_name>Wordle|6mal5.com|Wördl)(?: 🇩🇪)? (?P<game_id>\d{3}) (?P<points>[\d|X|x]{1})/6')
"6mal5.com 🇩🇪 448 4/6"
DATETIME_FORMATS = {
    "android": "%d.%m.%y, %H:%M",
    "apple": "%d.%m.%y, %H:%M:%S",
}
DATE_FORMAT = "%d.%m.%y"
TIME_FORMAT = "%H:%M"
SPLIT_TEXTS = {
    "android": re.compile(r"(\d{2}\.\d{2}\.\d{2}, \d{2}:\d{2} - [\w ]+: )"),
    "apple": re.compile(r"(\[\d{2}\.\d{2}\.\d{2}, \d{2}:\d{2}:\d{2}\] [\w ]+: )"),
}
HEADER_PATTERNS = {
    "android": re.compile(
        r"(?P<date_time>\d{2}.\d{2}.\d{2}, \d{2}:\d{2}) - (?P<name>[\w ]+)"
    ),
    "apple": re.compile(
        r"\[(?P<date_time>\d{2}.\d{2}.\d{2}, \d{2}:\d{2}:\d{2})\] (?P<name>[\w ]+)"
    ),
}


@dataclass
class Message:
    date: datetime
    sender: str
    content: str


class MessageReader(Protocol):
    def read_messages(self) -> None:
        ...

    def get_messages(self) -> List[Message]:
        ...


@dataclass
class TextMessageReader:
    messages: List[Message] = field(default_factory=list)

    def read_messages(self, messages: str, dialect: str) -> List[Message]:
        # set dialect specific formats
        split_text = SPLIT_TEXTS[dialect]
        header_pattern = HEADER_PATTERNS[dialect]
        datetime_format = DATETIME_FORMATS[dialect]

        # print(messages)
        # clean source
        clean_text = remove_emojis_from_str(messages)

        # print(clean_text)
        # split messages string into header and body parts
        messages = split_text.split(clean_text)

        # print(messages)
        # build message instances and append them to the list
        for header, body in zip(messages[1:-1:2], messages[2::2]):
            # print(header, body)
            header_details = header_pattern.search(header)
            # message_datetime = datetime.strptime(header_details.group('date'), DATE_FORMAT).date()
            message = Message(
                date=datetime.strptime(
                    header_details.group("date_time"), datetime_format
                ),
                sender=header_details.group("name"),
                content=body,
            )
            # print(message)
            self.messages.append(message)

    def get_messages(self) -> List[Message]:
        return self.messages


def remove_emojis_from_str(input_string: str) -> str:
    return_str = RE_EMOJI.sub(r"", input_string)
    return_str = re.sub(r"[\n⬜⬛]+", "", return_str)
    return return_str
