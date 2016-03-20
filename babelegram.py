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

AVAILABLE_LANGUAGES = [
    # ('ar', ' Arabic'),
    # ('bg', 'Bulgarian'),
    # ('ca', 'Catalan'),
    # ('zh-CHS', 'Chinese (Simplified)'),
    # ('zh-CHT', 'Chinese (Traditional)'),
    # ('cs', 'Czech'),
    # ('da', 'Danish'),
    # ('nl', 'Dutch'),
    ('en', 'Inglês'),
    # ('et', 'Estonian'),
    # ('fi', 'Finnish'),
    ('fr', 'Francês'),
    ('de', 'Alemão'),
    # ('el', 'Greek'),
    # ('ht', 'Haitian Creole'),
    # ('he', 'Hebrew'),
    # ('hi', 'Hindi'),
    # ('hu', 'Hungarian'),
    # ('id', 'Indonesian'),
    ('it', 'Italian'),
    ('ja', 'Japanese'),
    # ('ko', 'Korean'),
    # ('lv', 'Latvian'),
    # ('lt', 'Lithuanian'),
    # ('mww', 'Hmong Daw'),
    # ('no', 'Norwegian'),
    # ('pl', 'Polish'),
    ('pt', 'Português'),
    # ('ro', 'Romanian'),
    # ('ru', 'Russian'),
    # ('sk', 'Slovak'),
    # ('sl', 'Slovenian'),
    ('es', 'Spanish'),
    # ('sv', 'Swedish'),
    # ('th', 'Thai'),
    # ('tr', 'Turkish'),
    # ('uk', 'Ukrainian'),
    # ('vi', 'Vietnamese'),
]


def default_rank(languages):
    """
    """
    return {_id: [name, 1] for _id, name in languages}

def rating_calc(item, last_ones, total):
    _id = item[0]
    name, ocur = item[1]
    rating = ocur / total
    if _id in last_ones:
        rating *= 2
    if last_ones and _id == last_ones[-1]:
        rating *= 4
    return rating


class InlineHandler(telepot.async.helper.UserHandler):

    def __init__(self, seed_tuple, timeout):
        super(InlineHandler, self).__init__(seed_tuple, timeout,
                                            flavors=['inline_query', 'chosen_inline_result'])

        # Create the Answerer, give it the compute function.
        self._answerer = telepot.async.helper.Answerer(
            self.bot, self.compute_answer)
        self._last = []
        self._language_rank = default_rank(AVAILABLE_LANGUAGES)
        self._total_ocurrences = len(self._language_rank)

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
        self._total_ocurrences += 1
        self._language_rank[result_id][1] += 1
        self._last = self._last[1:] + [result_id]

    def get_result_list(self, query_string):
        for lang_id, lang_data in sorted(self._language_rank.items(), \
                key=lambda x: rating_calc(x, self._last, self._total_ocurrences),
                reverse=True):
            lang_name = lang_data[0]
            translated_query = translator.translate(query_string, lang_id)
            yield InlineQueryResultArticle(
                type='article',
                id=lang_id,
                title=translated_query,
                description=lang_name,
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
