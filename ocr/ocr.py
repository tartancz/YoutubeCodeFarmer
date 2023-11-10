from abc import ABC, abstractmethod
from difflib import get_close_matches

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cv2.typing import MatLike


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
        matches = get_close_matches(self.search_value, texts, n=1, cutoff=0.3)
        return matches[0] if len(matches) > 0 else ""
