import json
import os
import re
from src.nlp.entity_extractor import MeetingEntityExtractor
from src.nlp.intent_classifier import IntentClassifier
from src.nlp.date_parser import DateParser
from src.nlp.boolean_parser import BooleanParser

# Load source data
with open("Data/emails.json", "r", encoding="utf-8") as f:
    EMAILS = json.load(f)

with open("Data/calendar_events.json", "r", encoding="utf-8") as f:
    CALENDAR_EVENTS = json.load(f)

# Initialize extractors
entity_extractor = MeetingEntityExtractor()
dp = DateParser()
boolean_parser = BooleanParser()
classifier = IntentClassifier()
intent_label = ""


def process_query(user_query: str):
    if not user_query or not user_query.strip():
        return []

    query_lower = user_query.lower()
    intent = classifier.classify_intent(user_query)
    print(f"Intent classified as: {intent} for query: {user_query}")

    source_data = EMAILS if intent == "email" else CALENDAR_EVENTS

    # print(f"[DEBUG] DateParser reference time: {dp.reference}")
    # print(f"[DEBUG] DateParser settings: {dp.settings}")
    entities = entity_extractor.extract_entities(user_query)
    print(f"[DEBUG] Extracted entities: {entities}")

    date_info = dp.parse(user_query)
    print(f"[DEBUG] Raw date_info from parser: {repr(date_info)}")
    # print(f"[DEBUG] Type of date_info: {type(date_info)}")

    if isinstance(date_info, str) and re.search(r'\b(from|since)\s+\w+\s+\d{4}\s+(to|until)\s+\w+\s+\d{4}\b', query_lower):
        all_dates = dp.extract_all_dates(user_query)
        if len(all_dates) >= 2:
            date_info = all_dates
    # print(f"[DEBUG] Raw date_info from parser: {repr(date_info)}")
    # print(f"[DEBUG] Type of date_info: {type(date_info)}")
    
    def match_fn(term: str) -> set[int]:
        if term == "__ALL__":
            return set(range(len(source_data)))

        if term.startswith("from:"):
            person = term.split(":", 1)[1].lower()
            print(f"[DEBUG] Searching for person '{person}' in senders")
            return {i for i, item in enumerate(source_data)
                    if person in item.get("sender", "").lower()}

        elif term.startswith("to:"):
            person = term.split(":", 1)[1].lower()
            return {i for i, item in enumerate(source_data)
                    if any(person in r.lower() for r in item.get("recipients", []))}

        elif term.startswith("cc:"):
            person = term.split(":", 1)[1].lower()
            return {i for i, item in enumerate(source_data)
                    if any(person in c.lower() for c in item.get("cc", []))}

        matches = set()
        for i, item in enumerate(source_data):
            term_lower = term.lower()
            if intent == "email":
                if (term_lower in item.get("sender", "").lower() or
                    any(term_lower in r.lower() for r in item.get("recipients", [])) or
                    any(term_lower in c.lower() for c in item.get("cc", [])) or
                    term_lower in item.get("subject", "").lower() or
                    term_lower in item.get("topic", "").lower() or
                    term_lower in item.get("team", "").lower() or
                    term_lower in item.get("body", "").lower()):
                    matches.add(i)
                    
            else:
                if (any(term_lower in a.lower() for a in item.get("attendees", [])) or
                    term_lower in item.get("title", "").lower() or
                    term_lower in item.get("description", "").lower() or
                    term_lower in item.get("topic", "").lower() or
                    # term_lower in item.get("meeting_type", "").lower() or
                    term_lower in item.get("team", "").lower() or
                    term_lower in item.get("location", "").lower()):
                    matches.add(i)
        
        
        return matches
    
    # print(f"[DEBUG] Matches for 'devops': {match_fn('devops')}")
    # print(f"[DEBUG] Matches for 'Zoom': {match_fn('Zoom')}")
    
    
    
    # intent_label = intent if intent in {"email", "calendar"} else "result"
    # print(f"intent: {intent_label}")
    

    search_terms = []
    contextual_filters = {}
    has_date_range_pattern = bool(re.search(r'\b(from|since)\s+\w+\s+\d{4}\s+(to|until)\s+\w+\s+\d{4}\b', query_lower))

    from_match = re.search(r'\bfrom\s+([a-zA-Z.]+)(?:\s+(?:to|until|since)\s+\w+\s+\d{4})?', query_lower)
    if from_match and not has_date_range_pattern:
        person = from_match.group(1)
        matched_person = next((p for p in entities.get('people', []) if person.lower() in p.lower()), person)
        contextual_filters['from'] = matched_person
    elif from_match and has_date_range_pattern:
        person_match = re.search(r'\bfrom\s+([a-zA-Z.]+)(?=\s+(?:from|since))', query_lower)
        if person_match:
            person = person_match.group(1)
            matched_person = next((p for p in entities.get('people', []) if person.lower() in p.lower()), person)
            contextual_filters['from'] = matched_person

    to_match = re.search(r'\bto\s+([a-zA-Z.]+)(?!\s+\d{4})', query_lower)
    if to_match and not has_date_range_pattern:
        contextual_filters['to'] = to_match.group(1)

    cc_match = re.search(r'\bcc\s+([a-zA-Z.]+)', query_lower)
    if cc_match:
        contextual_filters['cc'] = cc_match.group(1)

    filtered_data = []
    if contextual_filters:
        matching_indices = set(range(len(source_data)))
        for filter_type, person in contextual_filters.items():
            if filter_type == 'from':
                matching_indices &= match_fn(f"from:{person}")
            elif filter_type == 'to':
                matching_indices &= match_fn(f"to:{person}")
            elif filter_type == 'cc':
                matching_indices &= match_fn(f"cc:{person}")
        print(f"[DEBUG] Final matching indices after intersection: {matching_indices}")
        filtered_data = [source_data[i] for i in matching_indices]
    else:
        for entity_set in entities.values():
            search_terms.extend(entity_set)

        if not search_terms:
            stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "show", "me", "find", "get", "any", "all", "have", "do", "i", "my", "are", "is", "was", "were", "been", "be", "will", "would", "could", "should"}
            query_words = [w.strip(".,!?") for w in query_lower.split() if w.strip(".,!?") not in stop_words and len(w.strip(".,!?")) > 2]
            search_terms.extend(query_words)

        print(f"[DEBUG] Final search_terms before matching: {search_terms}")

        # OR Logic
        # if search_terms:
        #     matching_indices = set()
        #     for term in search_terms:
        #         matching_indices.update(match_fn(term))

        if search_terms:
            matching_indices = set(range(len(source_data)))
            for term in search_terms:
                matching_indices &= match_fn(term)

            if any(op in query_lower for op in ["and", "or", "not"]):
                try:
                    postfix_expr = boolean_parser.parse(user_query)
                    matching_indices = boolean_parser.evaluate(postfix_expr, match_fn)
                except:
                    pass

            filtered_data = [source_data[i] for i in matching_indices]
        else:
            filtered_data = source_data

        # print(f"[DEBUG] Raw query: '{user_query}'")
        # print(f"[DEBUG] Query lower: '{query_lower}'")
        # print(f"[DEBUG] Contextual filters: {contextual_filters}")
        # print(f"[DEBUG] Entities extracted: {entities}")

    # for filter_type, person in contextual_filters.items():
    #     print(f"[DEBUG] Applying {filter_type}:{person}")
    #     filter_results = match_fn(f"{filter_type}:{person}")
    #     print(f"[DEBUG] Found {len(filter_results)} items")
    #     matching_indices &= filter_results


    if isinstance(date_info, tuple) and len(date_info) == 2:
        print(f"[DEBUG] Applying date range filter: {date_info}")
        start_date, end_date = date_info
        filtered_data = [
            item for item in filtered_data
            if item.get("timestamp") and len(item["timestamp"]) >= 10 and
               (start_date is None or item["timestamp"][:10] >= start_date) and
               (end_date is None or item["timestamp"][:10] <= end_date)
        ]
    elif isinstance(date_info, list) and len(date_info) >= 2:
        print(f"[DEBUG] Applying date list filter: {date_info}")
        start_date, end_date = date_info[0], date_info[-1]
        filtered_data = [
            item for item in filtered_data
            if item.get("timestamp") and len(item["timestamp"]) >= 10 and
               start_date <= item["timestamp"][:10] <= end_date
        ]
    elif isinstance(date_info, str) and date_info:
        print(f"[DEBUG] Applying single date filter: {date_info}")
        filtered_data = [
            item for item in filtered_data
            if item.get("timestamp") and len(item["timestamp"]) >= 10 and
               item["timestamp"][:10] == date_info
        ]
    elif isinstance(date_info, list) and len(date_info) == 1:
        print(f"[DEBUG] Applying single date from list filter: {date_info}")
        filtered_data = [
            item for item in filtered_data
            if item.get("timestamp") and len(item["timestamp"]) >= 10 and
               item["timestamp"][:10] == date_info[0]
        ]

    # print(f"[DEBUG] Final filtered_data length: {len(filtered_data)}")
    # print(f"[DEBUG] Date info: {date_info}")
    if filtered_data:
        print(f"[DEBUG] First item timestamp: {filtered_data[0].get('timestamp', 'No timestamp')}")
    return filtered_data


def display_results(results, intent):
    if not results:
        print("[INFO] No matching results found.")
        return

    print(f"🔍 Query Intent: {intent}")
    print(f"\n📋 Found {len(results)} matching {intent}(s):\n")
    for i, item in enumerate(results, 1):
        print(f"--- Result {i} ---")
        if intent == "email":
            print(f"From: {item.get('sender', 'Unknown')}")
            print(f"To: {', '.join(item.get('recipients', []))}")
            print(f"Subject: {item.get('subject', 'No subject')}")
            print(f"Date: {item.get('timestamp', 'Unknown')}")
            if item.get('cc'):
                print(f"CC: {', '.join(item.get('cc', []))}")
            content = item.get('body', 'No content')
            print(f"Content: {content[:100]}{'...' if len(content) > 100 else ''}")
        else:
            print(f"Title: {item.get('title', 'No title')}")
            print(f"Date: {item.get('timestamp', 'Unknown')}")
            print(f"Attendees: {', '.join(item.get('attendees', []))}")
            print(f"Location: {item.get('location', 'No location')}")
            description = item.get('description', 'No description')
            print(f"Description: {description[:100]}{'...' if len(description) > 100 else ''}")
        print()


if __name__ == "__main__":
    print("📬 Natural Language Query System (type empty input to exit)\n")
    while True:
        query = input("Ask: ")
        if not query.strip():
            break
        try:
            results = process_query(query)
            intent = classifier.classify_intent(query)
            display_results(results, intent)
        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")
            import traceback
            traceback.print_exc()
            print("Please try rephrasing your query.")
