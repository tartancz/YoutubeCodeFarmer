import logging
import os
from dataclasses import dataclass
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlite3 import Connection

logger = logging.getLogger(os.environ.get("LOGGER_NAME", "FARMER"))

@dataclass
class Video:
    video_id: str
    yt_channel_id: str
    publish_time: datetime
    skipped_finding: bool
    contain_discount: bool


class VideoModel:
    def __init__(self, db: 'Connection'):
        self._db = db
        self._cursor = db.cursor()

    def insert(self,
               video_id: str,
               yt_channel_id: str,
               publish_time: datetime,
               skipped_finding: bool,
               contain_discount: bool | None = None
               ):
        insert_query = '''
            INSERT INTO video (video_id, yt_channel_id, publish_time, skipped_finding, contain_discount)
            VALUES (?, ?, ?, ?, ?)
        '''
        logger.debug(f"inserting video with video_id: {video_id}, yt_channel_id: {yt_channel_id}, publish_time: {publish_time}, skipped_finding: {skipped_finding}, skipped_finding: {skipped_finding}, contain_discount: {contain_discount}")
        self._cursor.execute(insert_query, [video_id, yt_channel_id, publish_time, skipped_finding, contain_discount])
        self._db.commit()

    def find_video_which_is_not_in_db(self, videos_ids: list[str]) -> str:
        """
        will search for video_id that is not in database
        return first match, if every id is in db return empty string
        :param videos_ids: list of videos ids
        :return: id that is not in database or empty string
        """
        find_query = '''
            select EXISTS(SELECT *
            FROM video
            where video_id = ?)
        '''
        logger.debug(f"Finding video which is not in db...")
        for video_id in videos_ids:
            self._cursor.execute(find_query, [video_id])
            if not self._cursor.fetchone()[0]:
                logger.debug(f"video with ID {video_id} was not found in db")
                return video_id
            logger.debug(f"Video with ID {video_id} is in db.")
        return ""
