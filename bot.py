import os
import sys
import queue
import threading
import subprocess
import tempfile
import discord

# ===== CONFIG =====
BT_SINK = "bluez_output.0F_13_9F_39_84_62.1"
TARGET_CHANNEL_ID = 1089577790795432018
MAX_LEN = 250
VOICE_TH = "th-TH-NiwatNeural"
VOICE_EN = "en-US-GuyNeural"
DEFAULT_RATE_TH = "-25%"
DEFAULT_RATE_EN = "-10%"
# ==================

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("Missing DISCORD_TOKEN env var")
    raise SystemExit(1)

# ===== TTS QUEUE =====
tts_q: "queue.Queue[tuple[str,str,str]]" = queue.Queue()

def normalize_rate(rate: str) -> str:
    # กันกรณี rate ว่าง/None/มีช่องว่างแปลก ๆ
    if not rate:
        return "0%"
    rate = str(rate).strip()
    # ต้องลงท้ายด้วย %
    if not rate.endswith("%"):
        rate += "%"
    # ต้องมีเครื่องหมาย +/- ถ้าเป็นตัวเลขล้วน
    if rate[0].isdigit():
        rate = "+" + rate
    return rate

def tts_worker():
    while True:
        text, voice, rate = tts_q.get()
        try:
            text = (text or "").strip()
            if not text:
                continue

            rate = normalize_rate(rate)

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as f:
                # สร้างเสียง
                tts = subprocess.run(
                    [
                        sys.executable, "-m", "edge_tts",
                        "--voice", voice,
                        "--rate", rate,
                        "--text", text,
                        "--write-media", f.name,
                    ],
                    capture_output=True,
                    text=True,
                )

                if tts.returncode != 0:
                    print("edge-tts failed:", tts.stderr.strip() or tts.stdout.strip())
                    continue

                # เล่นออก Bluetooth เท่านั้น
                play = subprocess.run(
                    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "error", f.name],
                    env={**os.environ, "PULSE_SINK": BT_SINK},
                    capture_output=True,
                    text=True,
                )
                if play.returncode != 0:
                    print("ffplay failed:", play.stderr.strip() or play.stdout.strip())

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
        lower = content.lower()

        # คำสั่งเทส
        if lower.startswith("speak eng"):
            speak_text = content[9:].strip()
            voice = VOICE_EN
            rate = DEFAULT_RATE_EN
        elif lower.startswith("speak thai"):
            speak_text = content[10:].strip()
            voice = VOICE_TH
            rate = "-30%"
        else:
            speak_text = f"{message.author.display_name} พูดว่า {content}"
            voice = VOICE_TH
            rate = DEFAULT_RATE_TH

        print(speak_text)
        tts_q.put((speak_text, voice, rate))

client = Client(intents=intents)
client.run(TOKEN)
