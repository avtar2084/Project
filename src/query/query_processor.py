import json
from src.nlp.entity_extractor import MeetingEntityExtractor
from src.nlp.intent_classifier import classify_intent
from src.nlp.date_parser import parse_date_range
from src.nlp.boolean_parser import BooleanParser, build_match_function

# Initialize extractor with hardcoded metadata path
entity_extractor = MeetingEntityExtractor()
boolean_parser = BooleanParser()

def process_query(query: str):
    print(f"\n📬 Natural Language Query System (type empty input to exit)\n")
    
    # 1. Classify intent
    intent = classify_intent(query)
    print(f"[INFO] Intent: {intent}")

    # 2. Extract entities
    entities = entity_extractor.extract_entities(query)
    print(f"[INFO] Entities: {entities}")

    # 3. Parse date range
    date_range = parse_date_range(query)
    print(f"[INFO] Date range: {date_range}")

    # 4. Load source data based on intent
    if intent == "email":
        with open("Data/emails.json") as f:
            source_data = json.load(f)
    elif intent == "calendar":
        with open("Data/calendar_events.json") as f:
            source_data = json.load(f)
    else:
        print("[WARN] Unsupported intent — no data source available.")
        return []

    # 5. Build search tokens from canonical values
    tokens = []
    for key in ["people", "topics", "teams", "meeting_types", "locations"]:
        tokens.extend(entities.get(key, []))

    # 6. Build Boolean query string (default: OR chain)
    boolean_query = " OR ".join(tokens) if tokens else query
    print(f"[INFO] Boolean query: {boolean_query}")

    # 7. Parse Boolean query and create match function
    postfix = boolean_parser.to_postfix(boolean_query)
    match_fn = build_match_function(postfix)

    # 8. Filter results
    results = []
    for item in source_data:
        if match_fn([item]):
            if date_range:
                timestamp = item.get("timestamp", "")
                if timestamp and not (date_range[0] <= timestamp[:10] <= date_range[1]):
                    continue
            results.append(item)

    if results:
        print(f"[INFO] {len(results)} result(s) found.")
    else:
        print("[INFO] No matching results found.")

    return results

#example usage
if __name__ == "__main__":
    
    user_input = "email from sophia"
    process_query(user_input.strip())
