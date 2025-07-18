import re

EMAIL_KEYWORDS = [
    "email", "emails", "inbox", "mail", "message", "messages", "attachments"
]

CALENDAR_KEYWORDS = [
    "meeting", "meetings", "event", "events", "call", "calls",
    "appointment", "calendar", "schedule"
]

def classify_intent(query: str) -> str:
    query = query.lower()

    email_score = sum(1 for word in EMAIL_KEYWORDS if word in query)
    calendar_score = sum(1 for word in CALENDAR_KEYWORDS if word in query)

    if email_score > calendar_score:
        return "email"
    elif calendar_score > email_score:
        return "calendar"
    elif email_score == calendar_score and email_score > 0:
        return "ambiguous"
    else:
        return "unknown"

# print(classify_intent("Show me  with attachments from last week"))
# print(classify_intent("Do I have any meetings tomorrow with HR?"))  