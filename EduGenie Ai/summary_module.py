from gemini_client import get_gemini


SYSTEM = """
You are EduGenie's educational summarization assistant.

Summarize educational material for students.

Rules:

1. Preserve important facts.
2. Preserve definitions.
3. Preserve important relationships.
4. Remove unnecessary repetition.
5. Use simple language.
6. Keep the original meaning.
7. Do not invent information.
8. Use bullets when helpful.
"""


def summarize_text(text: str) -> str:

    prompt = f"""
Summarize the following educational passage.

The summary should be useful for quick revision.

Include the most important:
- concepts
- facts
- definitions
- relationships
- conclusions

Educational passage:

{text}
"""

    return get_gemini().generate(
        prompt,
        SYSTEM
    )