import logging
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

from database.errors import RowDontExistException

if TYPE_CHECKING:
    from sqlite3 import Connection

logger = logging.getLogger(os.environ.get("LOGGER_NAME", "FARMER"))



@dataclass
class YtChannel:
    channel_id: str
    video_count: int


class YtChannelModel:
    def __init__(self, db: 'Connection'):
        self._db = db
        self._cursor = db.cursor()

    def insert(self, channel_id: str, video_count: int | None = None):
        insert_query = '''
            INSERT INTO yt_channel (channel_id, video_count )
            VALUES (?, ?);
        '''
        logging.debug(f"Inserting YTchannel with channel_id: {channel_id}, video_count: {video_count}")
        self._cursor.execute(insert_query, [channel_id, video_count])
        self._db.commit()

    def update_video_count(self, channel_id: str, video_count: int):
        update_query = '''
            UPDATE yt_channel
            SET video_count = ?
            where channel_id = ?;
        '''
        logging.debug(f"updating video count to {video_count}")
        self._cursor.execute(update_query, [video_count, channel_id])
        self._db.commit()

    def get(self, channel_id: str) -> YtChannel:
        get_query = '''
            SELECT video_count
            FROM yt_channel 
            where channel_id = ?
            LIMIT 1;
        '''
        logger.debug(f"getting youtube channel with id {channel_id}")
        self._cursor.execute(get_query, [channel_id])
        video_count, = self._cursor.fetchone()
        if not video_count:
            raise RowDontExistException("Channel with this id do not exist in db")
        return YtChannel(channel_id=channel_id, video_count=video_count)
