from dataclasses import dataclass
from typing import TYPE_CHECKING

from database.errors import RowDontExistException

if TYPE_CHECKING:
    from sqlite3 import Connection


@dataclass
class YtChannel:
    channel_id: str
    video_count: int


class YtChannelModel:
    def __init__(self, db: 'Connection'):
        self._db = db

    def insert(self, channel_id: str, video_count: int | None = None):
        pass

    def update_video_count(self, channel_id: str, video_count: int):
        pass

    def get(self, channel_id: str) -> YtChannel:
        return YtChannel(channel_id=channel_id, video_count=200)
