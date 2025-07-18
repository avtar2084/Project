import spacy
import json
from typing import Dict, Set
import re

class MeetingEntityExtractor:
    def __init__(self, metadata_file_path: str = None, metadata_dict: dict = None):
        """
        Initialize the extractor with metadata
        
        Args:
            metadata_file_path: Path to metadata.json file
            metadata_dict: Dictionary containing metadata (alternative to file)
        """
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Please install spaCy English model: python -m spacy download en_core_web_sm")
            raise
        
        metadata_file_path="Data/metadata.json"
        # Load metadata
        if metadata_file_path:
            with open(metadata_file_path, 'r') as f:
                self.metadata = json.load(f)
        elif metadata_dict:
            self.metadata = metadata_dict
        else:
            raise ValueError("Either metadata_file_path or metadata_dict must be provided")
        
        # Preprocess metadata for better matching
        self.processed_metadata = self._preprocess_metadata()
    
    def _preprocess_metadata(self) -> Dict:
        """Preprocess metadata to handle variations and create lookup dictionaries"""
        processed = {
            'people': {},
            'teams': {},
            'topics': {},
            'meeting_types': {},
            'locations': {}
        }
        
        # Process people - extract first names and create variations
        for person in self.metadata['people']:
            name_parts = person.split('.')
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            # Add variations for matching
            processed['people'][person.lower()] = person
            processed['people'][first_name.lower()] = person
            if last_name:
                processed['people'][last_name.lower()] = person
                processed['people'][f"{first_name} {last_name}".lower()] = person
        
        # Process other categories
        for category in ['teams', 'topics', 'meeting_types']:
            for item in self.metadata[category]:
                processed[category][item.lower()] = item
                # Add variations (e.g., "code review" -> "review")
                if category == 'topics' and ' ' in item:
                    words = item.split()
                    for word in words:
                        if len(word) > 3:  # Avoid short words
                            processed[category][word.lower()] = item
        
        # Process locations with variations
        for location in self.metadata['locations']:
            processed['locations'][location.lower()] = location
            # Handle common variations
            if "conference room" in location.lower():
                room_letter = location.split()[-1]
                processed['locations'][f"conference {room_letter}".lower()] = location
                processed['locations'][f"room {room_letter}".lower()] = location
        
        return processed
    
    def extract_entities(self, text: str) -> Dict[str, Set[str]]:
        """
        Extract entities from text using spaCy and metadata matching
        
        Args:
            text: Input text to extract entities from
            
        Returns:
            Dictionary with extracted entities for each category
        """
        # Process text with spaCy (keep original case for NER)
        doc = self.nlp(text)
        text_lower = text.lower()
        
        # Initialize result sets
        result = {
            'people': set(),
            'teams': set(),
            'topics': set(),
            'meeting_types': set(),
            'locations': set()
        }
        
        # Extract people using spaCy NER (with original case)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                person_text = ent.text.lower()
                if person_text in self.processed_metadata['people']:
                    result['people'].add(self.processed_metadata['people'][person_text])
                else:
                    # If not in metadata, add the detected name as-is (lowercase)
                    result['people'].add(person_text)
        
        # Additional pattern matching for people (fallback)
        # Look for names that spaCy might have missed
        words = text_lower.split()
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in self.processed_metadata['people']:
                result['people'].add(self.processed_metadata['people'][clean_word])
        
        # Extract other entities using keyword matching
        # Match teams
        for key, value in self.processed_metadata['teams'].items():
            if key in text_lower:
                result['teams'].add(value)
        
        # Match topics (be more specific to avoid false positives)
        for key, value in self.processed_metadata['topics'].items():
            # Use word boundaries for better matching
            if re.search(r'\b' + re.escape(key) + r'\b', text_lower):
                result['topics'].add(value)
        
        # Match meeting types
        for key, value in self.processed_metadata['meeting_types'].items():
            if re.search(r'\b' + re.escape(key) + r'\b', text_lower):
                result['meeting_types'].add(value)
        
        # Match locations
        for key, value in self.processed_metadata['locations'].items():
            if key in text_lower:
                result['locations'].add(value)
        
        return result
    
    def extract_and_display(self, text: str) -> None:
        """Extract entities and display results"""
        entities = self.extract_entities(text)
        print(f"Input: {text}")
        print("Extracted entities:")
        for category, items in entities.items():
            print(f"  '{category}': {items}")
        print()
# Example usage
if __name__ == "__main__":
    # Initialize extractor with metadata file
    extractor = MeetingEntityExtractor()
    
    # Test examples
    test_queries = [
        "email from sophia?",
        # "Let's have a standup meeting with the engineering team in Zoom",
        # "Schedule an interview with Sarah Chen in Meeting Room",
        # "Need to do a demo with the product team",
        # "Performance review with Maya Singh in Office"
    ]
    
    for query in test_queries:
        extractor.extract_and_display(query)




# import spacy
# import re
# from typing import Dict, Any
# from difflib import get_close_matches

# # Load spaCy NLP pipeline
# nlp = spacy.load("en_core_web_sm")

# # Use your actual constants
# PEOPLE = [
#     'john.doe', 'sarah.chen', 'mike.johnson', 'priya.patel', 'alex.kim',
#     'emma.davis', 'raj.sharma', 'lisa.brown', 'tom.garcia', 'maya.singh',
#     'chris.taylor', 'anna.white', 'nicole.thompson', 'james.clark',
#     'sophia.rodriguez', 'daniel.lewis', 'william.king', 'amanda.scott',
#     'tyler.green', 'jessica.adams', 'david.wilson', 'jennifer.lee',
#     'kevin.martinez', 'rebecca.moore', 'mark.anderson', 'robert.jackson'
# ]

# TEAMS = ['engineering', 'product', 'design', 'hr', 'marketing', 'legal', 'devops']

# TOPICS = [
#     'code review', 'sprint planning', 'standup', 'interview', 'onboarding',
#     'performance review', 'project update', 'bug fix', 'feature request',
#     'meeting request', 'training', 'deployment', 'design review', 'demo'
# ]

# LOCATIONS = ['conference room a', 'conference room b', 'zoom', 'meeting room', 'office']

# def normalize_name(name: str) -> str:
#     return name.strip().lower().replace(" ", ".")


# def fuzzy_match_people_by_partial_name(name: str) -> list:
#     norm_token = name.strip().lower()
#     matches = [
#         person for person in PEOPLE
#         if norm_token in person.lower().split(".")  # match either first or last name
#     ]
#     return matches

# #print(matches)

# # def fuzzy_match_person(name: str) -> str:
# #     norm_name = normalize_name(name)
# #     match = get_close_matches(norm_name, PEOPLE, n=1, cutoff=0.8)
# #     return match[0] if match else ""

# def match_phrases(text: str, phrases: list) -> list:
#     """Extract known multi-word phrases from text (e.g., 'code review')."""
#     found = []
#     text_lower = text.lower()
#     for phrase in phrases:
#         if phrase in text_lower:
#             found.append(phrase)
#     return found

# def extract_entities(query: str) -> Dict[str, Any]:
#     """
#     Extract structured entities from a natural language query.
#     Input: user query string
#     Output: dict with people, teams, topics, locations
#     """
#     doc = nlp(query)
#     people = set()
#     teams = set()
#     topics = set()
#     locations = set()

#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             matched = fuzzy_match_people_by_partial_name(ent.text)
#             if matched:
#                 people.update(matched)

#         elif ent.label_ in ["ORG", "GPE", "NORP", "LOC"]:
#             val = ent.text.lower()
#             if val in TEAMS:
#                 teams.add(val)
#             elif val in LOCATIONS:
#                 locations.add(val)

#     # Fallback: also check individual tokens (helps with partial first names like "john")
#     for token in query.lower().split():
#         people.update(fuzzy_match_people_by_partial_name(token))

#     # Keyword fallback
#     tokens = set(re.findall(r'\b\w+\b', query.lower()))
#     for word in tokens:
#         if word in TEAMS:
#             teams.add(word)
#         if word in LOCATIONS:
#             locations.add(word)

#     # Match full phrases for topics (e.g., "code review")
#     topics.update(match_phrases(query, TOPICS))

#     return {
#         "people": sorted(people),
#         "teams": sorted(teams),
#         "topics": sorted(topics),
#         "locations": sorted(locations),
#     }

# # Example usage
# if __name__ == "__main__":
#     query = "Can you schedule a code review with John in conference room A?"
#     entities = extract_entities(query)
#     print(entities)
#     # Output: {'people': ['john.doe'], 'teams': [], 'topics': ['code review'], 'locations': ['conference room a']}
