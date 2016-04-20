#!/usr/bin/python3
"""
Package responsable for fetching the translations.
"""

import logging
import asyncio
import os
from concurrent.futures._base import CancelledError

import telepot
from telepot.namedtuple import InlineQueryResultArticle

import helpers


BASE_URL = os.environ['BOT_BASE_URL']


class Translator(object):
    """ Responsable for fetching the page results of inline queries.
    """

    def __init__(self, rank, queue, translator, loop=None):
        self.rank = rank
        self.queue = queue
        self.translator = translator
        self._loop = loop if loop is not None else asyncio.get_event_loop()
        self._working_tasks = {}

    def fetch_translation(self, query, lang_id):
        """ Queries the Microsoft translator API and fetchs
        the translations for the given user query.
        """
        translated_query = self.translator.translate(query, lang_id)
        return InlineQueryResultArticle(
            type='article',
            id=lang_id,
            title=translated_query,
            description=helpers.get_lang_name(lang_id),
            message_text=translated_query,
            # thumb_url=BASE_URL + '/img/icon.png',
            # thumb_width=64,
            # thumb_height=64
        )

    def cache(self, inline_query):
        """ Creates the task and get it running in the event loop.
        """
        _, from_id, query = telepot.glance(inline_query, flavor='inline_query')

        async def compute_and_cache():
            """Wraps the function to be executed in order to proper
             handling exceptions.
             """
            try:
                for lang_id in self.rank:
                    future = self._loop.run_in_executor(
                        None, self.fetch_translation, query, lang_id)
                    translation = await future
                    await self.queue.put(translation)
                    logging.info('Caching result for %s', lang_id)
            except CancelledError:
                # Cancelled. Record has been occupied by new task. Don't touch.
                raise
            except:
                # Die accidentally. Remove myself from record.
                del self._working_tasks[from_id]
                raise
            else:
                # Die naturally. Remove myself from record.
                del self._working_tasks[from_id]

        if from_id in self._working_tasks:
            self._working_tasks[from_id].cancel()

        caching_task = self._loop.create_task(compute_and_cache())
        self._working_tasks[from_id] = caching_task
