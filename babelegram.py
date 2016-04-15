#!/usr/bin/python3
"""
An Telegram bot for translating messages.
The bot uses the Microsoft Translator API via microsofttranslator library.
"""

import os
import logging
import asyncio
from aiohttp import web
import microsofttranslator

import handlers


async def server_init(loop, bot, queue, base_url, url_path, port):
    """ Starts server and plugs-in the bot."""

    async def webhook(request):
        """ Handles all income messages from Telegram API"""
        data = await request.text()
        await queue.put(data)  # pass update to bot
        return web.Response(body='OK'.encode('utf-8'))

    app = web.Application(loop=loop)
    app.router.add_route('GET', url_path, webhook)
    app.router.add_route('POST', url_path, webhook)

    logging.info('Starting the server...')
    srv = await loop.create_server(app.make_handler(), '', port)
    logging.info('Server started...')
    # sets the url for webhook
    await bot.setWebhook(base_url + url_path)

    return srv


def main():
    """ Application entry point.
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
    logging.info('Creating translator...')
    mstranslator = microsofttranslator.Translator(
        az_client_id, az_client_secret)
    # Creating the bot
    logging.info('Creating the bot...')
    bot = handlers.create_bot(bot_token, mstranslator)

    # Starting the main loop
    loop = asyncio.get_event_loop()

    if os.environ.get('IS_PROD'):
        url = os.environ['BOT_BASE_URL']
        url_path = os.environ['BOT_WEBHOOK_PATH']
        port = os.environ['PORT']

        message_queue = asyncio.Queue()  # channel between web app and bot
        server_task = server_init(loop, bot, message_queue, url, url_path, port)
        loop.run_until_complete(server_task)
        logging.info('Starting the bot...')
        loop.create_task(bot.messageLoop(source=message_queue))
    else:
        logging.info('Deleting webhook')
        loop.create_task(bot.setWebhook())  # deleting the webhook
        logging.info('Starting the bot...')
        loop.create_task(bot.messageLoop())

    try:
        loop.run_forever()
        logging.info('Bot listening...')
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
