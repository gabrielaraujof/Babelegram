#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Bot engine handlers.
"""

import asyncio
from collections import namedtuple
import telepot
from telepot.namedtuple import InlineQueryResultArticle
from telepot.async.delegate import per_inline_from_id, create_open

import helpers


UserSettings = namedtuple('UserSettings', \
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
        self._settings = UserSettings(rank, ocur, len(rank), [], 2)
        self.cached_results = None

    def on_inline_query(self, msg):
        """ Handler for inline queries.
        """
        # Just dump inline query to answerer
        self._answerer.answer(msg, self.compute_answer, msg)

    @asyncio.coroutine
    def compute_answer(self, inline_query):
        """ Delegated function for handling inline queries.
        """
        if not inline_query['query']:
            return []
        offset = int(inline_query['offset']) if inline_query['offset'] else 0
        return {
            'results': self.get_result_list(inline_query, offset),
            'next_offset': str(offset + self._settings.page_size)
        }

    def get_result_list(self, inline_query, offset):
        """ Create the result dict containing all the inline query results.
        """
        query_string = inline_query['query']
        if not offset:
            page_languages = self._settings.rank[:self._settings.page_size * 2]
            results = list(self.fetch_translations(query_string, page_languages))
            self.cached_results = results[self._settings.page_size:self._settings.page_size * 2]
            cur_results = results[:self._settings.page_size]
            return cur_results
        else:
            fetch_offset = offset + self._settings.page_size
            self._cacher.cache(inline_query, self.caching_results, query_string, fetch_offset)
            return self.cached_results

    def fetch_translations(self, query, languages):
        """ Queries the Microsoft translator API and fetchs
        the translations for the given user query.
        """
        for lang_id in languages:
            translated_query = self._translator.translate(
                query, lang_id)
            yield InlineQueryResultArticle(
                type='article',
                id=lang_id,
                title=helpers.get_lang_name(lang_id),
                description=translated_query,
                message_text=translated_query
            )

    @asyncio.coroutine
    def caching_results(self, query, offset):
        """ Fetching and caching the next results.
        """
        languages = self._settings.rank[offset:offset + self._settings.page_size]
        results = list(self.fetch_translations(query, languages))
        return results

    def on_chosen_inline_result(self, msg):
        """ Handler for when inline result has been chosen.
        """
        result_id = msg['result_id']
        self._settings.total_ocurrences += 1
        self._settings.ocurrences[result_id] += 1
        self._settings.last_ocurrences = self._settings.last_ocurrences[1:] + [result_id]
        self._settings.rank.sort(
            key=lambda lang_id: helpers.rating_calc(
                lang_id,
                self._settings.ocurrences[lang_id],
                self._settings.last_ocurrences,
                self._settings.total_ocurrences
            ),
            reverse=True
        )
