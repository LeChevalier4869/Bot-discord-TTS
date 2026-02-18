import os
import queue
import subprocess
import tempfile
import threading

# ===== CONFIG =====
BT_SINK = "bluez_output.0F_13_9F_39_84_62.1"
#VOICE_TH = "th-TH-PremwadeeNeural"
VOICE_TH = "th-TH-NiwatNeural"
MAX_LEN = 200
# ==================

tts_q = queue.Queue()


def _tts_worker():
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


threading.Thread(target=_tts_worker, daemon=True).start()


def speak(text: str):
    """ส่งข้อความเข้า TTS queue"""
    text = (text or "").strip()
    if text:
        print(f"[TTS] {text}")
        tts_q.put(text)
