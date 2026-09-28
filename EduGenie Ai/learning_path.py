from gemini_client import get_gemini


SYSTEM = """
You are EduGenie, an expert curriculum designer.

Create realistic and structured learning paths.

Start with prerequisites and beginner concepts.

Then progress to intermediate and advanced concepts.

Include:
- practice
- checkpoints
- projects
- suggested resource types

Do not fabricate specific URLs.

Make the plan achievable for the learner's level.
"""


def get_learning_recommendations(
    topic: str,
    level: str,
    weeks: int
) -> str:

    prompt = f"""
Create a {weeks}-week learning path.

Topic:
{topic}

Current learner level:
{level}

Structure the answer as:

1. Learning goal
2. Prerequisites
3. Week-by-week plan
4. Beginner topics
5. Intermediate topics
6. Advanced topics
7. Practice activities
8. Checkpoints
9. Mini projects
10. Suggested resource types
11. Final project
12. Next steps

Make the progression logical.

The learner should gradually move
from beginner knowledge toward advanced understanding.
"""

    return get_gemini().generate(
        prompt,
        SYSTEM
    )