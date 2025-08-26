#!/usr/bin/env python3

import sys
import os
import uuid
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def explain_search_engine():
    """Explain and demonstrate what the search engine does"""
    print("🔍 POLYGLOT MEETING ASSISTANT - SEARCH ENGINE EXPLANATION")
    print("=" * 80)
    
    print("""
🤔 WHAT IS THIS SEARCH ENGINE?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is a SEMANTIC SEARCH ENGINE that helps you find information across all your meetings.
Instead of just matching keywords, it understands the MEANING of what you're looking for.

🧠 HOW IT WORKS:
1. CONVERTS TEXT TO VECTORS: Uses AI to turn meeting content into numerical representations
2. STORES IN FAISS DATABASE: Fast vector similarity search database
3. SEMANTIC MATCHING: Finds content that means the same thing, even with different words
4. RELEVANCE SCORING: Ranks results by how well they match your query

🎯 WHAT CAN YOU SEARCH?
• Meeting transcripts (what people said)
• Summaries (key points)
• Action items (tasks assigned)
• Decisions made
• Timeline items (deadlines, milestones)
    """)
    
    try:
        from models.search import MeetingSearchEngine
        
        # Initialize search engine
        print("\n🚀 INITIALIZING SEARCH ENGINE...")
        search_engine = MeetingSearchEngine()
        print("✅ Search engine ready!")
        
        # Create a sample meeting to demonstrate
        print("\n📝 ADDING A SAMPLE MEETING...")
        sample_meeting = {
            'id': str(uuid.uuid4()),
            'title': 'Product Launch Strategy Meeting',
            'date': datetime.now().isoformat(),
            'transcript': '''
            Sarah (CEO): We need to finalize our product launch strategy for the new AI assistant.
            
            Mike (CTO): The technical infrastructure is ready. We can handle 100,000 users on day one.
            
            Lisa (Marketing): I've prepared a comprehensive marketing campaign with social media and email outreach.
            
            John (Sales): We have 50 enterprise customers already interested in early access.
            
            Sarah: Great! Let's set the launch date for next Friday. Mike, can you ensure the servers are scaled?
            
            Mike: I'll coordinate with the DevOps team to prepare auto-scaling configurations.
            
            Lisa: We should also prepare press releases for tech blogs and industry publications.
            
            John: I'll reach out to our enterprise contacts for testimonials and case studies.
            ''',
            'participants': ['Sarah', 'Mike', 'Lisa', 'John'],
            'summary': 'Product launch strategy meeting to finalize AI assistant launch, technical readiness, marketing campaign, and enterprise customer engagement.',
            'action_items': [
                {'text': 'Mike will coordinate with DevOps team for auto-scaling', 'assignee': 'Mike', 'deadline': 'This week'},
                {'text': 'Lisa will prepare press releases for tech publications', 'assignee': 'Lisa', 'deadline': 'Before launch'},
                {'text': 'John will collect testimonials from enterprise customers', 'assignee': 'John', 'deadline': 'Next week'}
            ],
            'key_decisions': [
                'Set product launch date for next Friday',
                'Approved marketing campaign with social media and email',
                'Decided to target enterprise customers for early access'
            ],
            'timelines': [
                {'timeline': 'Next Friday', 'context': 'Product launch date', 'type': 'milestone'},
                {'timeline': 'This week', 'context': 'Server scaling preparation', 'type': 'deadline'}
            ]
        }
        
        # Add to search index
        success = search_engine.add_meeting(sample_meeting)
        if success:
            print("✅ Sample meeting added to search index!")
            
            print("\n🔍 NOW LET'S DEMONSTRATE SEMANTIC SEARCH:")
            print("=" * 60)
            
            # Demonstrate different types of searches
            demo_queries = [
                {
                    'query': 'server infrastructure and scaling',
                    'explanation': 'Looking for technical infrastructure topics'
                },
                {
                    'query': 'marketing and promotion activities',
                    'explanation': 'Finding marketing-related discussions'
                },
                {
                    'query': 'customer testimonials and feedback',
                    'explanation': 'Searching for customer-related content'
                },
                {
                    'query': 'deadlines and important dates',
                    'explanation': 'Finding timeline and deadline information'
                }
            ]
            
            for i, demo in enumerate(demo_queries, 1):
                print(f"\n{i}. QUERY: '{demo['query']}'")
                print(f"   PURPOSE: {demo['explanation']}")
                print("   " + "-" * 50)
                
                results = search_engine.search(demo['query'], top_k=3)
                
                if results:
                    for j, result in enumerate(results, 1):
                        print(f"   ✅ RESULT {j}:")
                        print(f"      Meeting: {result['meeting_title']}")
                        print(f"      Content Type: {result['content_type']}")
                        print(f"      Relevance Score: {result['relevance_score']:.3f}")
                        print(f"      Found Text: {result['snippet'][:100]}...")
                        print()
                else:
                    print("   ❌ No results found")
            
            print("\n🎯 KEY FEATURES DEMONSTRATED:")
            print("=" * 40)
            print("✅ SEMANTIC UNDERSTANDING: Finds 'server scaling' when you search 'infrastructure'")
            print("✅ CONTENT TYPE FILTERING: Can search only summaries, action items, etc.")
            print("✅ RELEVANCE SCORING: Shows how well each result matches your query")
            print("✅ CONTEXT SNIPPETS: Shows relevant text around your search terms")
            print("✅ METADATA INCLUDED: Meeting titles, dates, participants, etc.")
            
            print("\n🚀 WHAT MAKES THIS SPECIAL:")
            print("=" * 40)
            print("• UNDERSTANDS MEANING: Not just keyword matching")
            print("• FAST SEARCH: Vector database for quick results")
            print("• COMPREHENSIVE: Searches all meeting content types")
            print("• PERSISTENT: Saves search index to disk")
            print("• SCALABLE: Can handle thousands of meetings")
            print("• MULTILINGUAL: Works with different languages")
            
            # Show statistics
            stats = search_engine.get_search_statistics()
            print(f"\n📊 CURRENT INDEX STATS:")
            print(f"   Total documents indexed: {stats.get('total_documents', 0)}")
            print(f"   Total meetings: {stats.get('total_meetings', 0)}")
            print(f"   Index size: {stats.get('index_size_mb', 0):.2f} MB")
            print(f"   Embedding model: {stats.get('model_name', 'N/A')}")
            
        else:
            print("❌ Failed to add sample meeting")
            
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    explain_search_engine()
