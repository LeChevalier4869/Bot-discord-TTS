import os
import queue
import threading
import subprocess
import tempfile
import re
import discord

# ===== CONFIG =====
BT_SINK = "bluez_output.0F_13_9F_39_84_62.1"
TARGET_CHANNEL_IDS = {
    1089577790795432018,
    1136998778411425823
}
#VOICE_TH = "th-TH-PremwadeeNeural"
VOICE_TH = "th-TH-NiwatNeural"
MAX_LEN = 200
OWNER_ID = 408988653772341248
# ==================

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise SystemExit("Missing DISCORD_TOKEN env var")

# ===== TTS QUEUE =====
tts_q = queue.Queue()

def tts_worker():
    while True:
        text = tts_q.get()
        try:
            text = text.strip()
            if not text:
                continue

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as f:
                subprocess.run(
                    [
                        "python",
                        "-m",
                        "edge_tts",
                        "--voice",
                        VOICE_TH,
                        "--text",
                        text,
                        "--write-media",
                        f.name,
                    ],
                    check=False,
                )

                subprocess.run(
                    [
                        "ffplay",
                        "-nodisp",
                        "-autoexit",
                        "-loglevel",
                        "error",
                        f.name,
                    ],
                    env={**os.environ, "PULSE_SINK": BT_SINK},
                    check=False,
                )
        finally:
            tts_q.task_done()

threading.Thread(target=tts_worker, daemon=True).start()

# ===== DISCORD BOT =====
intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True
intents.members = True

class Client(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        if message.author.bot or message.author.id == OWNER_ID:
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

        tts_q.put(text)

client = Client(intents=intents)
client.run(TOKEN)
