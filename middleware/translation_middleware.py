import json
from django.utils.deprecation import MiddlewareMixin
from utils.translate import translate_text


class TranslationMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response and response.has_header('Content-Type') and 'application/json' in response['Content-Type']:
            lang = request.META.get('HTTP_ACCEPT_LANGUAGE', 'en').split(',')[0]
            if lang != 'ru':
                return response

            # Translate the response content
            try:
                response_data = json.loads(response.content.decode('utf-8'))
                translated_data = self.translate_dict(response_data)
                response.content = json.dumps(translated_data).encode('utf-8')
            except Exception as e:
                print(f"Translation error: {e}")

        return response

    def translate_dict(self, data):
        if isinstance(data, dict):
            return {key: self.translate_dict(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.translate_dict(item) for item in data]
        elif isinstance(data, str):
            return translate_text(data)
        return data
