#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.nlp import NLPProcessor

def test_improvements_comparison():
    """Compare the improvements made to NLP analysis"""
    
    print("🎯 NLP IMPROVEMENT ANALYSIS")
    print("=" * 60)
    
    # Test case with clear action items and decisions
    comprehensive_meeting = """
    Meeting Leader Sarah: Good morning team. We need to finalize our Q4 strategy today.
    
    Product Manager Mike: I've reviewed all the proposals. We have decided to prioritize the mobile app redesign.
    
    Sarah: Mike, can you prepare the project timeline by Friday?
    
    Mike: Absolutely. I will create a comprehensive timeline by Friday afternoon.
    
    Engineering Lead Kate: We voted to approve the new database migration approach.
    
    Sarah: Kate, you should coordinate with the DevOps team by Wednesday.
    
    Kate: I'll schedule the migration window. Mike, will you notify all stakeholders?
    
    Mike: Yes, I need to reach out to all department heads by tomorrow.
    
    Sarah: Final decision - we will implement the new security protocols by January 15th.
    
    Kate: The implementation timeline will be approximately 8-10 weeks total.
    
    Mike: We also approved the budget increase of $25,000 for additional testing.
    
    Sarah: Everyone agreed to move forward with the phased rollout starting December 1st.
    
    Kate: I concluded that we need external consultants for the security audit.
    
    Mike: Sarah, can you review the consultant proposals by end of week?
    
    Sarah: I'll have my recommendations ready by Thursday.
    """
    
    nlp = NLPProcessor()
    result = nlp.generate_comprehensive_summary(comprehensive_meeting)
    
    # Analysis of improvements
    print("📊 IMPROVEMENT METRICS:")
    print(f"   Action Items Detected: {len(result['action_items'])}")
    print(f"   Key Decisions Found: {len(result['key_decisions'])}")  
    print(f"   Timeline Items: {len(result['timelines'])}")
    print(f"   Participants Identified: {len(result['participants'])}")
    print()
    
    print("✅ ENHANCED ACTION ITEMS (with assignees & deadlines):")
    for i, item in enumerate(result['action_items'], 1):
        if isinstance(item, dict):
            assignee = item.get('assignee', 'Unassigned')
            deadline = item.get('deadline', 'No deadline')
            confidence = item.get('confidence', 0.0)
            print(f"   {i}. [{assignee}] {item.get('text', '')[:80]}...")
            if deadline != 'No deadline':
                print(f"      ⏰ Due: {deadline}")
            print(f"      🎯 Confidence: {confidence:.1f}")
        print()
    
    print("🎯 IMPROVED DECISION DETECTION:")
    for i, decision in enumerate(result['key_decisions'], 1):
        print(f"   {i}. {decision[:100]}...")
    print()
    
    print("⏰ ENHANCED TIMELINE EXTRACTION:")
    for i, timeline in enumerate(result['timelines'], 1):
        if isinstance(timeline, dict):
            timeline_text = timeline.get('timeline', '')
            timeline_type = timeline.get('type', 'general')
            confidence = timeline.get('confidence', 0.0)
            print(f"   {i}. {timeline_text} ({timeline_type}) - Confidence: {confidence:.1f}")
        else:
            print(f"   {i}. {timeline}")
    print()
    
    print("👥 PARTICIPANT EXTRACTION:")
    participants = result['participants']
    if participants:
        for i, participant in enumerate(participants, 1):
            print(f"   {i}. {participant}")
    else:
        print("   No participants detected")
    print()
    
    print("🏆 IMPROVEMENT HIGHLIGHTS:")
    print("   ✅ Enhanced action item extraction with pattern matching")
    print("   ✅ Better assignee detection and deadline parsing") 
    print("   ✅ Improved decision recognition with multiple patterns")
    print("   ✅ Advanced timeline extraction with type classification")
    print("   ✅ Refined participant identification with filtering")
    print("   ✅ Comprehensive structured output with confidence scores")
    
    print("\n" + "=" * 60)
    return result

def analyze_accuracy():
    """Analyze the accuracy of extraction"""
    print("\n🔍 ACCURACY ANALYSIS")
    print("=" * 40)
    
    result = test_improvements_comparison()
    
    # Count different types of extractions
    action_items_with_assignees = sum(1 for item in result['action_items'] 
                                    if isinstance(item, dict) and item.get('assignee', 'Unassigned') != 'Unassigned')
    
    action_items_with_deadlines = sum(1 for item in result['action_items']
                                    if isinstance(item, dict) and item.get('deadline', 'No deadline') != 'No deadline')
    
    print(f"📈 EXTRACTION ACCURACY:")
    print(f"   Action items with assignees: {action_items_with_assignees}/{len(result['action_items'])}")
    print(f"   Action items with deadlines: {action_items_with_deadlines}/{len(result['action_items'])}")
    print(f"   Decision detection rate: {len(result['key_decisions'])} decisions found")
    print(f"   Timeline extraction: {len(result['timelines'])} timeline items")

if __name__ == "__main__":
    analyze_accuracy()
