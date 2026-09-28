import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, Field


# Load .env
load_dotenv()


class Settings(BaseModel):

    gemini_api_key: str = Field(
        default="",
        alias="GEMINI_API_KEY"
    )

    gemini_model: str = Field(
        default="gemini-2.5-flash",
        alias="GEMINI_MODEL"
    )

    local_explanation_model: str = Field(
        default="MBZUAI/LaMini-Flan-T5-783M",
        alias="LOCAL_EXPLANATION_MODEL"
    )

    use_local_explanation: bool = Field(
        default=True,
        alias="USE_LOCAL_EXPLANATION"
    )

    temperature: float = Field(
        default=0.4,
        alias="TEMPERATURE"
    )

    max_output_tokens: int = Field(
        default=2048,
        alias="MAX_OUTPUT_TOKENS"
    )


@lru_cache
def get_settings() -> Settings:

    return Settings(
        GEMINI_API_KEY=os.getenv(
            "GEMINI_API_KEY",
            ""
        ),

        GEMINI_MODEL=os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash"
        ),

        LOCAL_EXPLANATION_MODEL=os.getenv(
            "LOCAL_EXPLANATION_MODEL",
            "MBZUAI/LaMini-Flan-T5-783M"
        ),

        USE_LOCAL_EXPLANATION=(
            os.getenv(
                "USE_LOCAL_EXPLANATION",
                "true"
            ).lower() == "true"
        ),

        TEMPERATURE=float(
            os.getenv(
                "TEMPERATURE",
                "0.4"
            )
        ),

        MAX_OUTPUT_TOKENS=int(
            os.getenv(
                "MAX_OUTPUT_TOKENS",
                "2048"
            )
        ),
    )