import os
import re
import discord
import tts_engine

# ===== CONFIG =====
TARGET_CHANNEL_IDS = {
    1089577790795432018,
    1136998778411425823
}
MAX_LEN = 200
OWNER_ID = 408988653772341241
# ==================

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise SystemExit("Missing DISCORD_TOKEN env var")

# ===== DISCORD BOT =====
intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True
intents.members = True

class Client(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        if message.author.id == OWNER_ID:
            return

        # ข้ามข้อความจาก bot
        if message.author.bot:
            return

        # อ่านเฉพาะห้องที่กำหนด
        if message.channel.id not in TARGET_CHANNEL_IDS:
            return

        content = (message.content or "").strip()
        if not content:
            return

        content = content.replace("\n", " ")

        # สร้างรายชื่อคนที่ถูก mention
        mentioned = [u.display_name for u in message.mentions]
        mention_text = f" ... มีการอ้างถึง {', '.join(mentioned)}" if mentioned else ""

        # ลบ mention ออกจากเนื้อหา
        content = re.sub(r"<@[!&]?\d+>", "", content)
        content = re.sub(r"<#\d+>", "", content)
        content = content.strip()
        content = content[:MAX_LEN]

        text = f"ข้อความจาก {message.author.display_name}{mention_text} ... {content}"
        print(text)

        tts_engine.speak(text)

client = Client(intents=intents)
client.run(TOKEN)
