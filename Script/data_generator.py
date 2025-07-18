#!/usr/bin/env python3
"""
Simplified Tech Company Data Generator
Creates realistic but simple email and calendar data
"""

import json
import random
from datetime import datetime, timedelta
from faker import Faker
import os

fake = Faker()

# Simple company structure
PEOPLE = [
    'john.doe', 'sarah.chen', 'mike.johnson', 'priya.patel', 'alex.kim',
    'emma.davis', 'raj.sharma', 'lisa.brown', 'tom.garcia', 'maya.singh',
    'chris.taylor', 'anna.white', 'nicole.thompson', 'james.clark',
    'sophia.rodriguez', 'daniel.lewis', 'william.king', 'amanda.scott',
    'tyler.green', 'jessica.adams', 'david.wilson', 'jennifer.lee',
    'kevin.martinez', 'rebecca.moore', 'mark.anderson', 'robert.jackson'
]

TEAMS = ['engineering', 'product', 'design', 'hr', 'marketing', 'legal', 'devops']

TOPICS = [
    'code review', 'sprint planning', 'standup', 'interview', 'onboarding',
    'performance review', 'project update', 'bug fix', 'feature request',
    'meeting request', 'training', 'deployment', 'design review', 'demo'
]

MEETING_TYPES = ['standup', 'sprint planning', 'interview', 'one-on-one', 'demo', 'review']

LOCATIONS = ['Conference Room A', 'Conference Room B', 'Zoom', 'Meeting Room', 'Office']

def random_date(days_back=30, days_forward=30):
    """Generate random date within range"""
    start = datetime.now() - timedelta(days=days_back)
    end = datetime.now() + timedelta(days=days_forward)
    return fake.date_time_between(start_date=start, end_date=end)

def generate_emails(count=200):
    """Generate simple but realistic emails"""
    emails = []
    
    for i in range(count):
        sender = random.choice(PEOPLE)
        recipients = random.sample([p for p in PEOPLE if p != sender], random.randint(1, 3))
        cc = random.sample([p for p in PEOPLE if p != sender and p not in recipients], 
                          random.randint(0, 2)) if random.random() < 0.3 else []
        
        topic = random.choice(TOPICS)
        team = random.choice(TEAMS)
        
        # More varied subject templates
        subjects = [
            f"RE: {topic.title()}",
            f"Update on {topic}",
            f"Question about {topic}",
            f"Meeting: {topic}",
            f"FW: {topic.title()} - {team} team",
            f"Urgent: {topic}",
            f"Follow-up: {topic}",
            f"Status: {topic}",
            f"Weekly {topic} report",
            f"Action required: {topic}",
            f"Feedback on {topic}",
            f"Proposal for {topic}",
            f"Discussion: {topic}",
            f"{team.title()} team - {topic}",
            f"Next steps for {topic}"
        ]
        
        # More varied and realistic body content
        body_templates = [
            f"Hi team,\n\nI wanted to follow up on the {topic} we discussed earlier. Can you please review and let me know your thoughts?\n\nThanks,\n{sender}",
            f"Hello everyone,\n\nJust a quick update on the {topic} project. We're making good progress and should have an update by tomorrow.\n\nBest regards,\n{sender}",
            f"Hi,\n\nI need your help with the {topic} issue. Could we schedule a meeting to discuss this further?\n\nThanks,\n{sender}",
            f"Team,\n\nGreat work on the {topic} this week! The {team} team is really making excellent progress.\n\nBest,\n{sender}",
            f"Hi everyone,\n\nI have some questions about the {topic} approach. Could someone from the {team} team help clarify?\n\nThanks,\n{sender}",
            f"Hello,\n\nI've completed the {topic} task. Please review when you have a chance and let me know if any changes are needed.\n\nRegards,\n{sender}",
            f"Hi team,\n\nWe need to discuss the {topic} at our next meeting. I'll send out a calendar invite shortly.\n\nThanks,\n{sender}",
            f"Hello,\n\nI'm sharing the latest update on {topic}. Please see the attached document for more details.\n\nBest,\n{sender}"
        ]
        
        body = random.choice(body_templates)
        
        email = {
            'id': f"email_{i+1}",
            'subject': random.choice(subjects),
            'sender': sender,
            'recipients': recipients,
            'cc': cc,
            'timestamp': random_date().isoformat(),
            'body': body,
            'attachments': ['document.pdf'] if random.random() < 0.2 else [],
            'read': random.choice([True, False]),
            'important': random.random() < 0.1,
            'team': team,
            'topic': topic
        }
        
        emails.append(email)
    
    return emails

def generate_calendar_events(count=200):
    """Generate simple but realistic calendar events"""
    events = []
    
    for i in range(count):
        meeting_type = random.choice(MEETING_TYPES)
        team = random.choice(TEAMS)
        topic = random.choice(TOPICS)
        
        organizer = random.choice(PEOPLE)
        attendees = random.sample([p for p in PEOPLE if p != organizer], random.randint(2, 8))
        attendees.append(organizer)  # Add organizer to attendees
        
        start_time = random_date()
        duration = random.choice([30, 60, 90, 120])  # minutes
        end_time = start_time + timedelta(minutes=duration)
        
        # More varied title templates
        titles = [
            f"Daily Standup - {team.title()}",
            f"Sprint Planning - {team.title()}",
            f"{meeting_type.title()} - {topic.title()}",
            f"{team.title()} Team Meeting",
            f"Interview - {topic}",
            f"1:1 Meeting - {topic}",
            f"Demo - {topic}",
            f"Review Meeting - {topic}",
            f"Weekly {team} sync",
            f"Planning session - {topic}",
            f"Discussion: {topic}",
            f"{team.title()} retrospective",
            f"Brainstorming - {topic}",
            f"Training: {topic}",
            f"All hands - {topic}"
        ]
        
        # More varied descriptions
        descriptions = [
            f"Team meeting to discuss {topic} progress and next steps for the {team} team.",
            f"Weekly {meeting_type} session focusing on {topic} and project updates.",
            f"Collaborative discussion about {topic} with the {team} team members.",
            f"Planning and review meeting for {topic} initiatives.",
            f"Regular {team} team sync to cover {topic} and upcoming priorities.",
            f"Working session on {topic} - please come prepared with updates.",
            f"Monthly review of {topic} progress and team objectives.",
            f"Strategy discussion for {topic} implementation."
        ]

        event = {
            'id': f"event_{i+1}",
            'title': random.choice(titles),
            'description': random.choice(descriptions),
            'timestamp': start_time.isoformat(),
            'duration': (duration_minutes := random.choice([15, 30, 45, 60, 90, 120, 150])),
            'location': random.choice(LOCATIONS),
            'attendees': attendees,
            'organizer': organizer,
            'meeting_type': meeting_type,
            'team': team,
            'topic': topic,
            'status': 'confirmed'
        }
        
        events.append(event)
    
    return events

def save_metadata():
    """Save metadata (people, teams, topics, locations) to a JSON file"""
    metadata = {
        "people": sorted(PEOPLE),
        "teams": sorted(TEAMS),
        "topics": sorted(TOPICS),
        "locations": sorted(LOCATIONS),
        "meeting_types": sorted(MEETING_TYPES)
        
    }

    with open("Data/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print("📁 Saved metadata to Data/metadata.json")


def save_data(emails, events):
    """Save data to JSON files"""
    os.makedirs('Data', exist_ok=True)
    
    with open('Data/emails.json', 'w') as f:
        json.dump(emails, f, indent=2)
    
    with open('Data/calendar_events.json', 'w') as f:
        json.dump(events, f, indent=2)
    
    save_metadata()
    
    print(f"✅ Generated {len(emails)} emails and {len(events)} calendar events")
    print("📁 Saved to Data/emails.json and Data/calendar_events.json")

def show_samples(emails, events):
    """Show sample data"""
    print("\n📧 Sample Emails:")
    for i in range(3):
        email = emails[i]
        print(f"  {i+1}. {email['subject']} (from {email['sender']})")
    
    print("\n📅 Sample Calendar Events:")
    for i in range(3):
        event = events[i]
        print(f"  {i+1}. {event['title']} ({len(event['attendees'])} attendees)")
    
    print(f"\n👥 People: {len(PEOPLE)}")
    print(f"🏢 Teams: {', '.join(TEAMS)}")
    print(f"📋 Topics: {len(TOPICS)} different topics")

def main():
    """Generate all sample data"""
    print("🚀 Generating Simple Tech Company Data")
    print("=" * 40)
    
    emails = generate_emails(300)  # Generate 300 emails
    events = generate_calendar_events(300)  # Generate 300 events
    
    save_data(emails, events)
    show_samples(emails, events)
    
    print("\n✅ Phase 1 Complete! Ready for Phase 2 (NLP Processing)")

if __name__ == "__main__":
    main()




# """
# Simplified Tech Company Data Generator
# Creates realistic but simple email and calendar data
# """

# import json
# import random
# from datetime import datetime, timedelta
# from faker import Faker
# import os

# fake = Faker()

# # Simple company structure
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

# MEETING_TYPES = ['standup', 'sprint planning', 'interview', 'one-on-one', 'demo', 'review']

# LOCATIONS = ['Conference Room A', 'Conference Room B', 'Zoom', 'Meeting Room', 'Office']

# def random_date(days_back=30, days_forward=30):
#     """Generate random date within range"""
#     start = datetime.now() - timedelta(days=days_back)
#     end = datetime.now() + timedelta(days=days_forward)
#     return fake.date_time_between(start_date=start, end_date=end)

# def generate_emails(count=300):
#     """Generate simple but realistic emails"""
#     emails = []
    
#     for i in range(count):
#         sender = random.choice(PEOPLE)
#         recipients = random.sample([p for p in PEOPLE if p != sender], random.randint(1, 3))
#         cc = random.sample([p for p in PEOPLE if p != sender and p not in recipients], 
#                           random.randint(0, 2)) if random.random() < 0.3 else []
        
#         topic = random.choice(TOPICS)
#         team = random.choice(TEAMS)
        
#         # Simple subject templates
#         subjects = [
#             f"RE: {topic.title()}",
#             f"Update on {topic}",
#             f"Question about {topic}",
#             f"Meeting: {topic}",
#             f"FW: {topic.title()} - {team} team",
#             f"Urgent: {topic}",
#             f"Follow-up: {topic}",
#             f"Status: {topic}"
#         ]
        
#         email = {
#             'id': f"email_{i+1}",
#             'subject': random.choice(subjects),
#             'sender': sender,
#             'recipients': recipients,
#             'cc': cc,
#             'timestamp': random_date().isoformat(),
#             'body': f"Hi team,\n\nThis is about {topic} for the {team} team.\n\nBest regards,\n{sender}",
#             'attachments': ['document.pdf'] if random.random() < 0.2 else [],
#             'read': random.choice([True, False]),
#             'important': random.random() < 0.1,
#             'team': team,
#             'topic': topic
#         }
        
#         emails.append(email)
    
#     return emails

# def generate_calendar_events(count=300):
#     """Generate simple but realistic calendar events"""
#     events = []
    
#     for i in range(count):
#         meeting_type = random.choice(MEETING_TYPES)
#         team = random.choice(TEAMS)
#         topic = random.choice(TOPICS)
        
#         organizer = random.choice(PEOPLE)
#         attendees = random.sample([p for p in PEOPLE if p != organizer], random.randint(2, 8))
#         attendees.append(organizer)  # Add organizer to attendees
        
#         start_time = random_date()
#         duration = random.choice([30, 60, 90, 120])  # minutes
#         end_time = start_time + timedelta(minutes=duration)
        
#         # Simple title templates
#         titles = [
#             f"Daily Standup - {team.title()}",
#             f"Sprint Planning - {team.title()}",
#             f"{meeting_type.title()} - {topic.title()}",
#             f"{team.title()} Team Meeting",
#             f"Interview - {topic}",
#             f"1:1 Meeting",
#             f"Demo - {topic}",
#             f"Review Meeting - {topic}"
#         ]
        
#         event = {
#             'id': f"event_{i+1}",
#             'title': random.choice(titles),
#             'description': f"Meeting about {topic} for {team} team",
#             'start_time': start_time.isoformat(),
#             'end_time': end_time.isoformat(),
#             'location': random.choice(LOCATIONS),
#             'attendees': attendees,
#             'organizer': organizer,
#             'meeting_type': meeting_type,
#             'team': team,
#             'topic': topic,
#             'status': 'confirmed'
#         }
        
#         events.append(event)
    
#     return events

# def save_data(emails, events):
#     """Save data to JSON files"""
#     os.makedirs('Data', exist_ok=True)
    
#     with open('Data/emails.json', 'w') as f:
#         json.dump(emails, f, indent=2)
    
#     with open('Data/calendar_events.json', 'w') as f:
#         json.dump(events, f, indent=2)
    
#     print(f"✅ Generated {len(emails)} emails and {len(events)} calendar events")
#     print("📁 Saved to Data/emails.json and Data/calendar_events.json")

# def show_samples(emails, events):
#     """Show sample data"""
#     print("\n📧 Sample Emails:")
#     for i in range(3):
#         email = emails[i]
#         print(f"  {i+1}. {email['subject']} (from {email['sender']})")
    
#     print("\n📅 Sample Calendar Events:")
#     for i in range(3):
#         event = events[i]
#         print(f"  {i+1}. {event['title']} ({len(event['attendees'])} attendees)")
    
#     print(f"\n👥 People: {len(PEOPLE)}")
#     print(f"🏢 Teams: {', '.join(TEAMS)}")
#     print(f"📋 Topics: {len(TOPICS)} different topics")

# def main():
#     """Generate all sample data"""
#     print("🚀 Generating Simple Tech Company Data")
#     print("=" * 40)
    
#     emails = generate_emails(200)
#     events = generate_calendar_events(200)
    
#     save_data(emails, events)
#     show_samples(emails, events)
    
#     print("\n✅ Phase 1 Complete! Ready for Phase 2 (NLP Processing)")

# if __name__ == "__main__":
#     main()