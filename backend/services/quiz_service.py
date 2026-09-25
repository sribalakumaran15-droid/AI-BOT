import json

def create_questions(course: str, topic: str, difficulty: str, count: int):
    question_bank = [
        {"prompt": f"Which statement best describes {topic}?", "options": [f"It is a core concept in {course}.", "It is only used outside computing.", "It cannot be tested with examples.", "It is unrelated to systems."], "answer": f"It is a core concept in {course}.", "explanation": f"{topic} is an important part of the {course} curriculum."},
        {"prompt": f"What is the best way to study {topic}?", "options": ["Connect a definition to a worked example.", "Memorize its name only.", "Skip practice.", "Avoid asking questions."], "answer": "Connect a definition to a worked example.", "explanation": "Worked examples make abstract concepts easier to recall."},
    ]
    return [question_bank[index % len(question_bank)] for index in range(count)]
