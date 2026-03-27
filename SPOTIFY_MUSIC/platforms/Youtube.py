
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
from typing import Union, Optional, Tuple
import aiohttp
import yt_dlp
from urllib.parse import urlparse, parse_qs
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch
from Spy.utils.database import is_on_off, get_api_key
from Spy.utils.formatters import time_to_seconds
import logging
import config
from config import LOGGER_ID, BASE_URL, API_KEY
from Spy import app
import socket
import ipaddress
import random  # added missing import

# Constants
DOWNLOAD_DIR = "downloads"
ALLOWED_YOUTUBE_DOMAINS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}
MAX_URL_LENGTH = 500
RATE_LIMIT_WINDOW = 10  # seconds
MAX_REQ_PER_USER = 8
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

logger = logging.getLogger(__name__)

# Simple in‑memory rate limit per user
_user_request_cache = {}

async def rate_limit_user(user_id: int) -> bool:
    now = asyncio.get_event_loop().time()
    if user_id not in _user_request_cache:
        _user_request_cache[user_id] = []
    stamps = _user_request_cache[user_id]
    # Keep only last N seconds
    stamps[:] = [t for t in stamps if t >= now - RATE_LIMIT_WINDOW]
    if len(stamps) >= MAX_REQ_PER_USER:
        return False  # rate‑limited
    stamps.append(now)
    return True

def is_ip_unsafe(ip: str) -> bool:
    """Check if IP is private, loopback, link‑local, or multicast."""
    try:
        ip_obj = ipaddress.ip_address(ip)
        return (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_multicast
        )
    except Exception:
        return True

def resolve_all_ips(hostname: str) -> Optional[list]:
    """Resolve all IPs for a hostname; return None if any DNS error."""
    try:
        addrinfos = socket.getaddrinfo(hostname, None)
        ips = list({addr[4][0] for addr in addrinfos})
        return ips
    except Exception:
        return None

def is_host_safe(hostname: str) -> bool:
    """Check host: all resolved IPs are safe and no DNS error."""
    if not hostname:
        return False
    ips = resolve_all_ips(hostname)
    if not ips:
        return False
    return all(not is_ip_unsafe(ip) for ip in ips)

def is_safe_youtube_domain(host: str) -> bool:
    """Strict YouTube domain: exact match or subdomain."""
    if not host:
        return False
    host = host.lower().rstrip(".")
    for domain in ALLOWED_YOUTUBE_DOMAINS:
        if host == domain or host.endswith(f".{domain}"):
            return True
    return False

def is_safe_youtube_url(url: str) -> bool:
    if not isinstance(url, str) or len(url) > MAX_URL_LENGTH or not url.strip():
        return False
    try:
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        host = parsed.hostname
        if scheme not in ("http", "https") or not host:
            return False
        if not is_safe_youtube_domain(host) or not is_host_safe(host):
            return False
        return True
    except Exception:
        return False

def is_safe_stream_url(url: str) -> bool:
    if not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        host = parsed.hostname
        if scheme not in ("http", "https") or not host:
            return False
        if not is_host_safe(host):
            return False
        return True
    except Exception:
        return False

def extract_video_id(url: str) -> Optional[str]:
    if not is_safe_youtube_url(url):
        return None
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    if parsed.hostname == "youtu.be":
        vid = path.lstrip("/")
    else:
        query = parse_qs(parsed.query)
        vid = query.get("v", [""])[0]
    if vid and len(vid) == 11:
        return vid
    return None

def cookie_txt_file() -> Optional[str]:
    cookie_dir = f"{os.getcwd()}/cookies"
    if not os.path.exists(cookie_dir):
        return None
    cookies_files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]
    if not cookies_files:
        return None
    return os.path.join(cookie_dir, random.choice(cookies_files))

async def safe_api_request(
    session: aiohttp.ClientSession,
    url: str,
    max_retries: int = 3,
    user_id: Optional[int] = None,
) -> Optional[dict]:
    timeout = aiohttp.ClientTimeout(total=12)

    if user_id is not None and not await rate_limit_user(user_id):
        logger.warning(f"Rate‑limited user {user_id}")
        return None

    for attempt in range(max_retries):
        parsed = urlparse(url)
        if parsed.hostname and not is_host_safe(parsed.hostname):
            logger.error("unsafe API URL host")
            return None

        try:
            async with session.get(
                url,
                timeout=timeout,
                allow_redirects=False,  # manual redirect pinning is safer
            ) as resp:
                if resp.status in (301, 302, 303, 307, 308):
                    location = resp.headers.get("Location")
                    if not location:
                        return None
                    redir = urlparse(location)
                    redir_host = redir.hostname
                    if not redir_host or not is_host_safe(redir_host):
                        logger.error("Unsafe redirect location")
                        return None
                    # follow redirect once if safe
                    async with session.get(
                        location, timeout=timeout, allow_redirects=False
                    ) as redir_resp:
                        if redir_resp.status == 200:
                            return await redir_resp.json()
                        return None
                if resp.status == 200:
                    return await resp.json()
                elif resp.status in (423, 404, 410):
                    await asyncio.sleep(2 ** attempt)
                    continue
                elif resp.status in (401, 403, 429):
                    text = await resp.text()
                    logger.error(f"API blocked {resp.status}: {text[:100]}")
                    return None
                else:
                    logger.warning(f"API failed {resp.status}")
                    return None
        except asyncio.TimeoutError:
            logger.warning(f"API timeout attempt {attempt + 1}")
            await asyncio.sleep(2 ** attempt)
        except Exception as e:
            logger.error(f"API request error: {e}")
            await asyncio.sleep(2 ** attempt)
    return None

async def fallback_download(link: str, kind: str) -> Optional[str]:
    if not is_safe_youtube_url(link):
        return None

    cookie_file = cookie_txt_file()
    if not cookie_file:
        logger.warning("No cookies for yt‑dlp fallback")
        cookie_file = None

    try:
        if kind == "song":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
                "quiet": True,
                "cookiefile": cookie_file,
                "noplaylist": True,
                "restrictfilenames": True,
                "nocheckcertificate": False,
            }
        else:
            ydl_opts = {
                "format": "best[height<=720][width<=1280]",
                "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
                "quiet": True,
                "cookiefile": cookie_file,
                "noplaylist": True,
                "restrictfilenames": True,
                "nocheckcertificate": False,
            }

        ydl = yt_dlp.YoutubeDL(ydl_opts)
        info = await asyncio.get_event_loop().run_in_executor(
            None, lambda: ydl.extract_info(link, download=False)
        )
        output_path = ydl.prepare_filename(info)
        if os.path.exists(output_path):
            return output_path

        await asyncio.get_event_loop().run_in_executor(
            None, lambda: ydl.download([link])
        )
        return output_path
    except Exception as e:
        logger.error(f"yt‑dlp fallback failed: {e}")
        return None

async def _download_media(
    link: str, kind: str, exts: list[str], vid: str, max_wait: int = 60
) -> Optional[str]:
    if not is_safe_youtube_url(link):
        raise ValueError("Invalid YouTube URL")

    for ext in exts:
        path = f"{DOWNLOAD_DIR}/{vid}.{ext}"
        if os.path.exists(path):
            return path

    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        api_url = f"{BASE_URL}/api/{kind}?query={vid}&eq=pro&api={API_KEY}"
        res = await safe_api_request(session, api_url)
        if not res:
            logger.warning("API unavailable; falling back to yt‑dlp")
            return await fallback_download(link, kind)

        stream = res.get("stream")
        media_type = res.get("type")

        if not stream:
            logger.error("API returned no stream URL")
            return await fallback_download(link, kind)

        if not is_safe_stream_url(stream):
            logger.error("API returned unsafe stream URL")
            return await fallback_download(link, kind)

        if media_type == "live":
            return stream

        for _ in range(max_wait):
            parsed = urlparse(stream)
            if parsed.hostname and not is_host_safe(parsed.hostname):
                logger.error("Unsafe stream URL after redirect")
                return await fallback_download(link, kind)

            async with session.get(
                stream,
                timeout=aiohttp.ClientTimeout(total=5),
                allow_redirects=False,
            ) as r:
                if r.status == 200:
                    return stream
                if r.status in (423, 404, 410):
                    await asyncio.sleep(2)
                    continue
                if r.status in (401, 403, 429):
                    txt = await r.text()
                    raise Exception(f"{kind} blocked {r.status}: {txt[:100]}")
                raise Exception(f"{kind} failed ({r.status})")

        raise Exception(f"{kind} processing timeout")

async def download_song(link: str) -> Optional[str]:
    if not is_safe_youtube_url(link):
        raise ValueError("Invalid YouTube URL")
    vid = extract_video_id(link)
    if not vid:
        raise ValueError("Unable to extract YouTube video ID")
    return await _download_media(link, "song", ["mp3", "m4a", "webm"], vid, max_wait=60)

async def download_video(link: str) -> Optional[str]:
    if not is_safe_youtube_url(link):
        raise ValueError("Invalid YouTube URL")
    vid = extract_video_id(link)
    if not vid:
        raise ValueError("Unable to extract YouTube video ID")
    return await _download_media(link, "video", ["mp4", "webm", "mkv"], vid, max_wait=90)

async def check_file_size(link: str) -> Optional[int]:
    if not is_safe_youtube_url(link):
        return None

    cookie_file = cookie_txt_file()
    if not cookie_file:
        return None

    try:
        proc = await asyncio.create_subprocess_exec(
            "yt‑dlp",
            "--cookies",
            cookie_file,
            "-J",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
        if proc.returncode != 0:
            logger.error(f"Size check process failed: {stderr.decode()}")
            return None

        info = json.loads(stdout.decode())
        formats = info.get("formats", [])
        total_size = sum(
            fmt["filesize"]
            for fmt in formats
            if "filesize" in fmt and fmt["filesize"]
        )
        return total_size
    except Exception as e:
        logger.error(f"File size check error: {e}")
        return None

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None) -> bool:
        if videoid:
            link = self.base + str(videoid)
        return is_safe_youtube_url(link)

    async def url(self, message_1: Message) -> Optional[str]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)

        for message in messages:
            entities = (message.entities or []) + (message.caption_entities or [])
            for entity in entities:
                if entity.type == MessageEntityType.URL:
                    text = (message.text or message.caption or "")
                    offset = entity.offset
                    length = entity.length
                    candidate = text[offset : offset + length]
                    if is_safe_youtube_url(candidate):
                        return candidate
                elif entity.type == MessageEntityType.TEXT_LINK:
                    if is_safe_youtube_url(entity.url):
                        return entity.url
        return None

    async def details(
        self, link: str, videoid: Union[bool, str] = None
    ) -> Tuple[str, str, int, str, str]:
        if videoid:
            link = self.base + str(videoid)
        if not is_safe_youtube_url(link):
            raise ValueError("Invalid YouTube URL")
        link = link.split("&")[0]

        results = VideosSearch(link, limit=1)
        raw = (await results.next()).get("result", [])
        if not raw:
            raise ValueError("No video result")
        result = raw[0]
        title = result["title"]
        duration_min = result["duration"]
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        vidid = result["id"]
        duration_sec = 0 if str(duration_min) == "None" else int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None) -> str:
        title, _, _, _, _ = await self.details(link, videoid)
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None) -> str:
        _, duration_min, _, _, _ = await self.details(link, videoid)
        return duration_min

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None) -> str:
        _, _, _, thumbnail, _ = await self.details(link, videoid)
        return thumbnail

    async def video(
        self, link: str, videoid: Union[bool, str] = None
    ) -> Tuple[int, Optional[str]]:
        if videoid:
            link = self.base + str(videoid)
        if not is_safe_youtube_url(link):
            return 0, "Invalid YouTube URL"
        link = link.split("&")[0]

        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
        except Exception as e:
            logger.error(f"Video API failed: {e}")

        cookie_file = cookie_txt_file()
        if not cookie_file:
            return 0, "No cookies found. Cannot download video."

        try:
            proc = await asyncio.create_subprocess_exec(
                "yt‑dlp",
                "--cookies",
                cookie_file,
                "-g",
                "-f",
                "best[height<=?720][width<=?1280]",
                link,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
            if proc.returncode == 0 and stdout:
                return 1, stdout.decode().split("\n")[0]
            return 0, stderr.decode()
        except Exception as e:
            return 0, f"Download failed: {str(e)}"

    async def playlist(
        self, link: str, limit: int, user_id: int, videoid: Union[bool, str] = None
    ) -> list:
        if videoid:
            link = self.listbase + str(videoid)
        if not is_safe_youtube_url(link):
            return []
        link = link.split("&")[0]

        cookie_file = cookie_txt_file()
        if not cookie_file:
            return []

        try:
            proc = await asyncio.create_subprocess_exec(
                "yt‑dlp",
                "-i",
                "--get-id",
                "--flat-playlist",
                "--cookies",
                cookie_file,
                "--playlist-end",
                str(limit),
                "--skip-download",
                link,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
            result = [key.strip() for key in stdout.decode().split("\n") if key.strip()]
            return result
        except Exception:
            return []

    async def track(
        self, link: str, videoid: Union[bool, str] = None
    ) -> Tuple[dict, str]:
        title, duration_min, _, thumbnail, vidid = await self.details(link, videoid)
        yturl = f"https://www.youtube.com/watch?v={vidid}"
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

    async def formats(
        self, link: str, videoid: Union[bool, str] = None
    ) -> Tuple[list, str]:
        if videoid:
            link = self.base + str(videoid)
        if not is_safe_youtube_url(link):
            return [], link
        link = link.split("&")[0]

        cookie_file = cookie_txt_file()
        if not cookie_file:
