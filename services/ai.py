from collections import Counter
import json
import os

from django.db import transaction

from insights.models import Insight
from tasks.models import FailureLog
from interventions.models import Intervention


def _fallback_analysis(failures):
    tags = Counter(tag for failure in failures for tag in failure.tags)
    if not tags:
        return {
            'title': 'Нужны ещё данные',
            'body': 'Запиши ещё несколько причин — тогда AimAI сможет найти повторяющийся паттерн.',
            'intervention_title': 'Короткий разбор причины',
            'intervention_description': 'После следующего пропуска запиши одну конкретную причину и первый маленький шаг.',
        }
    tag, count = tags.most_common(1)[0]
    suggestions = {
        'усталость': ('Слишком высокая нагрузка', 'Перенеси задачу на окно с большей энергией и сократи первый шаг до 10 минут.'),
        'отвлёкся': ('Среда мешает фокусу', 'Запусти 25-минутную фокус-сессию, убери уведомления и оставь открытую только нужную вкладку.'),
        'неясно': ('Задача недостаточно конкретна', 'Перепиши задачу как один наблюдаемый результат, который можно закончить за 25 минут.'),
    }
    title, intervention = suggestions.get(tag, ('Повторяющаяся причина: ' + tag, 'Перед стартом подготовь защитное действие против причины «' + tag + '».'))
    return {
        'title': title,
        'body': f'Причина «{tag}» встретилась {count} раз(а). Это наиболее заметный паттерн в истории пропусков.',
        'intervention_title': 'Попробовать на следующем цикле',
        'intervention_description': intervention,
    }


def _llm_analysis(failures):
    """Use Gemini when configured; failures stay local and use the fallback."""
    if not os.getenv('GEMINI_API_KEY'):
        return None
    from google import genai
    from google.genai import types

    payload = [{'tags': failure.tags, 'text': failure.text} for failure in failures]
    schema = {
        'type': 'OBJECT',
        'properties': {
            'title': {'type': 'STRING'}, 'body': {'type': 'STRING'},
            'intervention_title': {'type': 'STRING'}, 'intervention_description': {'type': 'STRING'},
        },
        'required': ['title', 'body', 'intervention_title', 'intervention_description'],
    }
    response = genai.Client(api_key=os.environ['GEMINI_API_KEY']).models.generate_content(
        model=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
        contents='Ты коуч AimAI. Найди повторяющийся паттерн в причинах невыполнения задач. Верни конкретное, маленькое предложение без стыда. Данные: ' + json.dumps(payload, ensure_ascii=False),
        config=types.GenerateContentConfig(response_mime_type='application/json', response_schema=schema),
    )
    return json.loads(response.text)


@transaction.atomic
def analyze_task(task):
    failures = list(FailureLog.objects.filter(task=task))
    try:
        result = _llm_analysis(failures) or _fallback_analysis(failures)
    except Exception:
        result = _fallback_analysis(failures)
    insight = Insight.objects.create(user=task.owner, title=result['title'], body=result['body'], confidence=0.65 if failures else 0.1)
    intervention = Intervention.objects.create(task=task, title=result['intervention_title'], description=result['intervention_description'])
    return insight, intervention
