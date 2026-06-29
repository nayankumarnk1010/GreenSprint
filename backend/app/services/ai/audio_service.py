import os
import uuid
from pathlib import Path

from app.ai.languages import normalize_language
from app.core.config import settings


class AudioService:
    @staticmethod
    def generate_audio(
        text: str,
        language: str = "en",
    ) -> str | None:
        if not text:
            return None

        language = normalize_language(language)

        if language == "en":
            return AudioService._generate_english_audio(
                text=text,
            )

        return AudioService._generate_indian_language_audio(
            text=text,
            language=language,
        )

    @staticmethod
    def _generate_english_audio(
        text: str,
    ) -> str | None:
        try:
            import pyttsx3
        except Exception:
            return None

        storage_dir = Path(settings.AI_AUDIO_STORAGE_DIR)
        storage_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_name = f"{uuid.uuid4()}.wav"
        file_path = storage_dir / file_name

        try:
            engine = pyttsx3.init()

            voices = engine.getProperty("voices")
            selected_voice_id = None

            for voice in voices:
                voice_text = f"{voice.id} {voice.name}".lower()

                if "english" in voice_text or "en" in voice_text:
                    selected_voice_id = voice.id
                    break

            if selected_voice_id:
                engine.setProperty(
                    "voice",
                    selected_voice_id,
                )

            engine.setProperty(
                "rate",
                155,
            )

            engine.save_to_file(
                text,
                str(file_path),
            )

            engine.runAndWait()

            if not os.path.exists(file_path):
                return None

            return f"/media/ai_audio/{file_name}"

        except Exception:
            return None

    @staticmethod
    def _generate_indian_language_audio(
        text: str,
        language: str,
    ) -> str | None:
        try:
            from gtts import gTTS
        except Exception:
            return None

        storage_dir = Path(settings.AI_AUDIO_STORAGE_DIR)
        storage_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_name = f"{uuid.uuid4()}.mp3"
        file_path = storage_dir / file_name

        try:
            gtts_language_map = {
                "hi": "hi",
                "kn": "kn",
                "ta": "ta",
                "te": "te",
            }

            tts_language = gtts_language_map.get(
                language,
                "en",
            )

            tts = gTTS(
                text=text,
                lang=tts_language,
                slow=False,
            )

            tts.save(
                str(file_path),
            )

            if not os.path.exists(file_path):
                return None

            return f"/media/ai_audio/{file_name}"

        except Exception:
            return None