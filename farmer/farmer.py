import logging
from datetime import datetime

import pytz

from redeemer.wolt import CodeState
from videoEditor import Editor
import sqlite3
from typing import TYPE_CHECKING
from pathlib import Path

import time


if TYPE_CHECKING:
    from database.models import VideoModel, YtChannelModel, DiscountModel
    from ocr.ocr import OCR
    from redeemer import CodeState, Redeemer
    from youtube import Youtube
    from discord import Discord
    import cv2





class Farmer:
    video_name = "video.mp4"
    def __init__(self,
                 primary_ocr: 'OCR',  # faster ocr but less accurate
                 video_model: 'VideoModel',
                 yt_channel_model: 'YtChannelModel',
                 discount_model: 'DiscountModel',
                 wolt: 'Redeemer',  # Wolt class for handling interaction with redeemer website
                 youtube: 'Youtube',
                 secondary_ocr: 'OCR' = None,  # slower ocr but way more accurate, if not inserted then will always use primary_ocr
                 discord: 'Discord' = None # discord for notification
                 ):
        self.primary_ocr = primary_ocr
        self.video_model = video_model
        self.yt_channel_model = yt_channel_model
        self.discount_model = discount_model
        self.wolt = wolt
        self.youtube = youtube
        self.secondary_ocr = secondary_ocr
        self.discord = discord

        self.insert_to_db_youtube_channel_if_not_exist()
        self.insert_latest_videos()

    def insert_to_db_youtube_channel_if_not_exist(self):
        try:
            self.yt_channel_model.insert(self.youtube.youtube_id)
            logging.info(f"created youtuber model with {self.youtube.youtube_id}")
        except sqlite3.IntegrityError:
            pass

    def insert_latest_videos(self):
        logging.debug("inserting latest videos to db")
        for video in self.youtube.latest_uploaded_videos():
            try:
                self.video_model.insert(
                    video_id=video.id,
                    yt_channel_id=self.youtube.youtube_id,
                    publish_time=video.published_time,
                    skipped_finding=True
                )
            except sqlite3.IntegrityError:
                pass

    def get_new_video_id(self) -> str:
        self.youtube.wait_for_video_count_change()
        for x in range(10):
            videos = self.youtube.latest_uploaded_videos()
            video = self.video_model.find_video_which_is_not_in_db([video.id for video in videos])
            if video:
                return video
            time.sleep(10)


    def send_message_discord(self, msg: str):
        if self.discord:
            self.discord.send(msg)

    def get_code(self, imag: 'cv2.typing.MatLike') -> str:
        code = self.primary_ocr.get_text(imag)
        if code and self.secondary_ocr is not None:
            code = self.secondary_ocr.get_text(imag)
        return code

    def process_video(self, video_path: Path) -> (CodeState, str | None, int | None):
        status: CodeState = None
        with Editor(video_path=(video_path / self.video_name)) as editor:
            editor.set_frame(editor.frame_count - 1)
            for imag in editor.iterate_thought_video():
                code = self.get_code(imag)
                if code:
                    logging.info(f"Code was found with text '{code}'")
                    status = self.wolt.redeem_code(code[-12:])
                    if status == CodeState.SUCCESSFULLY_REDEEM or status == CodeState.EXPIRED or status.ALREADY_TAKEN:
                        return (status, code, editor.current_frame)
                    elif status == CodeState.TOO_MANY_REQUESTS:
                        time.sleep(10)
                editor.add_frames(int(-editor.FPS * 2))
        return (status, None, None)

    def create_database_log(
        self,
        status: CodeState,
        video_id: str,
        publish_time: datetime,
        code: str |None,
        frame: int | None
        ):
        print(datetime.utcnow(), publish_time)
        self.video_model.insert(
            video_id=video_id,
            publish_time=publish_time,
            yt_channel_id=self.youtube.youtube_id,
            skipped_finding=False,
            contain_discount=True
        )
        self.discount_model.insert(
            video_id=video_id,
            was_right= (status != CodeState.BAD_CODE),
            how_long_to_process = (datetime.now(tz=pytz.UTC) - publish_time).seconds,
            activated_by_me= status == CodeState.SUCCESSFULLY_REDEEM,
            code= code,
            frame=frame
        )



    def _farm(self):
        logging.info("starting farmer")
        while True:
            new_video_id = self.get_new_video_id()
            if not new_video_id:
                logging.info("No new video was that is in database was found")
                continue
            logging.info(f"new video with ID {new_video_id}")
            self.send_message_discord(f"new video with ID {new_video_id}")
            detailed_new_video = self.youtube.get_details_about_video(new_video_id)
            if not "wolt" in detailed_new_video.description.lower():
                self.video_model.insert(
                    video_id=detailed_new_video.id,
                    publish_time=detailed_new_video.published_time,
                    yt_channel_id=self.youtube.youtube_id,
                    skipped_finding=True
                )
                logging.info("In video description is not wolt, skipping")
                continue
            video_path = Path(f"./temp/video-{detailed_new_video.id}")
            self.youtube.download_video(detailed_new_video.url, (video_path / self.video_name))
            status, code, frame = self.process_video(video_path)
            self.create_database_log(
                status=status,
                video_id=detailed_new_video.id,
                publish_time=detailed_new_video.published_time,
                frame=frame,
                code=code,
            )
            #TODO: add logging and discord


    def farm(self):
        failures = list()
        try:
            self._farm()
        except Exception as e:
            self.discord.send(e)
            logging.exception(e)
            # if len(failures) < 5:
            #     failures.append(datetime.now())
            # else:


    def find_text(self, url):
        self.youtube.download_video(url, Path("./temp/video.mp4"))
        with Editor(video_path=Path("./temp/video.mp4")) as editor:
            print("video")
            editor.set_frame(editor.frame_count - 1)
            for imag in editor.iterate_thought_video():
                found = False
                code = self.primary_ocr.get_text(imag)
                print(editor.current_frame)
                editor.add_frames(-20)



