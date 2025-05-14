from aiogram import Bot
from aiogram.enums.chat_member_status import ChatMemberStatus

async def check_user_in_channel(bot: Bot, user_id: int, channel_username: str) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_username, user_id=user_id)
        print("✅ get_chat_member natijasi:", member)
        print("📌 Status:", member.status)
        return member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR  
        ]
    except Exception as e:
        print("❌ Xatolik yuz berdi:", e)
        return False
