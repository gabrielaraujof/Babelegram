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


update_queue = asyncio.Queue()  # channel between web app and bot

async def webhook(request):
    """Test..
    """
    data = await request.text()
    await update_queue.put(data)  # pass update to bot
    return web.Response(body='OK'.encode('utf-8'))

async def init(loop, bot, url, port):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/abc', webhook)
    app.router.add_route('POST', '/abc', webhook)

    srv = await loop.create_server(app.make_handler(), '0.0.0.0', port)
    print("Server started ...")

    await bot.setWebhook(url)

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
    port = os.environ['BOT_WEBHOOK_PORT']

    # Creating the translator
    mstranslator = microsofttranslator.Translator(
        az_client_id, az_client_secret)
    # Creating the bot
    bot = handlers.create_bot(bot_token, mstranslator)

    # Starting the main loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop, bot, url, port))
    logging.info('Starting the bot...')
    loop.create_task(bot.messageLoop(source=update_queue))
    logging.info('Bot listening...')
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
