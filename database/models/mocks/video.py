from datetime import datetime


class VideoModel:
    def __init__(self, db: 'Connection'):
        self._db = db

    def insert(self,
               video_id: str,
               yt_channel_id: str,
               publish_time: datetime,
               skipped_finding: bool,
               contain_discount: bool | None = None
               ):
        pass

    def find_video_which_is_not_in_db(self, videos_ids: list[str]) -> str:
        return videos_ids[0]
