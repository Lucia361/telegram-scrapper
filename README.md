# Telegram Scrapper

Based on [TeleGram-Scraper by th3unkn0n.](https://github.com/th3unkn0n/TeleGram-Scraper)

This version supports secret chat DMs.

# telethon-secret-chat

Includes the latest version of [telethon-secret-chat](https://github.com/painor/telethon-secret-chat/tree/7aa0c9a3b0fa5b3288a6107958b0908b2f35814c), as of June 8th, 2021, for dealing with secret chats.

This program requires an SQLite fix not yet available on [telethon-secret-chat 0.2.4](https://pypi.org/project/telethon-secret-chat/), hosted on the Python Package Index.

# API Setup

* Go to http://my.telegram.org  and log in.
* Click on API development tools and fill the required fields.
* Insert an app name.
* Copy "api_id" and "api_hash" after creating the app.
	* They will be used during setup.

# Installation and Usage

* Install requirements for Ubuntu:

`# apt install -y git python`

`$ git clone https://github.com/klement01/telegram-scrapper.git`

`$ cd telegram-scrapper`

* Setup configuration file (using the api_id and api_hash):

`$ python setup.py -i`

* Generate user data:

`$ python setup.py -c`

* Collect contact data from Telegram groups:

`$ python scrapper.py`

* Send bulk SMS to collected data:

`$ python smsbot.py members.csv`

* Update:

`$ python setup.py -u`
