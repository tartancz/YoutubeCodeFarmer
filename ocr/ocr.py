import logging
import os
from abc import ABC, abstractmethod
from difflib import get_close_matches

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cv2.typing import MatLike

logger = logging.getLogger(os.environ.get("LOGGER_NAME", "FARMER"))


class OCR(ABC):
    def __init__(self, search_value: str):
        self.search_value = search_value

    @abstractmethod
    def parse(self, image: 'MatLike') -> list[str]:
        """
        abstract method that will parse image with ocr
        :param image: image input
        :return: list of texts found in video
        """
        pass

    def get_text(self, image) -> str:
        texts = self.parse(image)
        logger.debug(f"texts found in image are {texts}")
        matches = get_close_matches(self.search_value, texts, n=1, cutoff=0.3)
        if matches:
            logger.info(f"Match found in OCR:{self.__class__.__name__}, text: {matches[0]}")
            return matches[0]
        return ""
