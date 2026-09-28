from functools import lru_cache

from config import get_settings


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


    def generate(
        self,
        prompt: str,
        system_instruction: str | None = None
    ) -> str:

        from google.genai import types

        config = types.GenerateContentConfig(
            temperature=self.settings.temperature,
            max_output_tokens=self.settings.max_output_tokens,
            system_instruction=system_instruction,
        )

        response = self.client.models.generate_content(
            model=self.settings.gemini_model,
            contents=prompt,
            config=config,
        )

        text = getattr(
            response,
            "text",
            None
        )

        if not text:

            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return text.strip()


@lru_cache
def get_gemini() -> GeminiService:

    return GeminiService()