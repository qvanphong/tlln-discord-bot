# TLLN Discord Bot!

**Features:**
---
- Get user avatar or other user avatar
- Send random stoic quotes.
- Send random Carl Jung quotes.
- Send full size image of emoji
- Calculate sleep and wake time.
- Check coins prices.
- Convert amount of 2 different coin. (eg: 1 NEO = 5 GAS)
- Alert coin pump or dump. (Customize your own by edit my binance_price.py)
- Word cross game, Caro game (gomoku in Vietnamese)
- Some funny commands...

**Installation**
---
Clone this repository.

    git clone https://github.com/qvanphong/ttln-discord-bot.git

Create `.env` file or rename `.env_example` to `.env`
Fill these important keys:

    Token # Your discord token
    CMCKey # Coinmarketcap token
    BinanceWssURL # Binance websocket url
    ServerId # Your server ID that bot working on

Install requirements library:

    pip install -r requirements.txt

If you are going to use official Discord Bot, install discord.py:

    pip install discord.py

Run:

    python3 selfbot.py
