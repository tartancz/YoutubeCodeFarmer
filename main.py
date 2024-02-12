import logging
import os
import sqlite3

from dotenv import load_dotenv

from database.models import (
    VideoModel,
    YtChannelModel,
    DiscountModel,
    TokenModel
)
from discord import Discord
from farmer import Farmer
from ocr import EasyOcr, PaddleOcr
from redeemer import Wolt
from youtube import Youtube


# TODO: PRIDAT PARSER NA WEB BROWSER KDYZ NENAJDCE NEJNOVEJSI VIDEO PRES API
# TODO: MULTIPLE YOUTUBE API KEY
def main(
        cnstr: str,
        API_KEY: str,
        youtube_id: str,
        discord_bot_token: str,
        discord_channel_id: int,
        search_value: str,
        code_regex: str,
):
    db_conn = sqlite3.connect(cnstr, detect_types=sqlite3.PARSE_DECLTYPES)
    farmer = Farmer(
        primary_ocr=EasyOcr(search_value),
        video_model=VideoModel(db_conn),
        yt_channel_model=YtChannelModel(db_conn),
        discount_model=DiscountModel(db_conn),
        wolt=Wolt(token_model=TokenModel(db_conn)),
        youtube=Youtube(
            API_KEY=API_KEY,
            youtube_id=youtube_id
        ),
        secondary_ocr=PaddleOcr(search_value),
        discord=Discord(
            channel_id=discord_channel_id,
            bot_token=discord_bot_token
        ),
        code_regex=code_regex
    )
    farmer.farm()
    #farmer._test("o5sJZ1iOTwc")

def get_env_or_throw_error_msg(env: str, help_msg: str):
    try:
        return os.environ[env]
    except KeyError:
        raise KeyError(f"Please set the environment variable {env}, help: {help_msg}")

def setLogging():
    logger = logging.getLogger(os.environ.get("LOGGER_NAME", "FARMER"))
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler("app.log")
    fh.setLevel(logging.DEBUG)
    fr = logging.Formatter(fmt='%(asctime)s : %(levelname)s : %(filename)s : %(message)s', datefmt="%m/%d/%Y %H:%M:%S")
    fh.setFormatter(fr)

    logger.addHandler(fh)

if __name__ == '__main__':
    load_dotenv()
    setLogging()
    main(
        cnstr=get_env_or_throw_error_msg("CNSTR", "Connection string to database"),
        API_KEY=get_env_or_throw_error_msg("API_KEY", "Your API key to youtube"),
        youtube_id=get_env_or_throw_error_msg("YOUTUBE_ID", "Youtubers id for farming"),
        discord_bot_token=get_env_or_throw_error_msg("DISCORD_BOT_TOKEN", "Discord token for access bot"),
        discord_channel_id=int(get_env_or_throw_error_msg("DISCORD_CHANNEL_ID", "Discord channel id for logging")),
        search_value=get_env_or_throw_error_msg("SEARCH_VALUE", "Similar text that will contain code"),
        code_regex=get_env_or_throw_error_msg("CODE_REGEX", "Regex of discount that will be redeemed"),

    )
#TODO PROJET POPISEK VIDEA JESTLI WOLT KOD NENI TAM
#TODO PROJET CELE VIDEO / JET DALE I KDYZ JSEM UZ NASEL WOLT KOD
#