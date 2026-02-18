#!/usr/bin/env bash
source venv/bin/activate
set -a; source .env; set +a

# รัน Discord bot (foreground)
python -u bot.py
