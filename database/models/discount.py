import os
from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlite3 import Connection

logger = logging.getLogger(os.environ.get("LOGGER_NAME", "FARMER"))


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
        logger.debug(f"inserting discount to db with video_id:{video_id}, code:{code}, frame:{frame}, was_right:{was_right}, activated_by_me:{activated_by_me}, how_long_to_process:{how_long_to_process}")
        return self._cursor.lastrowid

    def is_code_in_db(self, code: str) -> bool:
        select_query = '''
        SELECT 
        CASE WHEN exists(SELECT * FROM discount WHERE code LIKE %?%) THEN 1
        ELSE 0
        END
        '''
        self._cursor.execute(select_query, [code])
        is_in_db,  = self._cursor.fetchone()
        return is_in_db
