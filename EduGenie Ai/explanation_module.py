from functools import lru_cache

from config import get_settings
from gemini_client import get_gemini


# =========================================================
# Load local LaMini model
# =========================================================

@lru_cache(maxsize=1)
def _local_pipeline():

    # Import lazily so the application can still use Gemini when the optional
    # local-model dependency is not installed.
    from importlib import import_module

    pipeline = import_module("transformers").pipeline

    settings = get_settings()

    return pipeline(
        "text2text-generation",
        model=settings.local_explanation_model,
        device=-1
    )


# =========================================================
# Local explanation
# =========================================================

def _local_explain(
    topic: str,
    level: str
) -> str:

    generator = _local_pipeline()

    prompt = f"""
Explain {topic} to a {level} student.

Use:
- simple language
- one analogy
- one small example

Keep the explanation concise and educational.
"""

    result = generator(
        prompt,
        max_new_tokens=300,
        do_sample=False
    )

    return result[0]["generated_text"].strip()


# =========================================================
# Public explanation function
# =========================================================

def explain_topic(
    topic: str,
    level: str
) -> str:

    settings = get_settings()

    # Try local LaMini model
    if settings.use_local_explanation:

        try:

            result = _local_explain(
                topic,
                level
            )

            if result:
                return result

        except Exception:
            # Fall back to Gemini
            pass

    # Gemini fallback
    prompt = f"""
Explain the topic:

{topic}

Student level:
{level}

Use simple language.

Include:
1. Definition
2. Simple explanation
3. Analogy
4. Example
5. Key points
"""

    system_instruction = """
You are a patient teacher.

Explain difficult concepts in a simple way
without losing correctness.

Use student-friendly language.
"""

    return get_gemini().generate(
        prompt,
        system_instruction
    )