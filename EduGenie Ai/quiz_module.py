import json
import re

from gemini_client import get_gemini
from models import QuizQuestion


# =========================================================
# Remove Markdown JSON code blocks
# =========================================================

def clean_json_block(text: str) -> str:

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return text.strip()


# =========================================================
# Generate quiz
# =========================================================

def generate_quiz(
    text: str,
    level: str
) -> list[QuizQuestion]:

    prompt = f"""
Create exactly 3 multiple-choice questions
from the educational passage below.

Learner level:
{level}

Requirements:

- Exactly 3 questions
- Exactly 4 options for every question
- Exactly one correct answer
- Include a short explanation
- Questions must be relevant to the passage
- Distractors should be plausible
- Use student-friendly language

Return ONLY valid JSON.

Use exactly this structure:

{{
  "questions": [
    {{
      "question": "Question text",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "correct_answer": "Option A",
      "explanation": "Short explanation"
    }}
  ]
}}

Educational passage:

{text}
"""

    system_instruction = """
You are EduGenie Quiz Generator.

Generate accurate educational MCQs.

Return machine-readable JSON only.
Do not add Markdown.
Do not add explanations outside the JSON.
"""

    raw = get_gemini().generate(
        prompt,
        system_instruction
    )

    try:

        cleaned = clean_json_block(raw)

        data = json.loads(cleaned)

        if "questions" not in data:
            raise ValueError(
                "Missing questions field"
            )

        questions = data["questions"]

        if len(questions) != 3:
            raise ValueError(
                "Expected exactly 3 questions"
            )

        parsed_questions = []

        for question in questions:

            parsed = QuizQuestion.model_validate(
                question
            )

            if parsed.correct_answer not in parsed.options:

                raise ValueError(
                    "correct_answer must match one of the options"
                )

            parsed_questions.append(
                parsed
            )

        return parsed_questions

    except Exception as exc:

        raise RuntimeError(
            f"Could not parse quiz response: {exc}"
        ) from exc