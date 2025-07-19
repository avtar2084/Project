# Natural Language Query System

A hybrid NLP-powered natural language query system for retrieving relevant information from structured email and calendar metadata. Users can ask informal, conversational queries (e.g., "email from sarah cc james" or "email by legal team about on-boarding") and get precise results filtered by entities such as people, teams, topics, meeting types, locations, and dates.

## Features

* **Natural Language Understanding**: Supports informal queries using a combination of spaCy-based entity extraction, date parsing (via `dateparser`), and a custom Boolean parser.
* **Intent Classification**: Differentiates between email searches, calendar-event searches, and other query types.
* **Entity Extraction**: Identifies people, teams, topics, meeting types, and locations from user input.
* **Date Handling**: Interprets relative and absolute dates (e.g., "last 3 days", "July 17, 2025").
* **CLI & File Output**: Run queries programmatically or via module invocation, with results printed to CLI and appended to `output.txt`.

## Tech Stack

* Python 3.8+
* [spaCy](https://spacy.io/) for NLP
* [dateparser](https://dateparser.readthedocs.io/) for date interpretation
* Regex and custom Boolean parser for complex query logic

## Getting Started

1. **Clone the repository**:

   ```bash
   git clone https://github.com/avtar2084/Natural-Language-Qery.git
   cd Natural-Language-Qery
   ```


2. **Generate or prepare data**:

   * To simulate data, run:

     ```bash
     python Script/data_generator.py
     ```
   * Or use the provided sample data in `Data/`:

     * `metadata.json`: Reference metadata for entity matching
     * `emails.json`: Sample email metadata
     * `calendar_events.json`: Sample calendar entries

3. **Run a query**:
   Invoke the query processor module:

   ```bash
   python -B -m src.query.query_processor
   ```

## Project Structure

```
Natural-Language-Qery/
├── .git/                   # Git repository metadata
├── .vscode/                # Editor settings (optional)
├── Data/                   # Sample metadata and event data
│   ├── metadata.json
│   ├── emails.json
│   └── calendar_events.json
├── Script/                 # Data simulation scripts
│   └── data_generator.py   # Generates sample metadata and event data
├── src/                    # Core modules
│   ├── nlp/                # NLP components
│   │   ├── boolean_parser.py
│   │   ├── date_parser.p    # Parses the data in User Query
│   │   ├── entity_extractor.py #extract the entity in user Query
│   │   └── intent_classifier.py #Clasifiy if query is for email or calander
│   └── query/              # Query processing and interfaces
│       └── query_processor.py
├── output.txt              # Accumulated query results
└── README.md               # Project overview and instructions
```

