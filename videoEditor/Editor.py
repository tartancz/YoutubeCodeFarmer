import logging
from functools import cached_property
from pathlib import Path

import cv2

from .Decorator import opened_or_throw_error
from .Errors import frameIsOutOfFrameCountException

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Iterator


class Editor:
    video: cv2.VideoCapture | None = None

    def __init__(self, video_path: Path):
        self.video_path = str(video_path.absolute())
        self.current_frame = 1

    @cached_property
    @opened_or_throw_error
    def FPS(self) -> float:
        """
        :return: actual framerate of opened video
        """
        return self.video.get(cv2.CAP_PROP_FPS)

    @cached_property
    @opened_or_throw_error
    def frame_count(self) -> float:
        """
        :return: count of frames of video
        """
        return self.video.get(cv2.CAP_PROP_FRAME_COUNT)

    @cached_property
    @opened_or_throw_error
    def shape_of_video(self) -> (int, int):
        height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        return width, height

    @opened_or_throw_error
    def iterate_thought_video(self) -> 'Iterator[cv2.typing.MatLike]':
        while True:
            try:
                yield self._get_image()
            except frameIsOutOfFrameCountException:
                break


    def _add_frames(self, add_count: int | float):

        self._set_frame(self.current_frame + add_count)

    @opened_or_throw_error
    def add_frames(self, add_count: int | float):
        self._add_frames(add_count)

    def _set_frame(self, cur_frame: int | float):
        logging.debug(f"setting frame on {cur_frame}")
        self.current_frame = cur_frame
        self.video.set(cv2.CAP_PROP_POS_FRAMES, cur_frame)

    @opened_or_throw_error
    def set_frame(self, cur_frame: int | float):
        self._set_frame(cur_frame)

    def _get_image(self) -> cv2.typing.MatLike:
        logging.debug("Getting image of current frame")
        ret, img = self.video.read()
        if not ret or self.current_frame < 0:
            raise frameIsOutOfFrameCountException(
                f"frame {self.video.get(cv2.CAP_PROP_POS_FRAMES)} is bigger then {self.frame_count}")
        return img

    @opened_or_throw_error
    def get_image(self) -> cv2.typing.MatLike:
        return self._get_image()

    def __enter__(self):
        """
        calls open_video()
        """
        self.open_video()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        calls close_video()
        """
        self.close_video()

    def open_video(self):
        """
        Open cv2.VideoCapture class of video
        """
        logging.info(f"Opening video {self.video_path}")
        if self.video is not None:
            raise AttributeError("Video is already opened")
        self.video = cv2.VideoCapture(self.video_path)

    def close_video(self):
        """
        close cv2.VideoCapture class of video and set video to None
        """
        logging.info(f"Closing video {self.video_path}")
        if self.video is None:
            raise AttributeError("Video is already closed")
        self.current_frame = 0
        self.video.release()
        self.video = None
