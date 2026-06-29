SUPPORTED_LANGUAGES = {
    "en": {
        "name": "English",
        "native_name": "English",
        "instruction": "Respond in clear simple English.",
    },
    "kn": {
        "name": "Kannada",
        "native_name": "ಕನ್ನಡ",
        "instruction": "Respond only in Kannada language using Kannada script.",
    },
    "hi": {
        "name": "Hindi",
        "native_name": "हिन्दी",
        "instruction": "Respond only in Hindi language using Devanagari script.",
    },
    "ta": {
        "name": "Tamil",
        "native_name": "தமிழ்",
        "instruction": "Respond only in Tamil language using Tamil script.",
    },
    "te": {
        "name": "Telugu",
        "native_name": "తెలుగు",
        "instruction": "Respond only in Telugu language using Telugu script.",
    },
}


def normalize_language(language: str | None) -> str:
    if not language:
        return "en"

    language = language.lower().strip()

    if language in SUPPORTED_LANGUAGES:
        return language

    return "en"


def get_language_instruction(language: str | None) -> str:
    language = normalize_language(language)
    return SUPPORTED_LANGUAGES[language]["instruction"]


def get_language_name(language: str | None) -> str:
    language = normalize_language(language)
    return SUPPORTED_LANGUAGES[language]["name"]