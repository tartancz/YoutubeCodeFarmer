import datetime
from pathlib import Path

from pytz import UTC

from youtube import Youtube, Video


class ProgramEndedException(Exception):
    pass


class Youtube_mock():
    def __init__(self,
                 API_KEY: str,
                 youtube_id: str,
                 maximum_checks_per_day: int = 7000
                 ):
        self.youtube_id = youtube_id
        self.first_check = True

    def wait_for_video_count_change(self):
        if self.first_check:
            self.first_check = False
            return
        raise ProgramEndedException()

    def latest_uploaded_videos(self):
        return [Video(
            id="PctEhHUqnvY",
            url="https://www.youtube.com/watch?v=PctEhHUqnvY",
            published_time=datetime.datetime.now(UTC),
        )]

    def get_details_about_video(self, video_id: str) -> Video:
        video = Video(
            id="PctEhHUqnvY",
            url="https://www.youtube.com/watch?v=PctEhHUqnvY",
            published_time=datetime.datetime.now(UTC),
            video_lenght=60,
            description="WOLT"
        )
        return video

    @staticmethod
    def download_video(video_url, save_path: Path | str) -> bool:
        Youtube.download_video(video_url, save_path)
