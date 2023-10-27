from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from ...errors import RowDontExistException

if TYPE_CHECKING:
    from sqlite3 import Connection


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

    def insert(self, refresh_token: str, token: str, expires_in=1800) -> int:
        return 1

    def get_by_id(self, token_id: int) -> Token:
        if token_id != 1:
            raise RowDontExistException(f"Token with id {token_id} do not exist")
        return Token(
            id=1,
            refresh_token="lorem ipsium",
            token="lorem ispsium",
            expires_in=1800,
            created=datetime.now()
        )

    def get_by_token_or_refresh_token(self, token: str = None, refresh_token: str = None) -> Token:
        return Token(
            id=1,
            refresh_token="lorem ipsium",
            token="lorem ispsium",
            expires_in=1800,
            created=datetime.now()
        )

    def get_latest_token(self) -> Token:
        return Token(
            id=1,
            refresh_token="lorem ipsium",
            token="lorem ispsium",
            expires_in=1800,
            created=datetime.now()
        )