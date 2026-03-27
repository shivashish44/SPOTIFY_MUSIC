
# ======================================================================
# ||                                                               ||
# ||   ██████╗  █████╗ ██████╗ ██╗   ██╗███████╗███████╗██╗ ██████╗  ||
# ||   ██╔══██╗██╔══██╗██╔══██╗██║   ██║██╔════╝██╔════╝██║██╔═══██╗ ||
# ||   ██████╔╝███████║██████╔╝██║   ██║█████╗  ███████╗██║██║   ██║ ||
# ||   ██╔══██╗██╔══██║██╔══██╗██║   ██║██╔══╝  ╚════██║██║██║▄▄ ██║ ||
# ||   ██████╔╝██║  ██║██████╔╝╚██████╔╝███████╗███████║██║╚██████╔╝ ||
# ||   ╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚══════╝╚══════╝╚═╝ ╚══▀▀═╝  ||
# ║    ▓▒░ ʙ ᴀ ʙ ɪ ᴇ sＩＱ ░▒▓  s ᴇ ᴄ ᴜ ʀ ᴇ  ▓▒░ ɴ ᴇ ᴛ ᴡ ᴏ ʀ ᴋ ░▒▓    ║
# ||                                                               ||
# ======================================================================
# || PROJECT  : SPOTIFY_MUSIC Public Music Repository                  ||
# || AUTHOR   : BabiesIQ Team                                      ||
# || REPO     : github.com/BABY-MUSIC/SPOTIFY_MUSIC                ||
# || API      : www.babyapi.pro                                    ||
# || TELEGRAM : t.me/BabiesIQ                                      ||
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

import asyncio
import os
import re
import json
from typing import Union
import requests
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch
from SPOTIFY_MUSIC.utils.database import is_on_off
from SPOTIFY_MUSIC.utils.formatters import time_to_seconds
import glob
import random
import logging
import aiohttp
import config
from config import LOGGER_ID
from SPOTIFY_MUSIC import app
from config import BASE_URL, API_KEY
from urllib.parse import urlparse

# --- PROTECTION UTILITY ---
import re
from urllib.parse import urlparse, parse_qs, urlencode

def sanitize_arg(arg: str, debug: bool = False) -> str:
    """
    Allow only valid YouTube playlist URLs.
    Returns cleaned playlist URL or empty string if invalid.
    Debug mode prints step-by-step validation.
    """

    def log(msg):
        if debug:
            print(f"[DEBUG] {msg}")

    if not isinstance(arg, str):
        log("Input is not a string")
        return ""

    arg = arg.strip()
    log(f"Input after strip: {arg}")

    # Basic URL validation
    try:
        parsed = urlparse(arg)
        log(f"Parsed URL: {parsed}")
    except Exception as e:
        log(f"URL parsing failed: {e}")
        return ""

    # ✅ Allow only YouTube domains
    allowed_domains = {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com"
    }

    domain = parsed.netloc.lower()
    log(f"Domain: {domain}")

    if domain not in allowed_domains:
        log("Domain not allowed")
        return ""

    # ✅ Extract query params
    query = parse_qs(parsed.query)
    log(f"Query params: {query}")

    # Playlist must have "list" param
    playlist_id = query.get("list", [None])[0]
    log(f"Playlist ID: {playlist_id}")

    if not playlist_id:
        log("No playlist ID found")
        return ""

    # ✅ Strict playlist ID validation
    if not re.match(r'^[a-zA-Z0-9_-]{10,}$', playlist_id):
        log("Invalid playlist ID format")
        return ""

    # ✅ Rebuild clean URL
    clean_query = urlencode({"list": playlist_id})
    clean_url = f"https://www.youtube.com/playlist?{clean_query}"

    log(f"Final Clean URL: {clean_url}")

    return clean_url

def cookie_txt_file():
    cookie_dir = f"{os.getcwd()}/cookies"
    if not os.path.exists(cookie_dir):
        return None
    cookies_files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]
    if not cookies_files:
        return None
    cookie_file = os.path.join(cookie_dir, random.choice(cookies_files))
    return cookie_file

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def _download_media(link: str, kind: str, exts: list[str], wait: int = 60):
    vid = link.split("v=")[-1].split("&")[0]
    os.makedirs("downloads", exist_ok=True)
    for ext in exts:
        path = f"downloads/{vid}.{ext}"
        if os.path.exists(path):
            return path
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}/api/{kind}?query={vid}&eq=pro&api={API_KEY}"
            ) as resp:
                res = await resp.json()
            stream = res.get("stream")
            media_type = res.get("type")
            if not stream:
                raise Exception(f"{kind} stream not found")
            if media_type == "live":
                return stream
            for _ in range(wait):
                async with session.get(stream) as r:
                    if r.status == 200:
                        return stream
                    if r.status in (423, 404, 410):
                        await asyncio.sleep(2)
                        continue
                    if r.status in (401, 403, 429):
                        txt = await r.text()
                        raise Exception(
                            f"{kind} blocked {r.status}: {txt[:100]}"
                        )
                    raise Exception(f"{kind} failed ({r.status})")
            raise Exception(f"{kind} processing timeout")

    except Exception as e:
        await app.send_message(
            LOGGER_ID,
            f"❌ **{kind.upper()} API ERROR**\n\n"
            f"🔗 `{link}`\n"
            f"⚠️ `{str(e)[:120]}`"
        )
        raise

async def download_song(link: str):
    return await _download_media(link, "song", ["mp3", "m4a", "webm"], wait=60)

async def download_video(link: str):
    return await _download_media(link, "video", ["mp4", "webm", "mkv"], wait=90)

async def check_file_size(link):
    async def get_format_info(link):
        cookie_file = cookie_txt_file()
        if not cookie_file:
            print("No cookies found. Cannot check file size.")
            return None
            
        # SECURE: Using list for subprocess execution
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_file,
            "-J",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            print(f'Error:\n{stderr.decode()}')
            return None
        return json.loads(stdout.decode())

    def parse_size(formats):
        total_size = 0
        for format in formats:
            if 'filesize' in format:
                total_size += format['filesize']
        return total_size

    info = await get_format_info(link)
    if info is None:
        return None
    
    formats = info.get('formats', [])
    if not formats:
        print("No formats found.")
        return None
    
    total_size = parse_size(formats)
    return total_size

async def shell_cmd(cmd):
    """Updated to use subprocess_exec for better security."""
    import shlex
    args = shlex.split(cmd)
    
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            if str(duration_min) == "None":
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            duration = result["duration"]
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
        except Exception as e:
            print(f"Video API failed: {e}")
        
        cookie_file = cookie_txt_file()
        if not cookie_file:
            return 0, "No cookies found. Cannot download video."
            
        # SECURE: Subprocess execution
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_file,
            "-g",
            "-f",
            "best[height<=?720][width<=?1280]",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        
        cookie_file = cookie_txt_file()
        if not cookie_file:
            return []
            
        # SECURE: Passing arguments as a list
        cmd = f"yt-dlp -i --get-id --flat-playlist --cookies {cookie_file} --playlist-end {limit} --skip-download {link}"
        playlist_data = await shell_cmd(cmd)
        
        try:
            result = [key for key in playlist_data.split("\n") if key.strip() != ""]
        except:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]

        clean_title = title.strip()
        if len(clean_title) > 14:
            clean_title = clean_title[:14].rstrip() + "...."

        track_details = {
            "title": clean_title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        cookie_file = cookie_txt_file()
        if not cookie_file:
            return [], link
            
        ytdl_opts = {"quiet": True, "cookiefile" : cookie_file}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    str(format["format"])
                except:
                    continue
                if not "dash" in str(format["format"]).lower():
                    try:
                        format["format"]
                        format["filesize"]
                        format["format_id"]
                        format["ext"]
                        format["format_note"]
                    except:
                        continue
                    formats_available.append(
                        {
                            "format": format["format"],
                            "filesize": format["filesize"],
                            "format_id": format["format_id"],
                            "ext": format["ext"],
                            "format_note": format["format_note"],
                            "yturl": link,
                        }
                    )
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(self, link, mystic, video=None, videoid=None, songaudio=None, songvideo=None, format_id=None, title=None) -> str:
        if videoid:
            link = self.base + link
        loop = asyncio.get_running_loop()

        def audio_dl():
            cookie_file = cookie_txt_file()
            if not cookie_file: raise Exception("No cookies found.")
            ydl_opts = {"format": "bestaudio/best", "outtmpl": "downloads/%(id)s.%(ext)s", "cookiefile" : cookie_file, "quiet": True}
            with yt_dlp.YoutubeDL(ydl_opts) as x:
                info = x.extract_info(link, False)
                xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                if os.path.exists(xyz): return xyz
                x.download([link])
                return xyz

        def video_dl():
            cookie_file = cookie_txt_file()
            if not cookie_file: raise Exception("No cookies found.")
            ydl_opts = {"format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])", "outtmpl": "downloads/%(id)s.%(ext)s", "cookiefile" : cookie_file, "quiet": True}
            with yt_dlp.YoutubeDL(ydl_opts) as x:
                info = x.extract_info(link, False)
                xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                if os.path.exists(xyz): return xyz
                x.download([link])
                return xyz

        if songvideo or songaudio:
            # API download
            fpath = await download_song(link)
            return fpath
        elif video:
            try:
                downloaded_file = await download_video(link)
                if downloaded_file: return downloaded_file, True
            except: pass
            
            cookie_file = cookie_txt_file()
            if not cookie_file: return None, None
                
            if await is_on_off(1):
                downloaded_file = await download_song(link)
                return downloaded_file, True
            else:
                # SECURE: Subprocess execution
                proc = await asyncio.create_subprocess_exec(
                    "yt-dlp", "--cookies", cookie_file, "-g", "-f", "best[height<=?720]", link,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                )
                stdout, _ = await proc.communicate()
                if stdout:
                    return stdout.decode().split("\n")[0], False
                else:
                   file_size = await check_file_size(link)
                   if not file_size or (file_size / (1024*1024)) > 250: return None, None
                   downloaded_file = await loop.run_in_executor(None, video_dl)
                   return downloaded_file, True
        else:
            downloaded_file = await download_song(link)
            return downloaded_file, True
