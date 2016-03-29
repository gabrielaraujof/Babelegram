#!/usr/bin/python3
"""
Bot engine handlers.
"""

import logging
from collections import namedtuple, deque

import telepot
from telepot.namedtuple import InlineQueryResultArticle
from telepot.async.delegate import per_inline_from_id, create_open

import helpers


UserSettings = namedtuple('UserSettings',
                          'rank, ocurrences, total_ocurrences, last_ocurrences, page_size')


def create_bot(token, translator):
    """ Create a new bot instance
    """
    return telepot.async.DelegatorBot(token, [
        (per_inline_from_id(), create_open(
            BabelegramHandler, timeout=60, translator=translator)),
    ])


class BabelegramHandler(telepot.async.helper.UserHandler):
    """ Bot message handler.
    """

    def __init__(self, seed_tuple, timeout, translator):
        super(BabelegramHandler, self).__init__(
            seed_tuple, timeout,
            flavors=['inline_query', 'chosen_inline_result']
        )
        # Init instance variables
        # Create the Answerer, give it the compute function.
        self._translator = translator
        self._answerer = telepot.async.helper.Answerer(self.bot)
        self._cacher = helpers.Cacher(self)
        rank, ocur = helpers.start_rank()
        self.settings = UserSettings(rank, ocur, len(rank), [], 2)
        self.cached_results = deque()

    def on_inline_query(self, msg):
        """ Handler for inline queries.
        """
        if not msg['query']:
            return

        # Grab the offset
        offset = int(msg['offset']) if msg['offset'] else 0
        # Trigger the answerer
        self._answerer.answer(msg, self.compute_answer, msg['query'], offset)
        # Trigger the Cacher
        self._cacher.cache(msg, self.fetch_translation, msg['query'], offset)

    async def compute_answer(self, query, offset):
        """ Delegated function for handling inline queries.
        """
        if offset:
            # Take the cached results
            # TODO Handle empty cache properly
            results = [self.cached_results.popleft() for _ in range(
                self.settings.page_size) if len(self.cached_results) > 0]
        else:
            # Fetch the first results
            first_page_langs = self.settings.rank[:self.settings.page_size]
            results = [self.fetch_translation(
                query, lang) for lang in first_page_langs]
        logging.info('Returning results for %s', tuple(x.id for x in results))
        return {
            'results': results,
            'next_offset': str(offset + self.settings.page_size)
        }

    def fetch_translation(self, query, lang_id):
        """ Queries the Microsoft translator API and fetchs
        the translations for the given user query.
        """
        translated_query = self._translator.translate(query, lang_id)
        return InlineQueryResultArticle(
            type='article',
            id=lang_id,
            title=helpers.get_lang_name(lang_id),
            description=translated_query,
            message_text=translated_query
        )

    def on_chosen_inline_result(self, msg):
        """ Handler for when inline result has been chosen.
        """
        result_id = msg['result_id']
        self.settings.total_ocurrences += 1
        self.settings.ocurrences[result_id] += 1
        self.settings.last_ocurrences = self.settings.last_ocurrences[
            1:] + [result_id]
        self.settings.rank.sort(
            key=lambda lang_id: helpers.rating_calc(
                lang_id,
                self.settings.ocurrences[lang_id],
                self.settings.last_ocurrences,
                self.settings.total_ocurrences
            ),
            reverse=True
        )
