#!/usr/bin/python3
"""
Bot engine handlers.
"""

import logging
import asyncio

import telepot
from telepot.async.delegate import per_inline_from_id, create_open

import helpers
import translator


def create_bot(token, translator_engine):
    """ Create a new bot instance
    """
    return telepot.async.DelegatorBot(token, [
        (per_inline_from_id(), create_open(
            BabelegramHandler, timeout=60, translator_engine=translator_engine)),
    ])


class BabelegramHandler(telepot.async.helper.UserHandler):
    """ Bot message handler.
    """

    def __init__(self, seed_tuple, timeout, translator_engine):
        super(BabelegramHandler, self).__init__(
            seed_tuple, timeout,
            flavors=['inline_query', 'chosen_inline_result']
        )
        logging.info('Started handler...')
        # Init instance variables
        # Create the Answerer, give it the compute function.
        self._answerer = telepot.async.helper.Answerer(self.bot)
        rank, ocur = helpers.start_rank()
        self.settings = {
            'rank': rank,
            'ocurrences': ocur,
            'total_ocurrences': len(rank),
            'last_ocurrences': [],
            'page_size': 2
        }
        self.cached_results = asyncio.Queue(
            maxsize=self.settings['page_size'] * 2)
        self._translator = translator.Translator(
            self.settings['rank'], self.cached_results, translator_engine)

    def on_inline_query(self, msg):
        """ Handler for inline queries.
        """
        if not msg['query']:
            return
        offset = int(msg['offset'] if msg['offset'] else 0)

        logging.info('Processing query "%s"', msg['query'])
        if not offset:
            # Empty cache
            while not self.cached_results.empty():
                self.cached_results.get_nowait()
            # Start the translator
            self._translator.cache(msg)

        # Trigger the answerer
        self._answerer.answer(msg, self.gather_answers, offset)

    async def gather_answers(self, offset):
        """ Delegated function for gathering the results from queue.
        """
        results = []
        while offset < len(self.settings['rank']) and len(results) < self.settings['page_size']:
            translation = await self.cached_results.get()
            results.append(translation)
            offset += 1

        logging.info('Returning results for %s', tuple(x.id for x in results))
        return {
            'results': results,
            'next_offset': str(offset)
        }

    def on_chosen_inline_result(self, msg):
        """ Handler for when inline result has been chosen.
        """
        result_id = msg['result_id']
        self.settings['total_ocurrences'] += 1
        self.settings['ocurrences'][result_id] += 1
        self.settings['last_ocurrences'] = self.settings['last_ocurrences'][
            1:] + [result_id]
        self.settings['rank'].sort(
            key=lambda lang_id: helpers.rating_calc(
                lang_id,
                self.settings['ocurrences'][lang_id],
                self.settings['last_ocurrences'],
                self.settings['total_ocurrences']
            ),
            reverse=True
        )

    def on_close(self, exception):
        logging.info(r'Closing user handler. [Cause: %s]', exception)
