import easyocr

from .ocr import OCR

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cv2.typing import MatLike

class EasyOcr(OCR):
    @property
    def search_value(self):
        return "Kod na WOLT - AG100"

    def __init__(self):
        self.reader = easyocr.Reader(['en'])

    def parse(self, image: 'MatLike') -> list[str]:
        texts = self.reader.readtext(image, detail=0)
        return texts
