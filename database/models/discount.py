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
        self._cursor = db.cursor()

    def insert(self,
               video_id: str,
               code: str,
               frame: int,
               was_right: bool,
               activated_by_me: bool,
               how_long_to_process: int
               ) -> int:
        insert_query = '''
            INSERT INTO discount (video_id, code, frame, was_right, activated_by_me, how_long_to_process)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        self._cursor.execute(insert_query, [video_id, code, frame, was_right, activated_by_me, how_long_to_process])
        self._db.commit()
        return self._cursor.lastrowid
