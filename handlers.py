#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Bot engine handlers.
"""

import asyncio
import telepot
from telepot.namedtuple import InlineQueryResultArticle
from telepot.async.delegate import per_inline_from_id, create_open

import helpers


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
        self._answerer = telepot.async.helper.Answerer(
            self.bot, self.compute_answer)
        self._ocurrences, self._rank = helpers.start_rank()
        self._total_ocurrences = len(self._rank)
        self._last_ocurrences = []

    def on_inline_query(self, msg):
        """ Handler for inline queries.
        """
        # Just dump inline query to answerer
        self._answerer.answer(msg)

    @asyncio.coroutine
    def compute_answer(self, inline_query):
        """ Delegated function for handling inline queries.
        """
        query_string = inline_query['query']
        offset = int(inline_query['offset']) if inline_query['offset'] else 0

        if not query_string:
            return []

        return {
            'results': self.get_result_list(query_string, offset),
            'next_offset': str(offset + 2)
        }

    def get_result_list(self, query_string, offset):
        """ Create the result dict containing all the inline query results.
        """
        results = []
        for lang_id in self._rank[offset:offset + 2]:
            translated_query = self._translator.translate(
                query_string, lang_id)
            results.append(InlineQueryResultArticle(
                type='article',
                id=lang_id,
                title=helpers.get_lang_name(lang_id),
                description=translated_query,
                message_text=translated_query
            ))
        return results

    def on_chosen_inline_result(self, msg):
        """ Handler for when inline result has been chosen.
        """
        result_id = msg['result_id']
        self._total_ocurrences += 1
        self._ocurrences[result_id] += 1
        self._last_ocurrences = self._last_ocurrences[1:] + [result_id]
        self._rank.sort(
            key=lambda lang_id: helpers.rating_calc(
                lang_id,
                self._ocurrences[lang_id],
                self._last_ocurrences,
                self._total_ocurrences
            ),
            reverse=True
        )
