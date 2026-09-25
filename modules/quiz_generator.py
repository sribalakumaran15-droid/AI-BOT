import json
import os
from typing import Any


def generate_quiz(course: str, topic: str, count: int) -> list[dict[str, Any]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            prompt = f"Create {count} beginner MCQs about {topic} in {course}. Return only JSON array objects with question, options (4 strings), answer (one option exactly), explanation."
            response = client.chat.completions.create(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"}, temperature=0.4)
            payload = json.loads(response.choices[0].message.content)
            return payload.get("questions", payload)[:count]
        except Exception:
            pass
    return _local_quiz(course, topic, count)


def _local_quiz(course: str, topic: str, count: int) -> list[dict[str, Any]]:
    bank = [{"question": f"Which statement best describes {topic}?", "options": [f"It is a core concept in {course}.", "It is only used outside computing.", "It cannot be tested with examples.", "It is unrelated to data or systems."], "answer": f"It is a core concept in {course}.", "explanation": f"{topic} is listed as an important topic in the {course} curriculum."}, {"question": f"What is a good way to learn {topic}?", "options": ["Connect its definition to a worked example.", "Memorize the name only.", "Skip all practice.", "Avoid asking questions."], "answer": "Connect its definition to a worked example.", "explanation": "Examples make abstract academic concepts easier to understand and recall."}]
    return [bank[index % len(bank)] for index in range(count)]
