#!/usr/bin/env python3

import sys
import os
import uuid
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_search_engine():
    """Simple test of the search engine"""
    print("🧪 Testing Search Engine")
    print("=" * 50)
    
    try:
        # Import the search engine
        from models.search import MeetingSearchEngine
        print("✅ Successfully imported MeetingSearchEngine")
        
        # Initialize search engine
        search_engine = MeetingSearchEngine()
        print("✅ Search engine initialized")
        
        # Get initial statistics
        stats = search_engine.get_search_statistics()
        print(f"📊 Initial stats: {stats}")
        
        # Create a simple test meeting
        test_meeting = {
            'id': str(uuid.uuid4()),
            'title': 'Test Meeting',
            'date': datetime.now().isoformat(),
            'transcript': 'This is a test meeting about artificial intelligence and machine learning.',
            'summary': 'Discussion about AI and ML technologies.',
            'action_items': [
                {'text': 'Research new AI frameworks', 'assignee': 'John'},
                {'text': 'Prepare ML presentation', 'assignee': 'Jane'}
            ],
            'key_decisions': [
                'Adopt TensorFlow for new projects',
                'Start ML training program'
            ],
            'participants': ['John', 'Jane', 'Bob']
        }
        
        # Add meeting to index
        success = search_engine.add_meeting(test_meeting)
        if success:
            print("✅ Successfully added test meeting to index")
            
            # Test search
            results = search_engine.search("artificial intelligence", top_k=3)
            print(f"🔍 Search results for 'artificial intelligence': {len(results)} found")
            
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['meeting_title']} - {result['content_type']}")
                print(f"      Score: {result['relevance_score']:.3f}")
                print(f"      Snippet: {result['snippet'][:100]}...")
            
            # Get updated statistics
            final_stats = search_engine.get_search_statistics()
            print(f"📊 Final stats: {final_stats}")
            
        else:
            print("❌ Failed to add test meeting")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search_engine()
