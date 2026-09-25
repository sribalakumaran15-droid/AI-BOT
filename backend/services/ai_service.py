import os
from backend.config import OPENAI_API_KEY, OPENAI_MODEL

FALLBACKS = {
    "stack": "A stack is a last-in, first-out data structure. Think of plates: the last plate placed on top is the first removed. Its main operations are push, pop, and peek.",
    "queue": "A queue follows first-in, first-out, like a line at a counter. Items are added at the rear and removed from the front.",
    "recursion": "Recursion is when a function solves a problem by calling itself on a smaller version of the problem. Every recursive solution needs a base case to stop.",
    "normalization": "Normalization organizes database tables to reduce duplicate data and prevent inconsistent updates. The common stages are 1NF, 2NF, and 3NF.",
}

def generate_answer(question: str, context: list[dict], history: list[dict] | None = None) -> str:
    source_context = "\n\n".join(item["text"] for item in context)
    if OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            system = "You are StudyAI, a clear academic tutor. Use the provided study context first. Structure answers with headings, bullets, and examples. If context does not answer the question, say so clearly.\n\nSTUDY CONTEXT:\n" + (source_context or "No uploaded context available.")
            messages = [{"role": "system", "content": system}] + (history or []) + [{"role": "user", "content": question}]
            response = client.chat.completions.create(model=OPENAI_MODEL, messages=messages, temperature=0.2)
            return response.choices[0].message.content or "The AI returned an empty answer."
        except Exception:
            pass
    lowered = question.lower()
    for key, value in FALLBACKS.items():
        if key in lowered:
            return value
    if source_context:
        return "### From your uploaded material\n\n" + source_context + "\n\n**Study tip:** Connect this passage to a worked example from your course."
    return "I do not have enough course-specific context to answer that precisely yet. Upload a relevant study material or ask about a topic in the curriculum."
