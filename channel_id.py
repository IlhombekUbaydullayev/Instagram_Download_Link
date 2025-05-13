from dotenv import load_dotenv
load_dotenv()

from pyrogram import Client, filters
from pyrogram.types import Message
import os
import asyncio
from yt_dlp import YoutubeDL
from io import BytesIO
import requests  # video yuklab olish uchun kerak

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
COOKIES_PATH = os.getenv("COOKIES_PATH")  # cookies fayl yo‘li

app = Client("universal_video_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Video yuklab olish funksiyasi
def download_video_bytes(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': '-',  # to'g'ridan-to'g'ri oqim
        'quiet': True,
        'noplaylist': True,
        'retries': 3,
        'merge_output_format': 'mp4',
        # 'cookiefile': COOKIES_PATH  # << TUZATILDI
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', 'video')
            formats = info_dict.get("formats", [])
            best = next((f for f in formats if f.get("ext") == "mp4" and f.get("acodec") != "none"), None)

            if not best or not best.get("url"):
                return None, None

            video_url = best["url"]

            # Video faylni yuklab olish
            response = requests.get(video_url)
            response.raise_for_status()
            video_data = response.content
            bio = BytesIO(video_data)
            bio.name = f"{video_title[:30]}.mp4"
            bio.seek(0)
            return bio, video_title
        except Exception as e:
            print(f"Xatolik: {e}")
            return None, None

@app.on_message(filters.text & filters.private)
async def handle_message(client: Client, message: Message):
    url = message.text.strip()

    if not url.startswith("http"):
        return await message.reply("📎 Iltimos, Instagram havolasini yuboring.")

    status = await message.reply("📥 Havola qabul qilindi. ✅\n🔄 Yuklab olish boshlanmoqda...")

    try:
        loop = asyncio.get_event_loop()
        video, title = await loop.run_in_executor(None, download_video_bytes, url)

        if video:
            await message.reply_video(video, caption=f"✅ Yuklandi: {title}")
            await status.delete()
        else:
            await status.edit("❌ Video yuklab bo‘lmadi. Havola noto‘g‘ri yoki qo‘llab-quvvatlanmaydi.")
    except Exception as e:
        await status.edit(f"❌ Xatolik: {e}")

app.run()
