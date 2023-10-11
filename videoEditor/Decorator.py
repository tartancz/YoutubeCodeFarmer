from functools import wraps
from typing import TYPE_CHECKING

from .Errors import VideoIsClosedException

if TYPE_CHECKING:
    from .Editor import Editor


def opened_or_throw_error(func):
    @wraps(func)
    def wrapper(editor: 'Editor', *args, **kwargs):
        if editor.video is None:
            raise VideoIsClosedException("please Open() video or use __enter__")
        return func(editor, *args, **kwargs)

    return wrapper
