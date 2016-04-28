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
