"""
msmt.py

Functions to access the Microsoft Translator API HTTP Interface, using python's urllib/urllib2 libraries

"""

import urllib
import json
from xml.dom import minidom

from datetime import datetime


TOKEN_ENDPOINT = 'https://datamarket.accesscontrol.windows.net/v2/OAuth2-13'


def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


def datestring(display_format="%a, %d %b %Y %H:%M:%S", datetime_object=None):
    """Convert the datetime.date object (defaults to now, in utc) into a string, in the given display format"""
    if datetime_object is None:
        datetime_object = datetime.utcnow()
    return datetime.strftime(datetime_object, display_format)


def get_access_token(client_id, client_secret):
    """Make an HTTP POST request to the token service, and return the access_token,
    as described in number 3, here: http://msdn.microsoft.com/en-us/library/hh454949.aspx
    """

    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'scope': 'http://api.microsofttranslator.com'
    }

    data = urllib.parse.urlencode(params).encode('utf-8')

    try:

        request = urllib.request.Request(TOKEN_ENDPOINT)
        request.add_header(
            "Content-Type", "application/x-www-form-urlencoded; charset=utf-8")

        response = urllib.request.urlopen(request, data)
        response_data = json.loads(response.read().decode('utf-8'))

        if 'access_token' in response_data:
            return response_data['access_token']

    except urllib.error.HTTPError as e:
        if hasattr(e, 'reason'):
            print(datestring(), 'Could not connect to the server:', e.reason)
        elif hasattr(e, 'code'):
            print(datestring(), 'Server error: ', e.code)
    except TypeError:
        print(datestring(), 'Bad data from server')

supported_languages = {  # as defined here: http://msdn.microsoft.com/en-us/library/hh456380.aspx
    'ar': ' Arabic',
    'bg': 'Bulgarian',
    'ca': 'Catalan',
    'zh-CHS': 'Chinese (Simplified)',
    'zh-CHT': 'Chinese (Traditional)',
    'cs': 'Czech',
    'da': 'Danish',
    'nl': 'Dutch',
    'en': 'English',
    'et': 'Estonian',
    'fi': 'Finnish',
    'fr': 'French',
    'de': 'German',
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
    'pt': 'Portuguese',
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


def print_supported_languages():
    """Display the list of supported language codes and the descriptions as a single string
    (used when a call to translate requests an unsupported code)"""

    codes = []
    for k, v in supported_languages.items():
        codes.append('\t'.join([k, '=', v]))
    return '\n'.join(codes)


def to_bytestring(s):
    """Convert the given unicode string to a bytestring, using utf-8 encoding,
    unless it's already a bytestring"""

    if s:
        if isinstance(s, str):
            return s
        else:
            return s.encode('utf-8')


def translate(access_token, text, to_lang, from_lang=None):
    """Use the HTTP Interface to translate text, as described here:
    http://msdn.microsoft.com/en-us/library/ff512387.aspx
    and return an xml string if successful
    """

    if not access_token:
        print('Sorry, the access token is invalid')
    else:
        if to_lang not in supported_languages.keys():
            print('Sorry, the API cannot translate to', to_lang)
            print('Please use one of these instead:')
            print(print_supported_languages())
        else:
            data = {'text': to_bytestring(text), 'to': to_lang}

            if from_lang:
                if from_lang not in supported_languages.keys():
                    print('Sorry, the API cannot translate from', from_lang)
                    print('Please use one of these instead:')
                    print(print_supported_languages())
                    return
                else:
                    data['from'] = from_lang

            try:

                request = urllib.request.Request(
                    'http://api.microsofttranslator.com/v2/Http.svc/Translate?'
                    + urllib.parse.urlencode(data))
                request.add_header('Authorization', 'Bearer ' + access_token)

                response = urllib.request.urlopen(request)
                dom = minidom.parseString(response.read())
                stringNode = dom.getElementsByTagName('string')[0]
                return getText(stringNode.childNodes)

            except urllib.error.HTTPError as e:
                if hasattr(e, 'reason'):
                    print(datestring(), 'Could not connect to the server:', e.reason)
                elif hasattr(e, 'code'):
                    print(datestring(), 'Server error: ', e.code)
