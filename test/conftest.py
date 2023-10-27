import pytest
from farmer import Farmer

from ocr import EasyOcr, PaddleOcr
from database.models.mocks import *
from .mocks.wolt_mock import Wolt
from .mocks.youtube_mock import Youtube_mock

@pytest.fixture(scope='session')
def farmer() -> Farmer:
    far = Farmer(
        primary_ocr=EasyOcr(),
        video_model=VideoModel(None),
        yt_channel_model=YtChannelModel(None),
        discount_model=DiscountModel(None),
        wolt=Wolt(token_model=TokenModel(None)),
        youtube=Youtube_mock(
            API_KEY="API_KEY",
            youtube_id="youtube_id"
        ),
        secondary_ocr=PaddleOcr(),
    )
    return far
