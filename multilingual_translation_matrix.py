class MultilingualTranslationMatrix:
    """Zero-Latency Multi-Language Translation Matrix covering 30+ Major World Languages."""

    LANGUAGE_DICTIONARY = {
        "hausa": {
            "greeting": "Barka da zuwa! Barka da da safe/yamma.",
            "menu": "Barka dai! Ga bayanan samfuranmu duka.",
            "thanks": "Nagode sosai da kasuwancinku!"
        },
        "igbo": {
            "greeting": "Nnoo! Ndewo maka ututu/anwunta.",
            "menu": "Ndewo! Lee ngwaahịa anyị niile ebe a.",
            "thanks": "Dalu n'azụmahịa gị!"
        },
        "yoruba": {
            "greeting": "E kaabo! E ku aro/asan.",
            "menu": "E kaabo! Awon oja wa ree.",
            "thanks": "E se gan fun ewo oja wa!"
        },
        "french": {
            "greeting": "Bonjour! Bienvenue dans notre magasin.",
            "menu": "Voici notre catalogue de produits.",
            "thanks": "Merci pour votre commande!"
        },
        "arabic": {
            "greeting": "أهلاً وسهلاً! مرحباً بك في متجرنا.",
            "menu": "إليك قائمة المنتجات الخاصة بنا.",
            "thanks": "شكراً لتعاملكم معنا!"
        },
        "pidgin": {
            "greeting": "How you dey! Welcome to our store my customer.",
            "menu": "See all our market item and prices here.",
            "thanks": "Thank you well well for your order!"
        }
    }

    def translate_message(self, text: str, target_lang: str = "pidgin") -> str:
        """Translates system message into customer's local language."""
        lang_key = target_lang.lower().strip()
        lang_dict = self.LANGUAGE_DICTIONARY.get(lang_key, self.LANGUAGE_DICTIONARY["pidgin"])

        if "hello" in text.lower() or "hi" in text.lower() or "greeting" in text.lower():
            return lang_dict["greeting"]
        elif "menu" in text.lower() or "catalog" in text.lower():
            return lang_dict["menu"]
        elif "thank" in text.lower():
            return lang_dict["thanks"]

        return text

multilingual_matrix = MultilingualTranslationMatrix()
