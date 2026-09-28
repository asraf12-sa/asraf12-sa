from gemini_client import get_gemini


SYSTEM = """
You are EduGenie, a careful educational assistant.

Your job is to help students understand academic topics.

Rules:

1. Answer clearly.
2. Use simple language.
3. Explain difficult terms.
4. Give examples when useful.
5. Do not invent facts.
6. If information is uncertain, say so.
7. Keep answers appropriate for students.
8. Adapt the explanation to the student's needs.
"""


def answer_question(question: str) -> str:

    prompt = f"""
Answer this student's question:

{question}

Give a clear answer.

When useful, provide:
- a short explanation
- an example
- important points

Keep the answer educational and easy to understand.
"""

    return get_gemini().generate(
        prompt,
        SYSTEM
    )