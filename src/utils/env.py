# settings.py
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '../../.env')
load_dotenv(dotenv_path)

TOKEN = os.environ.get("Token")
CMC_KEY = os.environ.get("CMCKey")
SERVER_ID = int(os.environ.get("ServerId"))
NEO_CHANNEL = int(os.environ.get("NeoChannel"))
ARK_CHANNEL = int(os.environ.get("ArkChannel"))
FIRO_CHANNEL = int(os.environ.get("FiroChannel"))
ZEN_CHANNEL = int(os.environ.get("ZenChannel"))
BTC_CHANNEL = int(os.environ.get("BitcoinChannel"))
DASH_CHANNEL = int(os.environ.get("DashChannel"))
SPAM_BOT_CHANNEL = int(os.environ.get("SpamBotChannel"))
BINANCE_WS_URL = os.environ.get("BinanceWssURL")
