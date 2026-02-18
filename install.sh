#!/bin/bash

# Discord TTS Bot Auto-Install Script
# สำหรับติดตั้ง bot ให้รันอัตโนมัติเมื่อเปิดเครื่อง

set -e

echo "🤖 Discord TTS Bot Auto-Install Script"
echo "====================================="

# หา user ปัจจุบัน
CURRENT_USER=$(whoami)
HOME_DIR=$(eval echo ~$CURRENT_USER)

# สร้าง symlink จากปัจจุบันไป home directory (ถ้ายังไม่มี)
if [ ! -d "$HOME_DIR/discord-tts-bot" ]; then
    echo "📁 Creating symlink to $HOME_DIR/discord-tts-bot..."
    ln -sf "$(pwd)" "$HOME_DIR/discord-tts-bot"
fi

# แก้ไข service file ให้ใช้ user ปัจจุบัน
echo "🔧 Configuring service for user: $CURRENT_USER"
sed "s/%i/$CURRENT_USER/g; s|%h|$HOME_DIR|g" discord-tts-bot.service > /tmp/discord-tts-user.service

# ติดตั้ง service
echo "📦 Installing systemd service..."
sudo cp /tmp/discord-tts-user.service /etc/systemd/system/discord-tts-bot.service
sudo systemctl daemon-reload
sudo systemctl enable discord-tts-bot.service

# ตรวจสอบว่ามี .env ไหม
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Please create .env file with DISCORD_TOKEN"
    echo "   Example: DISCORD_TOKEN=your_bot_token_here"
    echo ""
    echo "Press Enter to continue anyway (service will fail without token)..."
    read -r
fi

# เริ่ม service
echo "🚀 Starting Discord TTS Bot service..."
sudo systemctl start discord-tts-bot.service

# ตรวจสอบสถานะ
echo ""
echo "✅ Installation complete!"
echo "📊 Service status:"
sudo systemctl status discord-tts-bot.service --no-pager -l

echo ""
echo "📝 Useful commands:"
echo "  View logs:     sudo journalctl -u discord-tts-bot.service -f"
echo "  Restart:       sudo systemctl restart discord-tts-bot.service"
echo "  Stop:          sudo systemctl stop discord-tts-bot.service"
echo "  Disable:       sudo systemctl disable discord-tts-bot.service"

echo ""
echo "🎉 Bot will auto-start on boot!"
