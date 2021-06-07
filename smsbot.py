#!/bin/env python3
from telethon import TelegramClient
from telethon.tl.types import InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, SessionPasswordNeededError, FloodWaitError
from telethon_secret_chat import SecretChatManager
from enum import Enum
import asyncio
import configparser
import os, sys
import csv
import random
import getpass

re="\033[1;31m"
gr="\033[1;32m"
cy="\033[1;36m"
SLEEP_TIME = 30
UPDATE_TIME = 10

class ExitCode(Enum):
    SUCCESS = 0
    NO_SETUP_ERROR = 1
    INVALID_MODE_ERROR = 2
    FLOOD_ERROR = 3    

async def start_chat_safe(manager, participant):
    while True:
        try:
            await manager.start_secret_chat(participant)
            return
        except FloodWaitError as e:
            print(re+f"[!] Rate limited for {e.seconds} seconds.")
            await asyncio.sleep(e.seconds + 3)

class main():

    def banner():
        
        print(f"""
    {re}╔╦╗{cy}┌─┐┬  ┌─┐{re}╔═╗  ╔═╗{cy}┌─┐┬─┐┌─┐┌─┐┌─┐┬─┐
    {re} ║ {cy}├┤ │  ├┤ {re}║ ╦  ╚═╗{cy}│  ├┬┘├─┤├─┘├┤ ├┬┘
    {re} ╩ {cy}└─┘┴─┘└─┘{re}╚═╝  ╚═╝{cy}└─┘┴└─┴ ┴┴  └─┘┴└─

                version : 3.1
    youtube.com/channel/UCnknCgg_3pVXS27ThLpw3xQ
            """)
            
    async def send_sms():
        # Loads configurations created by setup.
        try:
            cpass = configparser.RawConfigParser()
            cpass.read('config.data')
            api_id = cpass['cred']['id']
            api_hash = cpass['cred']['hash']
            phone = cpass['cred']['phone']
        except KeyError:
            os.system('clear')
            main.banner()
            print(re+"[!] run python3 setup.py first !!\n")
            sys.exit(ExitCode.NO_SETUP_ERROR)

        # Logs with the phone gotten from setup.
        client = TelegramClient(phone, api_id, api_hash)

        await client.connect()
        if not await client.is_user_authorized():
            client.send_code_request(phone)
            os.system('clear')
            main.banner()
            code = input(gr+'[+] Enter the code: '+re)
            try:
                client.sign_in(phone, code=code)
            except SessionPasswordNeededError as e:
                pwd_prompt = gr+'[+] Enter 2FA password: '+re
                password = getpass.getpass(prompt=pwd_prompt)
                client.sign_in(password=password)

        # Loads a file with data scrapped from a group.
        os.system('clear')
        main.banner()
        input_file = sys.argv[1]
        users = []
        with open(input_file, encoding='UTF-8') as f:
            rows = csv.reader(f,delimiter=",",lineterminator="\n")
            next(rows, None)
            for row in rows:
                user = {}
                user['username'] = row[0]
                user['id'] = int(row[1])
                user['access_hash'] = int(row[2])
                user['name'] = row[3]
                users.append(user)

        # Gets options from the user (mode, secret chat, message, etc.)
        # Mode:
        print(gr+"[1] send sms by user ID\n[2] send sms by username ")
        mode = 0
        while (mode not in (1,2)):
            try:
                mode = int(input(gr+"Input : "+re))
            except ValueError as e:
                pass

        # Secret chat:
        use_secret = input(gr+"Use secret chat [y/N]? ")
        use_secret = use_secret.lower() in "yes" and use_secret != ""
        
        # Message:
        message = input(gr+"[+] Enter Your Message : "+re)
        
        # Sets up the secret chat manager, if it is selected.
        if use_secret:
            queued_messages = dict()
            manager = SecretChatManager(client, auto_accept=True)
            async def new_chat(chat, created_by_me):
                # Runs whenever a secret chat is created.
                if created_by_me:
                    # Finds the message queued for the other participant.
                    key = chat.participant_id
                    try:
                        message = queued_messages[key]
                        del queued_messages[key]
                    except KeyError as e:
                        return
                    
                    # Tries sending the message.
                    try:
                        await manager.send_secret_message(chat, message)
                    except Exception as e:
                        print(f"Error sending message to ID {key}: {e}")
            manager.new_chat_created = new_chat

        # Iterates over the users, sending the message.
        for user in users:
            # Finds the user according to the mode.
            if mode == 2:
                if user['username'] == "":
                    continue
                receiver = await client.get_input_entity(user['username'])
            elif mode == 1:
                receiver = InputPeerUser(user['id'], user['access_hash'])
            else:
                print(re+"[!] Invalid Mode. Exiting.")
                await client.disconnect()
                sys.exit(ExitCode.INVALID_MODE_ERROR)

            # Tries sending the message to the user.
            try:
                formatted_message = message.format(user['name'])
                if use_secret:
                    print(gr+"[+] Creating chat with:", user['name'])
                    key = receiver.user_id
                    queued_messages[key] = formatted_message
                    try:
                        await start_chat_safe(manager, receiver)
                    except Exception as e:
                        print(re+"[!] Error creating chat with:", user['name'])
                        del queued_messages[key]
                else:
                    print(gr+"[+] Sending Message to:", user['name'])
                    await client.send_message(receiver, formatted_message)
                print(gr+"[+] Waiting {} seconds".format(SLEEP_TIME))
                await asyncio.sleep(SLEEP_TIME)
            except PeerFloodError:
                print(re+"[!] Getting Flood Error from telegram.\n[!] Script is stopping now.\n[!] Please try again after some time.")
                await client.disconnect()
                sys.exit(ExitCode.FLOOD_ERROR)
            except Exception as e:
                print(re+"[!] Error:", e)
                print(re+"[!] Trying to continue...")
                continue
        
        # Sends the rest of the queued messages.
        while len(queued_messages) > 0:
            print(gr+f"[+] Message left: {len(queued_messages)}")
            await asyncio.sleep(UPDATE_TIME)
        
        # Disconnects the client.
        await client.disconnect()
        print(gr+"[+] Done. Message sent to all users.")

asyncio.run(main.send_sms())
sys.exit(ExitCode.SUCCESS)
