from dataclasses import dataclass

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlite3 import Connection


@dataclass
class Discount:
    id: int
    video_id: int
    code: str
    frame: int
    was_right: bool
    activated_by_me: bool
    how_long_to_process: bool


class DiscountModel:
    def __init__(self, db: 'Connection'):
        self._db = db
        self._Discount: None | Discount = None
    def insert(self,
               video_id: str,
               code: str,
               frame: int,
               was_right: bool,
               activated_by_me: bool,
               how_long_to_process: int
               ) -> int:
        self._Discount = Discount(
            id=1,
            video_id = video_id,
            code =  code,
            frame = frame,
            was_right =   was_right,
            activated_by_me = activated_by_me,
            how_long_to_process = how_long_to_process
        )
        return 1
