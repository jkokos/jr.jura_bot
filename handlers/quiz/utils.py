import unicodedata
import re
import json
from difflib import SequenceMatcher
from aiogram import Bot
from ai_open.gpt_messages import GPTMessage
from ai_open import chat_gpt


def normalize_quiz_answer(text: str) -> str: #Подготавливает ответ для сравнения.


    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = text.lower().strip()


    text = re.sub(r"[«»\"'`(){}\[\].,!?;:]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()

       #Сравнивает ответ пользователя с допустимыми ответами.
def quiz_answers_are_equal(user_answer: str,accepted_answers: list[str],) -> bool:


    normalized_user = normalize_quiz_answer(user_answer)

    if not normalized_user:
        return False

    for accepted_answer in accepted_answers:
        normalized_correct = normalize_quiz_answer(accepted_answer)

        if not normalized_correct:
            continue


        if normalized_user == normalized_correct:    # Точное совпадение
            return True

        # Небольшая опечатка
        similarity = SequenceMatcher(None,normalized_user,normalized_correct,).ratio()

        # Для очень коротких ответов нужна почти полная точность
        threshold = 0.95 if len(normalized_correct) <= 4 else 0.88

        if similarity >= threshold:
            return True

    return False

def parse_quiz_response(response: str) -> dict: #Извлекает и проверяет JSON, который вернул GPT


    if not response:
        raise ValueError("GPT вернул пустой ответ")

    clean_response = response.strip()


    clean_response = re.sub(r"^```(?:json)?\s*","",clean_response,flags=re.IGNORECASE,)
    clean_response = re.sub(r"\s*```$", "", clean_response)

    json_match = re.search(r"\{.*\}",clean_response,flags=re.DOTALL,)

    if not json_match:
        raise ValueError("В ответе GPT не найден JSON")

    quiz_data = json.loads(json_match.group())

    question = quiz_data.get("question")
    correct_answer = quiz_data.get("correct_answer")
    accepted_answers = quiz_data.get("accepted_answers", [])
    explanation = quiz_data.get("explanation", "")

    if not isinstance(question, str) or not question.strip():
        raise ValueError("GPT не вернул вопрос")

    if not isinstance(correct_answer, str) or not correct_answer.strip():
        raise ValueError("GPT не вернул правильный ответ")

    if not isinstance(accepted_answers, list):
        accepted_answers = []

    # Основной ответ всегда добавляется в список допустимых
    all_answers = [correct_answer, *accepted_answers]
    unique_answers: list[str] = []
    normalized_seen: set[str] = set()

    for answer in all_answers:
        if not isinstance(answer, str):
            continue

        answer = answer.strip()
        normalized = normalize_quiz_answer(answer)

        if not normalized or normalized in normalized_seen:
            continue

        normalized_seen.add(normalized)
        unique_answers.append(answer)

    return {
        "question": question.strip(),
        "correct_answer": correct_answer.strip(),
        "accepted_answers": unique_answers,
        "explanation": (
            explanation.strip()
            if isinstance(explanation, str)
            else ""
        ),
    }

async def generate_quiz_question(bot: Bot,topic_command: str,topic_name: str,used_questions: list[str] | None = None,) -> dict:
    #Создаёт новый вопрос через GPT и возвращает данные вопроса

    used_questions = used_questions or []

    previous_questions = "\n".join(
        f"- {question}"
        for question in used_questions[-15:]
    )

    if not previous_questions:
        previous_questions = "Предыдущих вопросов нет."

    quiz_message = GPTMessage("quiz")

    quiz_message.message_list.append({
        "role": "user",
        "content": (
            "Создай один новый вопрос для викторины.\n\n"
            f"Команда темы: {topic_command}\n"
            f"Название темы: {topic_name}\n\n"
            "Требования:\n"
            "1. Создай только один вопрос.\n"
            "2. Правильный ответ должен состоять максимум из нескольких слов.\n"
            "3. Не создавай вопрос с числовым ответом.\n"
            "4. Вопрос должен иметь один однозначный правильный ответ.\n"
            "5. Не повторяй предыдущие вопросы.\n"
            "6. В accepted_answers укажи только правильные варианты написания.\n"
            "7. Не добавляй близкие по теме, но неправильные ответы.\n\n"
            "Предыдущие вопросы:\n"
            f"{previous_questions}\n\n"
            "Верни только корректный JSON без Markdown:\n"
            "{\n"
            '  "question": "Текст вопроса",\n'
            '  "correct_answer": "Основной правильный ответ",\n'
            '  "accepted_answers": ["вариант 1", "вариант 2"],\n'
            '  "explanation": "Короткое объяснение"\n'
            "}"
        ),
    })

    response = await chat_gpt.request(quiz_message, bot)
    return parse_quiz_response(response)