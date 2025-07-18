#!/usr/bin/env python3
"""
Simple Data Validator
Quick check of generated data quality
"""

import json
from collections import Counter

def load_data():
    """Load generated data"""
    try:
        with open('Data/emails.json', 'r') as f:
            emails = json.load(f)
        with open('Data/calendar_events.json', 'r') as f:
            events = json.load(f)
        return emails, events
    except FileNotFoundError:
        print("❌ Data files not found. Run 'python scripts/generate_data.py' first")
        return None, None

def validate_data():
    """Simple validation of the generated data"""
    emails, events = load_data()
    if not emails or not events:
        return
    
    print("📊 Data Validation Report")
    print("=" * 30)
    
    # Basic counts
    print(f"📧 Emails: {len(emails)}")
    print(f"📅 Events: {len(events)}")
    
    # Top senders
    senders = Counter(email['sender'] for email in emails)
    print(f"\n📤 Top Email Senders:")
    for sender, count in senders.most_common(3):
        print(f"  • {sender}: {count} emails")
    
    # Popular topics
    topics = Counter(email['topic'] for email in emails)
    print(f"\n📋 Popular Email Topics:")
    for topic, count in topics.most_common(3):
        print(f"  • {topic}: {count} emails")
    
    # Team distribution
    teams = Counter(email['team'] for email in emails)
    print(f"\n🏢 Team Distribution (Emails):")
    for team, count in teams.most_common():
        print(f"  • {team}: {count} emails")
    
    # Meeting types
    meeting_types = Counter(event['meeting_type'] for event in events)
    print(f"\n🤝 Meeting Types:")
    for mtype, count in meeting_types.most_common():
        print(f"  • {mtype}: {count} events")
    
    # Sample queries to test
    print(f"\n🔍 Sample Queries to Test:")
    sample_queries = [
        "emails from john.doe",
        "meetings with sarah.chen",
        "calendar events about interview",
        "emails from engineering team",
        "meetings tomorrow",
        "calendar events in Conference Room A",
        "emails about code review",
        "meetings with product team"
    ]
    
    for i, query in enumerate(sample_queries, 1):
        print(f"  {i}. {query}")
    
    print(f"\n✅ Data validation complete!")

if __name__ == "__main__":
    validate_data()