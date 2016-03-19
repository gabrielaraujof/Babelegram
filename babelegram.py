#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
An Telegram bot for translanting messages.
The bot uses the Microsoft Translator API via microsofttranslator library.
"""

import os
import asyncio
import telepot
from telepot.async.delegate import per_inline_from_id, create_open
from telepot.namedtuple import InlineQueryResultArticle
import microsofttranslator as mstranslator

TOP_LANGUAGES = [
    ('en', 'Inglês'),
    ('es', 'Espanhol'),
    ('fr', 'Francês'),
    ('de', 'Alemão')
]


class InlineHandler(telepot.async.helper.UserHandler):
    def __init__(self, seed_tuple, timeout):
        super(InlineHandler, self).__init__(seed_tuple, timeout,
                                            flavors=['inline_query', 'chosen_inline_result'])

        # Create the Answerer, give it the compute function.
        self._answerer = telepot.async.helper.Answerer(
            self.bot, self.compute_answer)

    @asyncio.coroutine
    def compute_answer(self, inline_query):
        query_id, from_id, query_string = telepot.glance(
            inline_query, flavor='inline_query')
        if not query_string:
            return []

        return list(self.get_result_list(query_string))

    def on_inline_query(self, msg):
        # Just dump inline query to answerer
        self._answerer.answer(msg)

    def on_chosen_inline_result(self, msg):
        result_id, from_id, query_string = telepot.glance(
            msg, flavor='chosen_inline_result')
        print(self.id, ':', 'Chosen Inline Result:',
              result_id, from_id, query_string)

    def get_result_list(self, query_string):
        for lang_id, lang_name in TOP_LANGUAGES:
            translated_query = translator.translate(query_string, lang_id)
            yield InlineQueryResultArticle(
                type='article',
                id=lang_id,
                title=lang_name,
                description=translated_query,
                message_text=translated_query
            )

# Getting environment variables
BOT_TOKEN = os.environ['BOT_TOKEN']
AZ_CLIENT_ID = os.environ['AZ_CLIENT_ID']
AZ_CLIENT_SECRET = os.environ['AZ_CLIENT_SECRET']
# Starting the translator
translator = mstranslator.Translator(AZ_CLIENT_ID, AZ_CLIENT_SECRET)
# Starting the bot
bot = telepot.async.DelegatorBot(BOT_TOKEN, [
    (per_inline_from_id(), create_open(InlineHandler, timeout=60)),
])
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop())
print('Listening ...')

loop.run_forever()
