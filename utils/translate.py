from translate import Translator
from django.core.cache import cache
from langdetect import detect

CACHE_TIMEOUT = 60 * 60 * 24 * 30 * 12  # 1 year


def translate_text(text):
    try:
        if detect(text) == 'ru':
            return text
    except:
        pass  # If language detection fails, proceed to translation
    cache_key = f'translation_{hash(text)}'
    translation = cache.get(cache_key)
    if not translation:
        translator = Translator(to_lang="ru")
        translation = translator.translate(text)
        cache.set(cache_key, translation, CACHE_TIMEOUT)
    return translation
