#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.nlp import NLPProcessor

def test_complex_board_meeting():
    """Test with a complex board meeting scenario"""
    
    board_meeting = """
    Chairman Robert: Welcome everyone to our quarterly board meeting. We have several critical decisions to make today regarding our expansion strategy.
    
    CFO Maria: Thank you Robert. I've prepared the financial projections. We need to decide on the proposed $2.5 million investment in our European expansion.
    
    CEO Jennifer: Based on market analysis, I believe we should approve this investment. Maria, can you walk us through the ROI calculations by next Monday?
    
    Maria: Certainly. I will prepare a comprehensive ROI analysis with 3-year projections by Monday morning.
    
    Board Member David: I have concerns about the timeline. The European market entry seems rushed.
    
    Chairman Robert: David raises a valid point. Jennifer, what's your assessment of the timeline?
    
    CEO Jennifer: We concluded that the optimal launch window is Q2 next year. David, could you review the market research with your committee by Friday?
    
    David: I'll coordinate with the strategy committee and have our recommendations ready by Friday afternoon.
    
    CFO Maria: We also need to address the staffing requirements. Jennifer, will you prepare the hiring plan for the European team?
    
    Jennifer: Absolutely. I need to finalize the organizational structure by December 10th.
    
    Board Member Lisa: We voted to approve the technology upgrade budget of $800,000 last month, but implementation has been delayed.
    
    Chairman Robert: Lisa, can you investigate the delays and report back by Wednesday?
    
    Lisa: I'll audit the vendor contracts and identify bottlenecks. Maria, you should coordinate with IT procurement on this.
    
    Maria: Agreed. I'll schedule meetings with all stakeholders by end of this week.
    
    CEO Jennifer: Final decision - we will proceed with the European expansion pending David's committee review.
    
    Chairman Robert: The board unanimously agreed to implement the new governance framework starting January 2026.
    
    David: The implementation timeline will be approximately 6-8 months from board approval.
    
    Lisa: We also approved the acquisition of the German subsidiary for €1.2 million.
    
    Maria: I concluded that we need external legal counsel for the acquisition due diligence.
    
    Jennifer: Maria, can you vet potential law firms by next Thursday?
    
    Maria: I'll have a shortlist of qualified firms ready by Thursday.
    
    Chairman Robert: Thank you all. Our next board meeting is scheduled for November 15th.
    """
    
    print("🏢 TESTING: Complex Board Meeting Analysis")
    print("=" * 60)
    
    nlp = NLPProcessor()
    result = nlp.generate_comprehensive_summary(board_meeting)
    
    print("📊 MEETING METRICS:")
    print(f"   Participants: {len(result['participants'])}")
    print(f"   Action Items: {len(result['action_items'])}")
    print(f"   Decisions: {len(result['key_decisions'])}")
    print(f"   Timelines: {len(result['timelines'])}")
    print()
    
    print("👥 PARTICIPANTS:")
    for participant in result['participants']:
        print(f"   • {participant}")
    print()
    
    print("✅ ACTION ITEMS:")
    for i, item in enumerate(result['action_items'], 1):
        if isinstance(item, dict):
            assignee = item.get('assignee', 'Unassigned')
            deadline = item.get('deadline', 'No deadline')
            text = item.get('text', '')[:100]
            print(f"   {i}. [{assignee}] {text}...")
            if deadline != 'No deadline':
                print(f"      ⏰ {deadline}")
        print()
    
    print("🎯 KEY DECISIONS:")
    for i, decision in enumerate(result['key_decisions'], 1):
        print(f"   {i}. {decision[:120]}...")
    print()
    
    return result

def test_crisis_management_meeting():
    """Test with a crisis management meeting"""
    
    crisis_meeting = """
    Incident Commander Sarah: Emergency response team, we have a critical security breach. All hands on deck.
    
    CISO Michael: The breach was detected at 3:47 AM. We have decided to immediately isolate affected systems.
    
    Sarah: Michael, can you coordinate with the forensics team and have a preliminary assessment by 6 PM today?
    
    Michael: I will lead the investigation and provide an initial damage assessment by 6 PM sharp.
    
    Legal Counsel Amanda: We need to determine notification requirements. Michael, will you document all affected customer data?
    
    Michael: Yes, I'll compile a comprehensive data impact report by tomorrow morning.
    
    PR Director James: We concluded that we need to prepare public statements immediately.
    
    Sarah: James, you should draft the press release and coordinate with Amanda on legal review by 2 PM.
    
    James: I'll have the draft ready by 2 PM. Amanda, can you review it within one hour of receipt?
    
    Amanda: Absolutely. I need to also notify our insurance carrier by end of business today.
    
    CISO Michael: The containment timeline will be approximately 12-16 hours if all goes smoothly.
    
    Sarah: We voted to activate our disaster recovery protocols immediately.
    
    James: I also approved emergency budget allocation of $150,000 for additional security resources.
    
    Amanda: Final decision - we will notify affected customers within 72 hours as required by GDPR.
    
    Michael: We agreed to bring in external cybersecurity consultants. Sarah, can you approve the emergency procurement?
    
    Sarah: Approved. James, you should contact our preferred vendor list by noon.
    
    James: I'll reach out to top three firms and have quotes by 3 PM today.
    
    Amanda: The legal timeline for regulatory notifications will be 24-48 hours depending on jurisdiction.
    
    Sarah: Everyone agreed that all communication must go through James to ensure consistency.
    
    Michael: I concluded that we need 24/7 monitoring until the threat is completely eliminated.
    """
    
    print("\n🚨 TESTING: Crisis Management Meeting Analysis")
    print("=" * 60)
    
    nlp = NLPProcessor()
    result = nlp.generate_comprehensive_summary(crisis_meeting)
    
    print("📈 CRISIS RESPONSE METRICS:")
    print(f"   Urgent Actions: {len(result['action_items'])}")
    print(f"   Critical Decisions: {len(result['key_decisions'])}")
    print(f"   Response Timelines: {len(result['timelines'])}")
    print()
    
    print("⚡ URGENT ACTION ITEMS:")
    urgent_count = 0
    for i, item in enumerate(result['action_items'], 1):
        if isinstance(item, dict):
            deadline = item.get('deadline', 'No deadline')
            if deadline != 'No deadline':
                urgent_count += 1
                assignee = item.get('assignee', 'Unassigned')
                text = item.get('text', '')[:80]
                print(f"   {i}. 🔥 [{assignee}] {text}...")
                print(f"      ⏰ DEADLINE: {deadline}")
            print()
    
    print(f"📊 URGENCY ANALYSIS: {urgent_count}/{len(result['action_items'])} items have specific deadlines")
    print()
    
    return result

def test_technical_architecture_meeting():
    """Test with a technical architecture discussion"""
    
    tech_meeting = """
    Lead Architect Alex: Today we need to finalize our microservices migration strategy.
    
    Senior Engineer Maya: I've analyzed the current monolith. We have decided to start with the user authentication service.
    
    Alex: Maya, can you create the service decomposition plan by next Friday?
    
    Maya: I will design the service boundaries and API contracts by Friday end of day.
    
    DevOps Engineer Carlos: We need to decide on the container orchestration platform. I recommend Kubernetes.
    
    Alex: We voted to proceed with Kubernetes after evaluating Docker Swarm and ECS.
    
    Maya: Carlos, will you set up the development cluster for initial testing?
    
    Carlos: I'll provision the dev environment and have it ready by Wednesday.
    
    Database Architect Nina: We concluded that we need to address data consistency across services.
    
    Alex: Nina, you should evaluate distributed transaction patterns by Monday.
    
    Nina: I need to research saga patterns and event sourcing approaches by Monday afternoon.
    
    Carlos: The migration timeline will be approximately 4-6 months for the complete transition.
    
    Maya: We also approved the adoption of gRPC for inter-service communication.
    
    Alex: Final decision - we will implement circuit breaker patterns for resilience.
    
    Nina: I also agreed to establish monitoring and observability standards. Carlos, can you research APM tools?
    
    Carlos: I'll evaluate Prometheus, Jaeger, and commercial options by Thursday.
    
    Maya: We decided to use infrastructure as code with Terraform for environment management.
    
    Alex: The phased rollout will start with 10% traffic in Q1, then 50% in Q2, and full migration by Q3.
    
    Nina: I concluded that we need database read replicas to handle the increased load during migration.
    
    Carlos: Everyone agreed on implementing blue-green deployment for zero-downtime releases.
    """
    
    print("\n💻 TESTING: Technical Architecture Meeting Analysis")
    print("=" * 60)
    
    nlp = NLPProcessor()
    result = nlp.generate_comprehensive_summary(tech_meeting)
    
    print("🔧 TECHNICAL DECISIONS:")
    tech_decisions = 0
    for decision in result['key_decisions']:
        if any(tech_word in decision.lower() for tech_word in 
               ['kubernetes', 'microservices', 'grpc', 'terraform', 'database', 'api', 'service']):
            tech_decisions += 1
            print(f"   • {decision[:100]}...")
    
    print(f"\n📊 Technical Focus: {tech_decisions}/{len(result['key_decisions'])} decisions are technical")
    print()
    
    print("⚙️ IMPLEMENTATION ACTIONS:")
    for i, item in enumerate(result['action_items'], 1):
        if isinstance(item, dict):
            assignee = item.get('assignee', 'Unassigned')
            text = item.get('text', '')
            if any(tech_word in text.lower() for tech_word in 
                   ['implement', 'develop', 'create', 'setup', 'design', 'evaluate']):
                deadline = item.get('deadline', 'No deadline')
                print(f"   {i}. [{assignee}] {text[:90]}...")
                if deadline != 'No deadline':
                    print(f"      ⏰ {deadline}")
                print()
    
    return result

def test_sales_pipeline_meeting():
    """Test with a sales pipeline review meeting"""
    
    sales_meeting = """
    VP Sales Rachel: Let's review our Q4 pipeline and close out the quarter strong.
    
    Account Manager Tom: We have three major deals in final stages. Enterprise Corp is ready to sign for $280,000.
    
    Rachel: Excellent! Tom, can you finalize the Enterprise Corp contract by Friday?
    
    Tom: I will coordinate with legal and have the signed contract by Friday afternoon.
    
    Sales Rep Jessica: TechStart Inc is requesting a 15% discount on their $150,000 proposal.
    
    Rachel: We decided to approve a 10% discount maximum to maintain our margins.
    
    Jessica: Understood. I'll present the revised proposal and close by Monday.
    
    Account Manager Kevin: Global Solutions wants to expand their contract by $200,000 but needs 60-day payment terms.
    
    Rachel: Kevin, you should check with finance on extended payment terms and report back by Wednesday.
    
    Kevin: I need to also prepare the contract amendment by Thursday.
    
    Sales Rep Melissa: We concluded that we need better lead qualification to improve our conversion rates.
    
    Rachel: Melissa, will you work with marketing to refine our qualification criteria?
    
    Melissa: I'll collaborate with the marketing team and have new criteria by next week.
    
    Tom: The Q4 timeline is tight - we have approximately 6 weeks to close pending deals.
    
    Jessica: We also approved additional sales training focused on enterprise objection handling.
    
    Rachel: Final decision - we will implement weekly pipeline reviews starting December.
    
    Kevin: I agreed to increase our outreach efforts by 30% to build Q1 pipeline.
    
    Melissa: Rachel, can you approve the additional lead generation budget of $25,000?
    
    Rachel: Approved. Tom, you should coordinate with the BDR team on lead distribution.
    
    Tom: I'll set up the new lead routing process by end of week.
    
    Jessica: We decided to extend our sales cycle reporting to include lost deal analysis.
    
    Kevin: Everyone agreed that we need better CRM data hygiene for accurate forecasting.
    """
    
    print("\n💰 TESTING: Sales Pipeline Meeting Analysis")
    print("=" * 60)
    
    nlp = NLPProcessor()
    result = nlp.generate_comprehensive_summary(sales_meeting)
    
    print("💼 SALES METRICS:")
    print(f"   Team Actions: {len(result['action_items'])}")
    print(f"   Strategic Decisions: {len(result['key_decisions'])}")
    print(f"   Sales Timelines: {len(result['timelines'])}")
    print()
    
    # Analyze sales-specific content
    revenue_mentions = 0
    for decision in result['key_decisions']:
        if any(money_word in decision.lower() for money_word in ['$', 'budget', 'discount', 'revenue', 'cost']):
            revenue_mentions += 1
    
    print(f"💵 Financial Focus: {revenue_mentions}/{len(result['key_decisions'])} decisions involve money/budget")
    print()
    
    print("🎯 SALES ACTION ITEMS:")
    for i, item in enumerate(result['action_items'][:5], 1):  # Show top 5
        if isinstance(item, dict):
            assignee = item.get('assignee', 'Unassigned')
            text = item.get('text', '')[:100]
            deadline = item.get('deadline', 'No deadline')
            print(f"   {i}. [{assignee}] {text}...")
            if deadline != 'No deadline':
                print(f"      ⏰ {deadline}")
            print()
    
    return result

def comprehensive_real_world_test():
    """Run all real-world scenario tests and analyze performance"""
    
    print("🌍 COMPREHENSIVE REAL-WORLD NLP TESTING")
    print("=" * 80)
    
    # Run all tests
    board_result = test_complex_board_meeting()
    crisis_result = test_crisis_management_meeting()
    tech_result = test_technical_architecture_meeting()
    sales_result = test_sales_pipeline_meeting()
    
    # Aggregate analysis
    print("\n📊 OVERALL PERFORMANCE ANALYSIS")
    print("=" * 50)
    
    total_actions = len(board_result['action_items']) + len(crisis_result['action_items']) + \
                   len(tech_result['action_items']) + len(sales_result['action_items'])
    
    total_decisions = len(board_result['key_decisions']) + len(crisis_result['key_decisions']) + \
                     len(tech_result['key_decisions']) + len(sales_result['key_decisions'])
    
    total_timelines = len(board_result['timelines']) + len(crisis_result['timelines']) + \
                     len(tech_result['timelines']) + len(sales_result['timelines'])
    
    # Count items with assignments and deadlines
    total_assigned = 0
    total_with_deadlines = 0
    
    for result in [board_result, crisis_result, tech_result, sales_result]:
        for item in result['action_items']:
            if isinstance(item, dict):
                if item.get('assignee', 'Unassigned') != 'Unassigned':
                    total_assigned += 1
                if item.get('deadline', 'No deadline') != 'No deadline':
                    total_with_deadlines += 1
    
    print(f"📈 EXTRACTION TOTALS:")
    print(f"   Total Action Items: {total_actions}")
    print(f"   Total Decisions: {total_decisions}")
    print(f"   Total Timelines: {total_timelines}")
    print()
    
    print(f"🎯 QUALITY METRICS:")
    print(f"   Actions with Assignees: {total_assigned}/{total_actions} ({total_assigned/total_actions*100:.1f}%)")
    print(f"   Actions with Deadlines: {total_with_deadlines}/{total_actions} ({total_with_deadlines/total_actions*100:.1f}%)")
    print()
    
    print("✅ REAL-WORLD TESTING COMPLETE!")
    print("   The NLP system successfully analyzed 4 different meeting types:")
    print("   • Board Meeting (Strategic)")
    print("   • Crisis Management (Urgent)")  
    print("   • Technical Architecture (Complex)")
    print("   • Sales Pipeline (Revenue-focused)")

if __name__ == "__main__":
    comprehensive_real_world_test()
