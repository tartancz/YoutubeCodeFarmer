import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from ..errors import RowDontExistException

if TYPE_CHECKING:
    from sqlite3 import Connection

logger = logging.getLogger(os.environ.get("LOGGER_NAME", "FARMER"))


@dataclass
class Token:
    id: int
    refresh_token: str
    token: str
    expires_in: int
    created: datetime


class TokenModel:
    def __init__(self, db: 'Connection'):
        self._db = db
        self._cursor = db.cursor()

    def insert(self, refresh_token: str, token: str, expires_in=1800) -> int:
        insert_query = '''
            INSERT INTO token (refresh_token, token, expires_in)
            VALUES (?, ?, ?);
        '''
        logger.debug(f"inserting Token to db with refresh_token: {refresh_token}, token: {token}, expires_in: {expires_in}")
        self._cursor.execute(insert_query, [refresh_token, token, expires_in])
        self._db.commit()

        return self._cursor.lastrowid

    def get_by_id(self, token_id: int) -> Token:
        select_query = '''
            SELECT id, refresh_token, token, expires_in, created
            FROM token
            WHERE id = ?
            LIMIT 1;
        '''
        logger.debug(f"getting token by id: {token_id}")
        self._cursor.execute(select_query, [token_id])
        token_row = self._cursor.fetchone()
        if not token_row:
            logger.debug(f"token with id {token_id} was not found")
            raise RowDontExistException(f"Token with id {token_id} do not exist")
        return Token(*token_row)

    def get_by_token_or_refresh_token(self, token: str = None, refresh_token: str = None):
        select_query = '''
            SELECT id, refresh_token, token, expires_in, created
            FROM token
            WHERE token=? OR refresh_token=?
            LIMIT 1;
        '''
        logger.debug(f"getting token token : {token} or by refresh_token : {refresh_token} ")
        self._cursor.execute(select_query, [token, refresh_token])
        token_row = self._cursor.fetchone()
        if not token_row:
            raise RowDontExistException(f"Token with id {token} do not exist")
        return Token(*token_row)

    def get_latest_token(self) -> Token:
        select_query = '''
            SELECT id, refresh_token, token, expires_in, created
            FROM token
            ORDER BY created DESC
            LIMIT 1;
        '''
        logger.debug("getting the latest token")
        self._cursor.execute(select_query)
        token_row = self._cursor.fetchone()
        if not token_row:
            raise RowDontExistException("table token is empty")
        return Token(*token_row)
