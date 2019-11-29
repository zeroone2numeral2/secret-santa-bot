# Secret Santa Telegram bot 🤫🎅🏼

Extremely simple and straightforward Telegram bot to organize a [Secret Santa](http://secret-santa.urbanup.com/4845681) in a Telegram group chat.

I was pretty shocked to discover there's not a single basic implementation of a Secret Santa bot on Telegram, so I've decided to spend a couple of hours on this small bot. I've tried to keep it as simple and gimmick-free as possible. The idea is simple: add the bot to a group chat, ask the members to start it, and start the Secret Santas draw. Easy as that.

### A bit of background

This was actually suggested by a friend of mine, who was wondering whether there was a way to do a Secret Santa draw without having all your friends to gather at the same place - which, for various reasons, might be an impossible task sometimes.

If you have a Telegram chat with your friends already set up, a Telegram bot is a pretty handy solution to solve the problem.

To avoid headaches I've decided to go down the easiest path possible: since the [Telegram bot API](https://core.telegram.org/bots/api) doesn't allow bots to fetch the members list of a chat, I went for [Pyrogram](https://docs.pyrogram.org/), which is a Python [MTProto](https://core.telegram.org/mtproto) client that allows to log-in as a bot and communicate with the servers via TCP, bypassing Telegram's HTTP API. Authorizing your bot account that way, Telegram will allow you to use some API methods which are usually not available through the bot API - such as fetching a chat's members list. Which is why this bot doesn't need to store any information to send Secret Santa matches to the participants. Thanks, Pyrogram!

### Installation

The is no installation setup/packaging, it's just a Python script you run as you prefer. I'm personally running it using [supervisor](http://supervisord.org) in a virtualenv

1. rename `config.example.toml` to `config.toml`
2. open `config.toml` and edit `pyrogram`'s `api_id` and `api_hash` according to [the docs](https://docs.pyrogram.org/intro/quickstart#get-pyrogram-real-fast), and set your bot's `token`
3. install the requirements via `pip install -r requirements.txt`
4. run the bot with `python main.py`

### The bot

I have an instance running at [@secretsantamatcherbot](https://t.me/secretsantamatcherbot)
