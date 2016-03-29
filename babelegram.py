#!/usr/bin/python3
"""
An Telegram bot for translanting messages.
The bot uses the Microsoft Translator API via microsofttranslator library.
"""

import os
import logging
import asyncio
import microsofttranslator

import handlers


def main():
    """ Applicaiton entry point.
    """
    # Configuring log
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p'
    )

    # Getting environment variables
    logging.info('Loading environment variables...')
    bot_token = os.environ['BOT_TOKEN']
    az_client_id = os.environ['AZ_CLIENT_ID']
    az_client_secret = os.environ['AZ_CLIENT_SECRET']

    # Creating the translator
    mstranslator = microsofttranslator.Translator(
        az_client_id, az_client_secret)
    # Creating the bot
    bot = handlers.create_bot(bot_token, mstranslator)

    # Starting the main loop
    loop = asyncio.get_event_loop()
    logging.info('Starting the bot...')
    loop.create_task(bot.messageLoop())
    logging.info('Bot listening...')
    loop.run_forever()

if __name__ == '__main__':
    main()
