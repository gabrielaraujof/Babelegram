import sys
import asyncio
import telepot
import telepot.async

import mstranslate as translator

"""
$ python3.4 skeletona.py <token>
A skeleton for your async telepot programs.
"""


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Normal Message:', content_type, chat_type, chat_id)


@asyncio.coroutine
def on_inline_query(msg):
    # need `/setinline`
    query_id, from_id, query_string = telepot.glance(
        msg, flavor='inline_query')

    if query_string:
        # print('Inline Query:', query_id, from_id, query_string)
        translated_text = translator.translate(
            AZ_ACCESS_TOKEN, query_string, 'en', 'pt')

        # Compose your own answers
        articles = [{
            'type': 'article',
            'id': '0',
            'title': '{0}...'.format(translated_text),
            'message_text': translated_text
        }]
        yield from bot.answerInlineQuery(query_id, articles)


def on_chosen_inline_result(msg):
    # need `/setinlinefeedback`
    result_id, from_id, query_string = telepot.glance(
        msg, flavor='chosen_inline_result')
    print('Chosen Inline Result:', result_id, from_id, query_string)


BOT_TOKEN, AZ_CLIENT_ID, AZ_CLIENT_SECRET = sys.argv[1:4]

# Getting the MS Translate API token
AZ_ACCESS_TOKEN = translator.get_access_token(AZ_CLIENT_ID, AZ_CLIENT_SECRET)
print(AZ_ACCESS_TOKEN)

bot = telepot.async.Bot(BOT_TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop({'normal': on_chat_message,
                                  'inline_query': on_inline_query,
                                  'chosen_inline_result': on_chosen_inline_result}))
print('Listening ...')

loop.run_forever()
