
# ======================================================================
# ||                                                               ||
# ||   ██████╗  █████╗ ██████╗ ██╗   ██╗███████╗███████╗██╗ ██████╗  ||
# ||   ██╔══██╗██╔══██╗██╔══██╗██║   ██║██╔════╝██╔════╝██║██╔═══██╗ ||
# ||   ██████╔╝███████║██████╔╝██║   ██║█████╗  ███████╗██║██║   ██║ ||
# ||   ██╔══██╗██╔══██║██╔══██╗██║   ██║██╔══╝  ╚════██║██║██║▄▄ ██║ ||
# ||   ██████╔╝██║  ██║██████╔╝╚██████╔╝███████╗███████║██║╚██████╔╝ ||
# ||   ╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚══════╝╚══════╝╚═╝ ╚══▀▀═╝  ||
# ║    ▓▒░ SHIV ░▒▓  s ᴇ ᴄ ᴜ ʀ ᴇ  ▓▒░ ɴ ᴇ ᴛ ᴡ ᴏ ʀ ᴋ ░▒▓    ║
# ||                                                               ||
# ======================================================================
# || PROJECT  : ♫─ᴀᴀʀᴜ MUSIC─♫ Public Music Repository                  ||
# || AUTHOR   : BabiesIQ Team                                      ||
# || REPO     : https://i.ibb.co/Lz4WxZnF/8418584090-29223.jpg               ||
# || API      : www.babyapi.pro                                    ||
# || TELEGRAM : t.me/BETABOT_HUB                                     ||
# ----------------------------------------------------------------------
# || LEGAL NOTICE                                                  ||
# || Use / upload / modify at your own risk.                       ||
# || Only config /.env edit allowed.                               ||
# || Do not modify core files.                                     ||
# || Keep this header if forked.                                   ||
# || Dev not responsible for ban / damage / api block.             ||
# ----------------------------------------------------------------------
# || SECURITY                                                      ||
# || Internal protection may exist.                                ||
# || Unauthorized change may stop system.                          ||
# || Use official API only -> www.babyapi.pro                      ||
# ======================================================================


import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters
# ------------------------------------
load_dotenv()
# ------------------------------------
# -----------------------------------------------------
API_ID = int(getenv("API_ID", None))
API_HASH = getenv("API_HASH", None)
BOT_TOKEN = getenv("BOT_TOKEN", None)
OWNER_USERNAME = getenv("OWNER_USERNAME","@SUKOON_S")
BOT_USERNAME = getenv("BOT_USERNAME" , "aaru_beatsbot")
BOT_NAME = getenv("BOT_NAME" , "╼⃝𖠁♫─ᴀᴀʀᴜ Qᴜᴇᴇɴ─♫𖠁⃝╾")
ASSUSERNAME = getenv("ASSUSERNAME" , "╼⃝𖠁♫─ᴀᴀʀᴜ Qᴜᴇᴇɴ─♫𖠁⃝╾")
# ---------------------------------------------------------
BASE_URL = getenv("BASE_URL", "https://BabyAPI.Pro")
API_KEY = getenv("API_KEY", None)
# ---------------------------------------------------------
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://shivbots:shivashish@cluster0.kdzu3eg.mongodb.net/?appName=Cluster0")
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 17000))
LOGGER_ID = int(getenv("LOGGER_ID", None))
OWNER_ID = int(getenv("OWNER_ID", None))
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")
UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/BABY-MUSIC/SPOTIFY_MUSIC",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv(
    "GIT_TOKEN", None
)
# ------------------------------------------------------------------------
# -------------------------------------------------------------------------
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/betabot_hub")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/betabot_support")
SOURCE = getenv("SOURCE", "https://preet_deal+bot")
CHAT = getenv("CHAT", "https://t.me/betabot_support")
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "False")
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "9000"))
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "9999999"))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "9999999"))
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "1c21247d714244ddbb09925dac565aed")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "709e1a2969664491b58200860623ef19")
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))
# ------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "5242880000"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "5242880000"))
# --------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
STRING1 = getenv("STRING_SESSION", "")
BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
START_IMG_URL = getenv(
    "START_IMG_URL", "https://files.catbox.moe/umpv9j.jpg"
)
PING_IMG_URL = getenv(
    "PING_IMG_URL", "https://files.catbox.moe/lnvimv.jpg"
)
PLAYLIST_IMG_URL = "https://files.catbox.moe/ho0744.png"
STATS_IMG_URL = "https://files.catbox.moe/ho0744.png"
TELEGRAM_AUDIO_URL = "https://files.catbox.moe/ho0744.png"
TELEGRAM_VIDEO_URL = "https://files.catbox.moe/ay13ih.png"
IQ_Proxy = "https://i.ytimg.com/vi"
STREAM_IMG_URL = "https://files.catbox.moe/ay13ih.png"
SOUNCLOUD_IMG_URL = "https://files.catbox.moe/ay13ih.png"
YOUTUBE_IMG_URL = "https://files.catbox.moe/ay13ih.png"
SPOTIFY_ARTIST_IMG_URL = "https://files.catbox.moe/umpv9j.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://files.catbox.moe/umpv9j.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://files.catbox.moe/umpv9j.jpg"
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))
# -----------------------------------------------------------------------------
# ------------------------------------------------------------------------------
if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://"
        )

# ====≈=========|   IQ   Proxy    |=============

__all__ = [
    "IQ_Proxy",
]
