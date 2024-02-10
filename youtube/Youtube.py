import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from pathlib import Path
from time import sleep

import pytz
import requests
from dateutil import parser
from pytube import YouTube as pytube_youtube

from youtube.errrors import VideoDoNotExistException, PathIsNotFileException

logger = logging.getLogger(os.environ.get("LOGGER_NAME", "FARMER"))

RESET_UNITS_TIME = time(7, tzinfo=pytz.UTC)


@dataclass
class Video:
    id: str
    url: str
    published_time: datetime
    # details of video
    video_lenght: time | None = None
    description: str | None = None


class Youtube:

    def __init__(self,
                 API_KEY: str,
                 youtube_id: str,
                 maximum_checks_per_day: int = 7000
                 ):
        self.API_KEY = API_KEY
        self.youtube_id = youtube_id
        self.maximum_checks_pet_day = maximum_checks_per_day
        self._previos_video_count: int | None = None
        self._reset_unit_datetime: datetime = Youtube.get_next_reset_units_datetime()
        self._used_points: int = 0

    @property
    def used_units(self) -> int:
        if self._reset_unit_datetime < datetime.now(tz=pytz.UTC):
            self._used_points = 0
            self._reset_unit_datetime = Youtube.get_next_reset_units_datetime()
        return self._used_points

    def get_video_count_url(self):
        """
        This method cost 1 unit
        """
        return f"https://youtube.googleapis.com/youtube/v3/channels?part=statistics&id={self.youtube_id}&key={self.API_KEY}"

    def get_last_videos_url(self, count=10):
        '''
        This method cost 100 unit
        '''
        return f"https://www.googleapis.com/youtube/v3/search?key={self.API_KEY}&channelId={self.youtube_id}&part=snippet,id&order=date&maxResults={count}"

    def get_details_about_video_url(self, video_id: str):
        '''
        This method cost 1 unit
        '''
        return f"https://youtube.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id={video_id}&key={self.API_KEY}"

    @staticmethod
    def get_video_url(video_id: str):
        return f"https://www.youtube.com/watch?v={video_id}"

    @staticmethod
    def download_video(video_url: str, save_path: Path | str) -> bool:
        '''
        will download youtube video with the lowest possible resolution
        :param video_url: full url for youtube video
        :param save_path: path to save to video
        :return:
        '''
        logger.info(f"dowloanding video {video_url}")
        if save_path is str:
            save_path = Path(save_path)
        Youtube.create_folder(save_path)
        ytb = pytube_youtube(video_url)
        video = ytb.streams.filter(file_extension="mp4").order_by('resolution').asc().first()
        return bool(video.download(filename=save_path, ))

    @staticmethod
    def get_next_reset_units_datetime() -> datetime:
        today = datetime.utcnow()
        next_day = today + timedelta(days=1)
        return datetime.combine(next_day.date(), RESET_UNITS_TIME, tzinfo=pytz.UTC)

    @staticmethod
    def _parse_duration(duration: str) -> time:
        '''
        :param duration: time format returned from youtube api
        :return: class time of duration
        '''
        hours_match = re.search(r'(\d+)H', duration)
        minutes_match = re.search(r'(\d+)M', duration)
        seconds_match = re.search(r'(\d+)S', duration)

        hours = int(hours_match.group(1)) if hours_match else 0
        minutes = int(minutes_match.group(1)) if minutes_match else 0
        seconds = int(seconds_match.group(1)) if seconds_match else 0

        return time(hour=hours, minute=minutes, second=seconds)

    @staticmethod
    def _parse_datetime(date_str: str) -> datetime:
        return parser.parse(date_str)

    def video_count(self) -> int:
        """
        make request to youtube api to get number of videos of users
        :return: number of videos on channel
        """
        self._used_points += 1
        logger.debug(f"Used Channels endpoint - costs 1 units - have used {self.used_units} units - ")
        response = requests.get(self.get_video_count_url())
        return json.loads(response.text)["items"][0]["statistics"]["videoCount"]

    @staticmethod
    def create_folder(path: Path | str):
        if path is str:
            path = Path(path)
        if not path.is_file():
            PathIsNotFileException(f"{path.absolute()} is not file.")
        path.parent.mkdir(parents=True, exist_ok=True)

    def is_changed_video_count(self) -> bool:
        """
        Will check if new video was uploaded from last call this function
        """
        if self._previos_video_count is None:
            self._previos_video_count = self.video_count()
            return False

        actual_video_count = self.video_count()
        # if youtuber delete video
        if actual_video_count < self._previos_video_count:
            self._previos_video_count = actual_video_count
        # new video
        if actual_video_count != self._previos_video_count:
            logger.info(f"video count has changed from {self._previos_video_count} to {actual_video_count}")
            self._previos_video_count = actual_video_count
            return True
        return False

    def latest_uploaded_videos(self, count: int = 10) -> list[Video]:
        '''
        make request to youtube api for the latest videos
        :param count: how many latest videos return
        :return: list of Video
        '''
        self._used_points += 100
        logger.debug(f"Used SEARCH LIST - costs 100 units - have used {self.used_units} units - ")
        request = requests.get(self.get_last_videos_url(count))
        parsed_req = json.loads(request.text)
        videos = []
        for item in parsed_req["items"]:
            video = Video(
                id=item["id"]["videoId"],
                url=Youtube.get_video_url(video_id=item["id"]["videoId"]),
                published_time=Youtube._parse_datetime(item["snippet"]["publishedAt"])
            )
            logger.debug(f"latest uploaded videos: {video.url} published at {video.published_time}")
            videos.append(video)
        return videos

    def get_details_about_video(self, video_id: str) -> Video:
        '''
        make request to youtube api for the fully described video
        :param video_id:
        :return: Video with description and published_at
        '''
        self._used_points += 100
        logger.debug(f"Used VIDEO LIST - costs 100 units - have used {self.used_units} units - ")
        request = requests.get(self.get_details_about_video_url(video_id))
        parsed_req = json.loads(request.text)
        if len(parsed_req["items"]) < 1:
            raise VideoDoNotExistException(f"Video with id {video_id} do not exist")
        item = parsed_req["items"][0]
        video = Video(
            id=item["id"],
            url=Youtube.get_video_url(video_id=item["id"]),
            published_time=Youtube._parse_datetime(item["snippet"]["publishedAt"]),
            video_lenght=Youtube._parse_duration(item["contentDetails"]["duration"]),
            description=item["snippet"]["description"]
        )
        return video

    def wait_for_video_count_change(self):
        '''
        block program until video count will change which mean probably new video was uploaded
        '''
        seconds_in_day = 60 * 60 * 24
        while True:
            if self.is_changed_video_count():
                return
            sleep(seconds_in_day / self.maximum_checks_pet_day)
