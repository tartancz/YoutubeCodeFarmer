import logging
import os
import re
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytz
import requests.exceptions

from redeemer.wolt import CodeState
from videoEditor import Editor

if TYPE_CHECKING:
    from database.models import VideoModel, YtChannelModel, DiscountModel
    from ocr.ocr import OCR
    from redeemer import CodeState, Redeemer
    from youtube import Youtube
    from discord import Discord
    import cv2

logger = logging.getLogger(os.environ.get("LOGGER_NAME", "FARMER"))


class Farmer:
    video_name = "video.mp4"

    def __init__(self,
                 primary_ocr: 'OCR',  # faster ocr but less accurate
                 code_regex: str,
                 video_model: 'VideoModel',
                 yt_channel_model: 'YtChannelModel',
                 discount_model: 'DiscountModel',
                 wolt: 'Redeemer',  # Wolt class for handling interaction with redeemer website
                 youtube: 'Youtube',
                 secondary_ocr: 'OCR' = None,
                 # slower ocr but way more accurate, if not inserted then will always use primary_ocr
                 discord: 'Discord' = None,  # discord for notification
                 ):
        self.primary_ocr = primary_ocr
        self.video_model = video_model
        self.yt_channel_model = yt_channel_model
        self.discount_model = discount_model
        self.wolt = wolt
        self.youtube = youtube
        self.secondary_ocr = secondary_ocr
        self.discord = discord
        self.compiled_regex = re.compile(code_regex)

        self.insert_to_db_youtube_channel_if_not_exist()
        self.insert_latest_videos()

    def insert_to_db_youtube_channel_if_not_exist(self):
        try:
            self.yt_channel_model.insert(self.youtube.youtube_id)
            logger.info(f"created youtuber model with {self.youtube.youtube_id}")
        except sqlite3.IntegrityError:
            pass

    def insert_latest_videos(self):
        logger.info("inserting latest videos to db")
        for video in self.youtube.latest_uploaded_videos():
            try:
                self.video_model.insert(
                    video_id=video.id,
                    yt_channel_id=self.youtube.youtube_id,
                    publish_time=video.published_time,
                    skipped_finding=True
                )
                logger.debug(f"Inserted video {video.id} with publish time {video.published_time}")
            except sqlite3.IntegrityError:
                logger.debug(f"{video.id} is already in db")

    def get_new_video_id(self) -> str:
        self.youtube.wait_for_video_count_change()
        for x in range(10):
            videos = self.youtube.latest_uploaded_videos()
            video = self.video_model.find_video_which_is_not_in_db([video.id for video in videos])
            if video:
                return video
            time.sleep(10)

    def send_message_discord(self, msg: str):
        try:
            if self.discord:
                self.discord.send(msg)
        except Exception:
            pass

    def get_text(self, imag: 'cv2.typing.MatLike') -> str:
        text = self.primary_ocr.get_text(imag)
        if text and self.secondary_ocr is not None:
            text = self.secondary_ocr.get_text(imag)
        return text

    def process_video(self, video_path: Path) -> tuple[CodeState | None, str | None, int | None]:
        status: CodeState | None = None
        with Editor(video_path=(video_path / self.video_name)) as editor:
            editor.set_frame(editor.frame_count - 1)
            for imag in editor.iterate_thought_video():
                text = self.get_text(imag)
                code = self.compiled_regex.findall(text)
                if code and not self.discount_model.is_code_in_db(code[0]):
                    logger.info(f"Code was found with text '{text}'")
                    status = self.wolt.redeem_code(code[0])
                    if status == CodeState.SUCCESSFULLY_REDEEM or status == CodeState.EXPIRED or status.ALREADY_TAKEN:
                        yield status, text, editor.current_frame
                    elif status == CodeState.TOO_MANY_REQUESTS:
                        time.sleep(10)
                editor.add_frames(int(-editor.FPS * 2))
        yield status, None, None

    def create_database_log(
            self,
            status: CodeState,
            video_id: str,
            publish_time: datetime,
            code: str | None,
            frame: int | None
    ):
        self.video_model.insert(
            video_id=video_id,
            publish_time=publish_time,
            yt_channel_id=self.youtube.youtube_id,
            skipped_finding=False,
            contain_discount=True
        )
        self.discount_model.insert(
            video_id=video_id,
            was_right=(status != CodeState.BAD_CODE),
            how_long_to_process=(datetime.now(tz=pytz.UTC) - publish_time).seconds,
            activated_by_me=status == CodeState.SUCCESSFULLY_REDEEM,
            code=code,
            frame=frame
        )

    def _farm(self):
        logger.info("starting farmer")
        while True:
            new_video_id = self.get_new_video_id()
            if not new_video_id:
                logger.info("No new video was that is in database was found")
                continue
            logger.info(f"new video with ID {new_video_id}")
            self.send_message_discord(f"new video with ID {new_video_id}")
            detailed_new_video = self.youtube.get_details_about_video(new_video_id)
            if not "wolt" in detailed_new_video.description.lower() and not os.environ.get("FORCE_SEARCH", False):
                self.video_model.insert(
                    video_id=detailed_new_video.id,
                    publish_time=detailed_new_video.published_time,
                    yt_channel_id=self.youtube.youtube_id,
                    skipped_finding=True
                )
                logger.info("In video description is not wolt, skipping")
                continue
            video_path = Path(f"./temp/video-{detailed_new_video.id}")
            self.youtube.download_video(detailed_new_video.url, (video_path / self.video_name))
            for status, code, frame in self.process_video(video_path):
                self.create_database_log(
                    status=status,
                    video_id=detailed_new_video.id,
                    publish_time=detailed_new_video.published_time,
                    frame=frame,
                    code=code,
                )
                if status == CodeState.SUCCESSFULLY_REDEEM:
                    self.send_message_discord(
                        f"Code sucesfully redeem {code}, duration was {(datetime.now(tz=pytz.UTC) - detailed_new_video.published_time).seconds}")
                else:
                    self.send_message_discord(
                        f"Something went wrong, code: {status.name}, duration was  {(datetime.now(tz=pytz.UTC) - detailed_new_video.published_time).seconds}")

    def farm(self):
        self.discord.send("farming  Created")
        failures = list()
        while True:
            try:
                self._farm()
            except requests.exceptions.ConnectionError:
                # when internet connection is lost, will start pinging to google.com until response come successfully back
                logger.info(f"Not connection to internet")
                while True:
                    try:
                        requests.get("https://www.google.com")
                    except Exception:
                        time.sleep(10)
                        continue
                    break
            except Exception as e:
                #any other is logged
                self.discord.send(str(e))
                logger.exception(e)
            #if more then 5 failures in time windows program will end
            failures.append(time.time())
            if len(failures) < 5:
                continue
            oldest_exc = failures.pop(0)
            if time.time() - oldest_exc < 1800:
                return

    def _test(self, video_id: str):
        video_path = Path(f"./temp/video-{video_id}")
        self.youtube.download_video(self.youtube.get_video_url(video_id), (video_path / self.video_name))
        with Editor(video_path=(video_path / self.video_name)) as editor:
            editor.set_frame(editor.frame_count - 1)
            for imag in editor.iterate_thought_video():
                text = self.get_text(imag)
                code = self.compiled_regex.findall(text)
                if code:
                    logger.info(f"Code was found with text '{text}'")
                editor.add_frames(int(-editor.FPS * 2))