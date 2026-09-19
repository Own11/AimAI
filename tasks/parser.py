import re
from datetime import timedelta
from django.utils import timezone


def parse_task_text(text):
    """Extract a small task batch from natural language without an API key."""
    lines = [line.strip(' -•\t') for line in text.splitlines() if line.strip()]
    result = []
    for line in lines:
        match = re.search(r'(.+?)(?:\s+через\s+(\d+)\s*(час|дн|день|дня))?$', line, re.I)
        title = (match.group(1) if match else line).strip()
        amount = int(match.group(2)) if match and match.group(2) else 24
        unit = match.group(3) if match else 'час'
        hours = amount * (24 if (unit or '').lower().startswith(('д',)) else 1)
        result.append({'title': title, 'due_at': timezone.now() + timedelta(hours=hours)})
    return result
