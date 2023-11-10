from typing import TYPE_CHECKING

import easyocr

from .ocr import OCR

if TYPE_CHECKING:
    from cv2.typing import MatLike


class EasyOcr(OCR):

    def __init__(self, search_value: str):
        super().__init__(search_value)
        self.reader = easyocr.Reader(['en'])

    def parse(self, image: 'MatLike') -> list[str]:
        texts = self.reader.readtext(image, detail=0)
        return texts
