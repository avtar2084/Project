import re

class IntentClassifier:
    EMAIL_KEYWORDS = [
        "email", "emails", "inbox", "mail", "message", "messages", "attachments"
    ]

    CALENDAR_KEYWORDS = [
        "meeting", "meetings", "event", "events", "call", "calls",
        "appointment", "calendar", "schedule"
    ]

    @classmethod
    def classify_intent(cls, query: str) -> str:
        query = query.lower()

        email_score = sum(1 for word in cls.EMAIL_KEYWORDS if word in query)
        calendar_score = sum(1 for word in cls.CALENDAR_KEYWORDS if word in query)

        if email_score > calendar_score:
            return "email"
        elif calendar_score > email_score:
            return "calendar"
        elif email_score == calendar_score and email_score > 0:
            return "ambiguous"
        else:
            return "unknown"

# # Example usage:
# classifier = IntentClassifier()
# print(classifier.classify_intent("code review meeting on 14 July 2025"))
# print(classifier.classify_intent("email from sarah to james"))  