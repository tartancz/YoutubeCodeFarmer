from typing import TYPE_CHECKING

from paddleocr import PaddleOCR as Paddle

from .ocr import OCR

if TYPE_CHECKING:
    from cv2.typing import MatLike


class PaddleOcr(OCR):

    def __init__(self, search_value: str):
        super().__init__(search_value)
        self.reader = Paddle(lang='en', show_log=False, use_gpu=False)

    def parse(self, image: 'MatLike') -> list[str]:
        texts = []
        result = self.reader.ocr(image, cls=False)
        for idx in range(len(result)):
            res = result[idx]
            if not res:
                continue
            for line in res:
                texts.append(line[1][0])
        return texts
