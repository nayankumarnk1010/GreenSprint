import json
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.request import Request
from urllib.request import urlopen

from app.core.config import settings


class OllamaClient:
    @staticmethod
    def generate(
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
    ) -> tuple[bool, str]:
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"

        final_prompt = prompt

        if system_prompt:
            final_prompt = f"{system_prompt}\n\nUser Request:\n{prompt}"

        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": final_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 500,
            },
        }

        request = Request(
            url=url,
            data=json.dumps(
                payload,
                ensure_ascii=False,
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
            method="POST",
        )

        try:
            with urlopen(
                request,
                timeout=180,
            ) as response:
                response_data = json.loads(
                    response.read().decode("utf-8")
                )

                answer = response_data.get(
                    "response",
                    "",
                ).strip()

                if not answer:
                    return False, "Ollama returned an empty response."

                return True, answer

        except HTTPError as exc:
            try:
                error_body = exc.read().decode("utf-8")
            except Exception:
                error_body = str(exc)

            return False, f"Ollama HTTP error: {error_body}"

        except URLError as exc:
            return False, f"Ollama is not available: {exc}"

        except TimeoutError:
            return False, "Ollama request timed out."

        except Exception as exc:
            return False, f"Ollama error: {exc}"