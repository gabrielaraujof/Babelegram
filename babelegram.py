#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
An Telegram bot for translanting messages.
The bot uses the Microsoft Translator API via microsofttranslator library.
"""

import os
import asyncio
import microsofttranslator

import handlers

if __name__ == '__main__':
    # Getting environment variables
    BOT_TOKEN = os.environ['BOT_TOKEN']
    AZ_CLIENT_ID = os.environ['AZ_CLIENT_ID']
    AZ_CLIENT_SECRET = os.environ['AZ_CLIENT_SECRET']

    # Creating the translator
    MSTRANSLATOR = microsofttranslator.Translator(AZ_CLIENT_ID, AZ_CLIENT_SECRET)
    # Creating the bot
    BOT = handlers.create_bot(BOT_TOKEN, MSTRANSLATOR)

    # Starting the main loop
    LOOP = asyncio.get_event_loop()
    LOOP.create_task(BOT.messageLoop())
    print('Listening ...')
    LOOP.run_forever()
