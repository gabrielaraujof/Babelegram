#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
A set of helpers functions and constants for supporting the bot engine.
"""

_LANG_SET = {
    'ar': ' Arabic',
    'bg': 'Bulgarian',
    'ca': 'Catalan',
    'zh-CHS': 'Chinese (Simplified)',
    'zh-CHT': 'Chinese (Traditional)',
    'cs': 'Czech',
    'da': 'Danish',
    'nl': 'Dutch',
    'en': 'Inglês',
    'et': 'Estonian',
    'fi': 'Finnish',
    'fr': 'Francês',
    'de': 'Alemão',
    'el': 'Greek',
    'ht': 'Haitian Creole',
    'he': 'Hebrew',
    'hi': 'Hindi',
    'hu': 'Hungarian',
    'id': 'Indonesian',
    'it': 'Italian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'lv': 'Latvian',
    'lt': 'Lithuanian',
    'mww': 'Hmong Daw',
    'no': 'Norwegian',
    'pl': 'Polish',
    'pt': 'Português',
    'ro': 'Romanian',
    'ru': 'Russian',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'es': 'Spanish',
    'sv': 'Swedish',
    'th': 'Thai',
    'tr': 'Turkish',
    'uk': 'Ukrainian',
    'vi': 'Vietnamese',
}


def get_lang_name(lang_id):
    """ Returns the name of a language by its id.
    """
    return _LANG_SET[lang_id]


def start_rank():
    """ Create the structure for ranking with the languages
    available for translating."""
    ocurrence_dict = {lang_id: 1 for lang_id, name in _LANG_SET.items()}
    ranking = list([lang_id for lang_id, name in _LANG_SET.items()])
    return ranking, ocurrence_dict


def rating_calc(item, ocurrences, last_ocurrences, total_ocurrences):
    """ Calculates the rating of the target language.
    """
    rating = ocurrences / total_ocurrences
    if item in last_ocurrences:
        rating *= 2
    if last_ocurrences and item == last_ocurrences[-1]:
        rating *= 4
    return rating

import asyncio
from concurrent.futures._base import CancelledError

@asyncio.coroutine
def _yell(fn, *args, **kwargs):
    if asyncio.iscoroutinefunction(fn):
        return (yield from fn(*args, **kwargs))
    else:
        return fn(*args, **kwargs)

class Cacher(object):

    def __init__(self, bot_handler, loop=None):
        self._bot_handler = bot_handler
        self._loop = loop if loop is not None else asyncio.get_event_loop()
        self._working_tasks = {}

    def cache(self, inline_query, compute_fn, *compute_args, **compute_kwargs):
        from_id = inline_query['from']['id']

        @asyncio.coroutine
        def compute_and_cache():
            try:
                ans = yield from _yell(compute_fn, *compute_args, **compute_kwargs)
                if isinstance(ans, list):
                    self._bot_handler.cached_results = ans
                else:
                    raise ValueError('Invalid answer format')
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

        t = self._loop.create_task(compute_and_cache())
        self._working_tasks[from_id] = t
