import os
from typing import Any


def _fallback_answer(question: str, context: str = "") -> str:
    if context:
        return f"### From your study material\n\n{context}\n\n**Study tip:** Re-read the surrounding section and connect this idea to an example from your course."
    lower = question.lower()
    answers = {
        "stack": "A stack is a last-in, first-out (LIFO) data structure. Think of a stack of plates: the last plate placed on top is the first one removed. Its main operations are push, pop, and peek.",
        "queue": "A queue is a first-in, first-out (FIFO) data structure. It works like a line at a counter: the first item to arrive is served first. Its common operations are enqueue and dequeue.",
        "normalization": "Database normalization organizes tables to reduce duplicate data and update problems. Common stages include 1NF, 2NF, and 3NF, each adding rules about atomic values and dependencies.",
        "operating system": "An operating system manages computer hardware and provides services for applications. Its responsibilities include process management, memory management, files, devices, and security.",
        "machine learning": "Machine learning is a way for computers to learn patterns from data and use those patterns to make predictions or decisions without being explicitly programmed for every case.",
    }
    for key, answer in answers.items():
        if key in lower:
            return answer
    return "I do not have enough course-specific context to answer that precisely yet. Upload a relevant study document, or ask about a topic in the sample curriculum."


def answer_question(question: str, results: list[dict[str, Any]], extra_context: str = "") -> str:
    if not question.strip():
        return "Please enter a question."
    context = "\n\n".join(result["text"] for result in results[:3])
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback_answer(question, context or extra_context)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        prompt = "Use the supplied study context first. If it does not answer the question, say that it was not found in the uploaded material. Be clear and beginner-friendly.\n\nContext:\n" + (context or extra_context or "No uploaded context")
        response = client.chat.completions.create(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), messages=[{"role": "system", "content": prompt}, {"role": "user", "content": question}], temperature=0.2)
        return response.choices[0].message.content or "The AI returned an empty answer."
    except Exception:
        return "The AI service is unavailable right now. Please check your API key or try again with local fallback by removing it temporarily."


def explain_simply(topic: str) -> str:
    if os.getenv("OPENAI_API_KEY"):
        return answer_question(f"Explain {topic} simply. Include a definition, simple example, real-world analogy, and key points.", [])
    return f"## {topic.title()}\n\n**Definition**\n{topic.title()} is a concept that can be understood by breaking it into a smaller idea and observing how it works.\n\n**Simple example**\nImagine working through a small example of {topic}; write down the starting information, the rule being applied, and the result.\n\n**Real-world analogy**\nLearning {topic} is like following a recipe: understand the ingredients, apply the steps in order, and check the result.\n\n**Key points**\n- Start with the definition.\n- Work through one small example.\n- Explain the idea in your own words."
