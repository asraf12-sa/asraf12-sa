import logging
from functools import lru_cache

from config import get_settings

logger = logging.getLogger(__name__)


class GeminiService:

    def __init__(self):

        from google import genai

        settings = get_settings()

        if not settings.gemini_api_key:

            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Create a .env file and add your Gemini API key."
            )

        self.settings = settings

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    @staticmethod
    def _is_retryable_provider_error(exc: Exception) -> bool:
        code = getattr(exc, "code", None)
        if code is None:
            code = getattr(exc, "status_code", None)

        if code in {429, 500, 503}:
            return True

        message = str(exc).lower()
        retry_indicators = (
            "temporarily unavailable",
            "unavailable",
            "rate limit",
            "quota",
            "overloaded",
            "too many requests",
            "high demand",
            "429",
            "503",
        )

        return any(indicator in message for indicator in retry_indicators)

    def _generate_with_model(
        self,
        model_name: str,
        prompt: str,
        system_instruction: str | None = None,
    ):
        from google.genai import types

        config = types.GenerateContentConfig(
            temperature=self.settings.temperature,
            max_output_tokens=self.settings.max_output_tokens,
            system_instruction=system_instruction,
        )

        return self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config,
        )

    def generate(
        self,
        prompt: str,
        system_instruction: str | None = None
    ) -> str:

        fallback_models = [
            self.settings.gemini_model,
            "gemini-2.5-flash",
            "gemini-1.5-flash",
        ]

        seen_models = set()
        last_error: Exception | None = None

        for model_name in fallback_models:
            if not model_name or model_name in seen_models:
                continue

            seen_models.add(model_name)

            try:
                response = self._generate_with_model(
                    model_name,
                    prompt,
                    system_instruction,
                )

                text = getattr(response, "text", None)

                if not text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                return text.strip()

            except Exception as exc:
                last_error = exc

                if not self._is_retryable_provider_error(exc):
                    raise

                logger.warning(
                    "Gemini model %s is unavailable; trying fallback model. "
                    "Error: %s",
                    model_name,
                    exc,
                )

        if last_error is not None:
            raise last_error

        raise RuntimeError("Gemini is temporarily unavailable. Please try again shortly.")


@lru_cache
def get_gemini() -> GeminiService:

    return GeminiService()