import os
import queue
import threading
import subprocess
import tempfile
import discord

# ===== CONFIG =====
BT_SINK = "bluez_output.0F_13_9F_39_84_62.1"
TARGET_CHANNEL_ID = 1089577790795432018
MAX_LEN = 250
# ==================

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("Missing DISCORD_TOKEN env var")
    raise SystemExit(1)

# ===== TTS QUEUE =====
tts_q = queue.Queue()

def tts_worker():
    while True:
        text, voice, rate = tts_q.get()
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
                        voice,
                        "--rate",
                        rate,
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

        if message.channel.id != TARGET_CHANNEL_ID:
            return

        content = (message.content or "").strip()
        if not content:
            return

        content = content.replace("\n", " ")
        content = content[:MAX_LEN]

        # ===== COMMAND MODE =====
        lower = content.lower()

        if lower.startswith("speak eng"):
            text = content[9:].strip()
            voice = "en-US-GuyNeural"
            rate = "-10%"   # อังกฤษช้าลงเล็กน้อย

        elif lower.startswith("speak thai"):
            text = content[10:].strip()
            voice = "th-TH-NiwatNeural"
            rate = "-30%"   # ไทยช้าลงชัด ๆ

        else:
            text = f"{message.author.display_name} พูดว่า {content}"
            voice = "th-TH-NiwatNeural"
            rate = "-25%"   # ค่า default ไทย

        print(text)
        tts_q.put((text, voice, rate))

client = Client(intents=intents)
client.run(TOKEN)
