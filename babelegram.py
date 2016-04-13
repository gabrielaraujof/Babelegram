#!/usr/bin/python3
"""
An Telegram bot for translanting messages.
The bot uses the Microsoft Translator API via microsofttranslator library.
"""

import os
import logging
import asyncio
from aiohttp import web
import microsofttranslator

import handlers


async def init(loop, bot, queue, url, port):
    """ Starts server and plugs-in the bot."""

    async def webhook(request):
        """ Handles all income messages from Telegram API"""
        data = await request.text()
        await queue.put(data)  # pass update to bot
        return web.Response(body='OK'.encode('utf-8'))

    # TODO passes the webhook url path by environment variable
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/abc', webhook)
    app.router.add_route('POST', '/abc', webhook)

    logging.info('Starting the server...')
    srv = await loop.create_server(app.make_handler(), '', port)
    logging.info('Server started...')
    await bot.setWebhook(url)  # sets the url for webhook

    return srv


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
    url = os.environ['BOT_WEBHOOK_URL']
    port = os.environ['PORT']

    # Creating the translator
    logging.info('Creating translator...')
    mstranslator = microsofttranslator.Translator(
        az_client_id, az_client_secret)
    # Creating the bot
    logging.info('Creating the bot...')
    bot = handlers.create_bot(bot_token, mstranslator)

    # Starting the main loop
    loop = asyncio.get_event_loop()
    message_queue = asyncio.Queue()  # channel between web app and bot
    loop.run_until_complete(init(loop, bot, message_queue, url, port))
    logging.info('Starting the bot...')
    loop.create_task(bot.messageLoop(source=message_queue))
    logging.info('Bot listening...')
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
