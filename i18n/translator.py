from .es import STRINGS_ES
from .en import STRINGS_EN

I18N = {
    "es": STRINGS_ES,
    "en": STRINGS_EN
}

class Translator:
    def __init__(self, default_lang="es"):
        self.current_lang = default_lang
        
    def set_language(self, lang):
        if lang in I18N:
            self.current_lang = lang
            
    def t(self, key):
        return I18N.get(self.current_lang, {}).get(key, key)
        
    def __call__(self, key):
        return self.t(key)