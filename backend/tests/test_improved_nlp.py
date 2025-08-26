#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.nlp import NLPProcessor

def test_comprehensive_meeting():
    """Test comprehensive meeting analysis with improved extraction"""
    
    # Comprehensive meeting transcript with clear decisions and action items
    test_transcript = """
    Sarah: Good morning everyone. Today we need to make some critical decisions about our Q4 strategy.
    
    Michael: Thanks Sarah. I've reviewed the budget proposals and I think we need to decide on three key areas.
    
    Sarah: Michael, can you walk us through the budget breakdown by Thursday? 
    
    Michael: Absolutely. I will prepare a detailed analysis by Thursday morning.
    
    Lisa: We have decided to approve the new marketing campaign with a budget of $50,000.
    
    Tom: Great! Lisa, will you coordinate with the design team on this?
    
    Lisa: Yes, I'll reach out to them today. Tom, you should contact the vendors by Friday.
    
    Sarah: Everyone agreed that we're moving forward with the hybrid work model starting January 1st.
    
    Michael: The timeline for implementation will be approximately 6 weeks from approval.
    
    Lisa: I need to survey all department heads by next week to get their input.
    
    Tom: We voted to reject the proposal for the new office space downtown.
    
    Sarah: Final decision - we will invest in the employee training program instead.
    
    Michael: The training should be completed within the next 3 months.
    
    Lisa: Tom and I will develop the curriculum by December 15th.
    
    Sarah: Perfect. Michael, can you calculate the total cost impact?
    
    Michael: I'll have those numbers ready by end of week.
    
    Tom: We concluded that the project timeline needs to be 2-3 weeks longer than originally planned.
    
    Lisa: Also, we approved the Q1 hiring plan with 5 new positions.
    
    Sarah: Meeting adjourned. Thanks everyone for your input.
    """
    
    print("🧪 Testing Improved NLP Analysis...")
    print("=" * 60)
    
    nlp = NLPProcessor()
    
    # Test comprehensive analysis
    result = nlp.generate_comprehensive_summary(test_transcript)
    
    print("📝 MEETING SUMMARY:")
    print(f"   {result['summary']}")
    print()
    
    print("✅ ACTION ITEMS:")
    for i, item in enumerate(result['action_items'], 1):
        if isinstance(item, dict):
            print(f"   {i}. [{item.get('assignee', 'Unassigned')}] {item.get('text', item)}")
            print(f"      Deadline: {item.get('deadline', 'No deadline')}")
            print(f"      Category: {item.get('category', 'General')}")
        else:
            print(f"   {i}. {item}")
        print()
    
    print("🎯 KEY DECISIONS:")
    for i, decision in enumerate(result['key_decisions'], 1):
        print(f"   {i}. {decision}")
    print()
    
    print("⏰ TIMELINES:")
    for i, timeline in enumerate(result['timelines'], 1):
        if isinstance(timeline, dict):
            print(f"   {i}. {timeline.get('timeline', timeline)} ({timeline.get('type', 'general')})")
            print(f"      Context: {timeline.get('context', '')} ")
        else:
            print(f"   {i}. {timeline}")
    print()
    
    print("👥 PARTICIPANTS:")
    for i, participant in enumerate(result['participants'], 1):
        print(f"   {i}. {participant}")
    print()
    
    print("🏷️ KEY TOPICS:")
    for i, topic in enumerate(result['topics'], 1):
        print(f"   {i}. {topic}")
    
    print("\n" + "=" * 60)
    print("✅ Improved NLP Analysis Complete!")

def test_complex_engineering_meeting():
    """Test with a complex engineering meeting"""
    
    engineering_meeting = """
    Alex: Let's discuss the critical bugs in our payment system.
    
    Jordan: We have decided to prioritize the database timeout issue first.
    
    Alex: Jordan, can you fix the connection pooling by Wednesday?
    
    Jordan: I will implement the fix and have it deployed by Wednesday evening.
    
    Casey: We approved the migration to the new API version 2.0.
    
    Alex: The migration timeline will be approximately 4-5 weeks.
    
    Jordan: Casey, you need to update all the client libraries by next Friday.
    
    Casey: I'll coordinate with the mobile team and web team on this.
    
    Alex: We voted to reject the proposal for rewriting the entire auth system.
    
    Jordan: Instead, we concluded that we'll refactor it incrementally over Q1.
    
    Casey: I need to audit all existing endpoints by December 20th.
    
    Alex: Final decision - we will implement rate limiting across all APIs.
    
    Jordan: The implementation should take about 2 weeks once we start.
    
    Casey: Alex, can you review the architecture proposal by tomorrow?
    
    Alex: I'll have feedback ready by end of business tomorrow.
    
    Jordan: We also approved the new monitoring dashboard with $15,000 budget.
    """
    
    print("\n🧪 Testing Engineering Meeting Analysis...")
    print("=" * 60)
    
    nlp = NLPProcessor()
    result = nlp.generate_comprehensive_summary(engineering_meeting)
    
    print("📝 SUMMARY:")
    print(f"   {result['summary']}")
    print()
    
    print("✅ ACTION ITEMS:")
    for i, item in enumerate(result['action_items'], 1):
        if isinstance(item, dict):
            print(f"   {i}. [{item.get('assignee', 'Unassigned')}] {item.get('text', item)}")
            if item.get('deadline') != 'No deadline':
                print(f"      ⏰ {item.get('deadline')}")
        else:
            print(f"   {i}. {item}")
    print()
    
    print("🎯 KEY DECISIONS:")
    for i, decision in enumerate(result['key_decisions'], 1):
        print(f"   {i}. {decision}")
    print()
    
    print("⏰ TIMELINES:")
    for i, timeline in enumerate(result['timelines'], 1):
        if isinstance(timeline, dict):
            print(f"   {i}. {timeline.get('timeline')} - {timeline.get('type')}")
        else:
            print(f"   {i}. {timeline}")

if __name__ == "__main__":
    test_comprehensive_meeting()
    test_complex_engineering_meeting()
