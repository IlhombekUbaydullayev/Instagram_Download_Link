# from dotenv import load_dotenv
# load_dotenv()

# from pyrogram import Client, filters
# from pyrogram.types import Message
# import os
# import asyncio
# from yt_dlp import YoutubeDL
# from io import BytesIO
# import requests  # video yuklab olish uchun kerak

# API_ID = int(os.getenv("API_ID"))
# API_HASH = os.getenv("API_HASH")
# BOT_TOKEN = os.getenv("BOT_TOKEN")
# COOKIES_PATH = os.getenv("COOKIES_PATH")  # cookies fayl yo‘li

# app = Client("universal_video_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# # Video yuklab olish funksiyasi
# def download_video_bytes(url):
#     ydl_opts = {
#         'format': 'bestvideo+bestaudio/best',
#         'outtmpl': '-',  # to'g'ridan-to'g'ri oqim
#         'quiet': True,
#         'noplaylist': True,
#         'retries': 3,
#         'merge_output_format': 'mp4',
#         # 'cookiefile': COOKIES_PATH  # << TUZATILDI
#     }

#     with YoutubeDL(ydl_opts) as ydl:
#         try:
#             info_dict = ydl.extract_info(url, download=False)
#             video_title = info_dict.get('title', 'video')
#             formats = info_dict.get("formats", [])
#             best = next((f for f in formats if f.get("ext") == "mp4" and f.get("acodec") != "none"), None)

#             if not best or not best.get("url"):
#                 return None, None

#             video_url = best["url"]

#             # Video faylni yuklab olish
#             response = requests.get(video_url)
#             response.raise_for_status()
#             video_data = response.content
#             bio = BytesIO(video_data)
#             bio.name = f"{video_title[:30]}.mp4"
#             bio.seek(0)
#             return bio, video_title
#         except Exception as e:
#             print(f"Xatolik: {e}")
#             return None, None

# @app.on_message(filters.text & filters.private)
# async def handle_message(client: Client, message: Message):
#     url = message.text.strip()

#     if not url.startswith("http"):
#         return await message.reply("📎 Iltimos, Instagram havolasini yuboring.")

#     status = await message.reply("📥 Havola qabul qilindi. ✅\n🔄 Yuklab olish boshlanmoqda...")

#     try:
#         loop = asyncio.get_event_loop()
#         video, title = await loop.run_in_executor(None, download_video_bytes, url)

#         if video:
#             await message.reply_video(video, caption=f"✅ Yuklandi: {title}")
#             await status.delete()
#         else:
#             await status.edit("❌ Video yuklab bo‘lmadi. Havola noto‘g‘ri yoki qo‘llab-quvvatlanmaydi.")
#     except Exception as e:
#         await status.edit(f"❌ Xatolik: {e}")

# app.run()





from dotenv import load_dotenv
load_dotenv()

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import os
import asyncio
from yt_dlp import YoutubeDL
from io import BytesIO
import requests

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
COOKIES_PATH = os.getenv("COOKIES_PATH")

CHANNEL_USERNAME = "@mashina_bozor_moshinalari"  # Public kanal username
CHANNEL_LINK = f"https://t.me/{CHANNEL_USERNAME[1:]}"
CHANNEL_PHOTO_PATH = "logo.jpg"  # Kanal rasmi (lokal fayl nomi)

app = Client("universal_video_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# /start komandasi
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Message):
    await message.reply("👋 Salom! Video havolasini yuboring – biz uni yuklab beramiz.")


# YouTube video yuklab olish
def download_video_bytes(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': '-',
        'quiet': True,
        'noplaylist': True,
        'retries': 3,
        'merge_output_format': 'mp4',
    }

    if COOKIES_PATH and os.path.exists(COOKIES_PATH):
        ydl_opts['cookiefile'] = COOKIES_PATH


    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'video')
            formats = info.get("formats", [])
            best = next((f for f in formats if f.get("ext") == "mp4" and f.get("acodec") != "none"), None)
            if not best or not best.get("url"):
                return None, None
            video_url = best["url"]
            response = requests.get(video_url)
            response.raise_for_status()
            video_data = response.content
            bio = BytesIO(video_data)
            bio.name = f"{video_title[:30]}.mp4"
            bio.seek(0)
            return bio, video_title
        except Exception as e:
            print("Video yuklab olish xatosi:", e)
            return None, None


# Video yuklash va reklama yuborish
@app.on_message(filters.text & filters.private)
async def download_handler(client: Client, message: Message):
    url = message.text.strip()
    if not url.startswith("http"):
        return await message.reply("❗ Iltimos, havola yuboring.")

    wait_msg = await message.reply("📥 Yuklab olinmoqda...")
    try:
        loop = asyncio.get_event_loop()
        video, title = await loop.run_in_executor(None, download_video_bytes, url)

        if video:
            await message.reply_video(video, caption=f"✅ Yuklandi: {title}")
            await wait_msg.delete()

            # Reklama postini yuborish
            caption = (
                f"📢 <b>Bizning kanal:</b>\n"
                f"📌 <b>Nomi:</b> {CHANNEL_USERNAME}\n"
                f"🔗 <b>Link:</b> {CHANNEL_LINK}"
            )
            try:
                await message.reply_photo(photo=CHANNEL_PHOTO_PATH, caption=caption)
            except Exception as e:
                await message.reply(f"🔗 {CHANNEL_USERNAME}")

        else:
            await wait_msg.edit("❌ Video yuklab bo‘lmadi. Havola noto‘g‘ri yoki format qo‘llab-quvvatlanmaydi.")
    except Exception as e:
        await wait_msg.edit(f"❌ Xatolik: {e}")

app.run()

