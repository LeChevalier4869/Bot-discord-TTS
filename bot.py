import os
import queue
import threading
import subprocess
import tempfile
import discord

# ===== CONFIG =====
BT_SINK = "bluez_output.0F_13_9F_39_84_62.1"
TARGET_CHANNEL_ID = 1089577790795432018
#VOICE_TH = "th-TH-PremwadeeNeural"
VOICE_TH = "th-TH-NiwatNeural"
MAX_LEN = 200
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

class Client(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # อ่านเฉพาะห้องที่กำหนด
        if message.channel.id != TARGET_CHANNEL_ID:
            return

        content = (message.content or "").strip()
        if not content:
            return

        content = content.replace("\n", " ")
        content = content[:MAX_LEN]

        text = f"{message.author.display_name} พูดว่า {content}"
        print(text)

        tts_q.put(text)

client = Client(intents=intents)
client.run(TOKEN)
