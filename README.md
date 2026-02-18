# Discord TTS Bot

Discord bot ที่อ่านข้อความและส่งเสียง TTS (Text-to-Speech)

## การติดตั้ง

### วิธีที่ 1: รันแบบธรรมดา
```bash
./run.sh
```

### วิธีที่ 2: ติดตั้งให้รันอัตโนมัติ (แนะนำ)
```bash
./install.sh
```

Script จะ:
- สร้าง symlink ไปยัง home directory
- ติดตั้ง systemd service
- เปิดใช้งาน auto-start
- เริ่ม bot ทันที

## คำสั่งควบคุม

```bash
# ดูสถานะ
sudo systemctl status discord-tts-bot.service

# ดู logs
sudo journalctl -u discord-tts-bot.service -f

# รีสตาร์ท
sudo systemctl restart discord-tts-bot.service

# หยุด
sudo systemctl stop discord-tts-bot.service

# ปิด auto-start
sudo systemctl disable discord-tts-bot.service
```

## ต้องการ

- Python 3.8+
- Discord bot token (ใน `.env` ไฟล์)
- edge-tts (สำหรับ TTS)

## การตั้งค่า

สร้าง `.env` ไฟล์:

```bash
# จำเป็นต้องมี
DISCORD_TOKEN=your_bot_token_here

# ตัวเลือก (จะมีค่า default ถ้าไม่ระบุ)
OWNER_ID=408988653772341241
MAX_LEN=200
TARGET_CHANNEL_IDS=1089577790795432018,1136998778411425823
```

### คำอธิบายตัวแปร:

- **DISCORD_TOKEN**: Bot token (จำเป็น)
- **OWNER_ID**: User ID ของเจ้าของบอท (default: 408988653772341241)
- **MAX_LEN**: ความยาวข้อความสูงสุด (default: 200)
- **TARGET_CHANNEL_IDS**: Channel IDs ที่ให้บอททำงาน คั่นด้วย comma (default: 1089577790795432018,1136998778411425823)

### วิธีหา Channel ID:
1. คลิกขวาที่ channel ใน Discord
2. เลือก "Copy Channel ID"
3. ถ้าไม่เห็น "Copy Channel ID" → Discord Settings → Advanced → Developer Mode ON
