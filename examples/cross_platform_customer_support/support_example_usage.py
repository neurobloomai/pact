#!/usr/bin/env python3
"""
PACT Cross-Platform Customer Support - Example Usage

This script demonstrates how to use the PACT support system for various
customer support scenarios across multiple channels.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any

from support_orchestrator import PACTSupportOrchestrator, SupportChannel
from support_agents import (
    ChannelAgent, TriageAgent, KnowledgeAgent, 
    CustomerAgent, EscalationAgent, AnalyticsAgent, NotificationAgent
)


async def setup_support_system() -> PACTSupportOrchestrator:
    """Initialize and configure the support system"""
    
    print("🔧 Setting up PACT Cross-Platform Support System...")
    
    # Initialize orchestrator
    orchestrator = PACTSupportOrchestrator()
    await orchestrator.initialize()
    
    # Register all support agents
    agents = [
        ChannelAgent(),
        TriageAgent(),
        KnowledgeAgent(),
        CustomerAgent(),
        EscalationAgent(),
        AnalyticsAgent(),
        NotificationAgent()
    ]
    
    for agent in agents:
        orchestrator.register_agent(agent)
        print(f"   ✅ Registered agent: {agent.name}")
    
    print("✅ Support system setup complete!\n")
    return orchestrator


async def example_email_support(orchestrator: PACTSupportOrchestrator):
    """Example: Customer contacts via email"""
    
    print("📧 Example 1: Email Support Request")
    print("=" * 50)
    
    contact_data = {
        "customer_id": "cust_12345",
        "customer_name": "John Smith",
        "customer_email": "john.smith@example.com",
        "channel": "email",
        "subject": "Can't login to my account",
        "message": "Hi, I've been trying to log into my account for the past hour but keep getting an error message saying 'invalid credentials'. I'm sure I'm using the right password. Can you help?",
        "metadata": {
            "from_email": "john.smith@example.com",
            "reply_to": "john.smith@example.com",
            "received_at": datetime.now().isoformat()
        }
    }
    
    print(f"📨 Email received from: {contact_data['customer_email']}")
    print(f"   Subject: {contact_data['subject']}")
    print(f"   Channel: {contact_data['channel']}")
    
    try:
        ticket_id = await orchestrator.handle_customer_contact(contact_data)
        print(f"✅ Ticket created successfully: {ticket_id}")
        
        # Simulate some processing time
        await asyncio.sleep(2)
        
        print(f"📊 Email support workflow completed for ticket {ticket_id}")
        
    except Exception as e:
        print(f"❌ Email support failed: {str(e)}")
    
    print()


async def example_slack_support(orchestrator: PACTSupportOrchestrator):
    """Example: Customer contacts via Slack"""
    
    print("💬 Example 2: Slack Support Request")
    print("=" * 50)
    
    contact_data = {
        "customer_id": "cust_67890",
        "customer_name": "Sarah Johnson",
        "channel": "slack",
        "subject": "API Integration Help",
        "message": "Hey team! 👋 I'm having trouble integrating with your API. Getting a 429 error every time I make more than 10 requests. Is there a rate limit I'm hitting? Our app needs to make about 100 requests per minute.",
        "metadata": {
            "slack_user_id": "U1234567890",
            "slack_channel": "C9876543210",
            "thread_ts": "1640995200.001400",
            "team_id": "T1234567890"
        }
    }
    
    print(f"💬 Slack message from: {contact_data['customer_name']}")
    print(f"   Message: {contact_data['message'][:100]}...")
    print(f"   Channel: {contact_data['channel']}")
    
    try:
        ticket_id = await orchestrator.handle_customer_contact(contact_data)
        print(f"✅ Ticket created successfully: {ticket_id}")
        
        await asyncio.sleep(1.5)
        
        print(f"📊 Slack support workflow completed for ticket {ticket_id}")
        
    except Exception as e:
        print(f"❌ Slack support failed: {str(e)}")
    
    print()


async def example_whatsapp_support(orchestrator: PACTSupportOrchestrator):
    """Example: Customer contacts via WhatsApp"""
    
    print("📱 Example 3: WhatsApp Support Request")
    print("=" * 50)
    
    contact_data = {
        "customer_id": "cust_11111",
        "customer_name": "Maria Garcia",
        "channel": "whatsapp",
        "subject": "Billing Question",
        "message": "Hola! I received a charge of $50 on my card today but I can't see what it's for in my account. Can you help me understand what this charge is for? 😊",
        "metadata": {
            "phone_number": "+1234567890",
            "message_type": "text",
            "whatsapp_id": "1234567890123456789"
        }
    }
    
    print(f"📱 WhatsApp message from: {contact_data['customer_name']}")
    print(f"   Phone: {contact_data['metadata']['phone_number']}")
    print(f"   Message: {contact_data['message']}")
    
    try:
        ticket_id = await orchestrator.handle_customer_contact(contact_data)
        print(f"✅ Ticket created successfully: {ticket_id}")
        
        await asyncio.sleep(1)
        
        print(f"📊 WhatsApp support workflow completed for ticket {ticket_id}")
        
    except Exception as e:
        print(f"❌ WhatsApp support failed: {str(e)}")
    
    print()


async def example_vip_customer_support(orchestrator: PACTSupportOrchestrator):
    """Example: VIP customer with urgent issue"""
    
    print("⭐ Example 4: VIP Customer Urgent Issue")
    print("=" * 50)
    
    contact_data = {
        "customer_id": "vip_99999",
        "customer_name": "Robert CEO",
        "customer_email": "robert@bigcorp.com",
        "channel": "email",
        "subject": "URGENT: Complete system outage affecting our business",
        "message": "This is extremely urgent! Our entire team of 500+ employees cannot access your platform. We're losing thousands of dollars every minute this is down. We need immediate assistance and escalation to your highest level of support. This is a critical business emergency!",
        "metadata": {
            "customer_tier": "enterprise",
            "account_value": 150000,
            "urgency": "critical",
            "business_impact": "high"
        }
    }
    
    print(f"⭐ VIP customer contact: {contact_data['customer_name']}")
    print(f"   Company: BigCorp (Enterprise)")
    print(f"   Issue: {contact_data['subject']}")
    print(f"   Impact: Critical business emergency")
    
    try:
        ticket_id = await orchestrator.handle_customer_contact(contact_data)
        print(f"🚨 URGENT ticket created: {ticket_id}")
        print(f"📞 Automatic escalation triggered")
        print(f"👨‍💼 Account manager notified")
        
        await asyncio.sleep(3)
        
        print(f"✅ VIP escalation workflow completed for ticket {ticket_id}")
        
    except Exception as e:
        print(f"❌ VIP support failed: {str(e)}")
    
    print()


async def example_multi_channel_conversation(orchestrator: PACTSupportOrchestrator):
    """Example: Customer switches between channels"""
    
    print("🔄 Example 5: Multi-Channel Conversation")
    print("=" * 50)
    
    customer_id = "cust_multichannel"
    
    # First contact via chat widget
    print("💻 Step 1: Customer starts conversation via chat widget")
    chat_contact = {
        "customer_id": customer_id,
        "customer_name": "Alex Chen",
        "channel": "chat_widget",
        "subject": "Payment failed",
        "message": "Hi, I tried to update my payment method but the transaction keeps failing. Can you help?",
        "metadata": {
            "page_url": "https://app.company.com/billing",
            "user_agent": "Mozilla/5.0...",
            "session_id": "sess_123456"
        }
    }
    
    ticket_id_1 = await orchestrator.handle_customer_contact(chat_contact)
    print(f"   💬 Chat ticket created: {ticket_id_1}")
    
    await asyncio.sleep(1)
    
    # Customer switches to email with more details
    print("📧 Step 2: Customer follows up via email with more details")
    email_followup = {
        "customer_id": customer_id,
        "customer_name": "Alex Chen",
        "customer_email": "alex.chen@email.com",
        "channel": "email",
        "subject": "Re: Payment failed - Additional details",
        "message": "Following up on my chat earlier. I'm getting error code 4001 when trying to update my credit card. I've tried three different cards and none work. Is there a known issue?",
        "metadata": {
            "reference_ticket": ticket_id_1,
            "error_code": "4001"
        }
    }
    
    ticket_id_2 = await orchestrator.handle_customer_contact(email_followup)
    print(f"   📨 Email ticket created: {ticket_id_2}")
    
    await asyncio.sleep(1)
    
    # Customer calls for immediate help
    print("📞 Step 3: Customer calls for immediate assistance")
    phone_contact = {
        "customer_id": customer_id,
        "customer_name": "Alex Chen",
        "channel": "phone",
        "subject": "Urgent payment issue - phone call",
        "message": "Customer called regarding ongoing payment issues. Has been unable to update payment method for 2 days. Needs immediate resolution as subscription is about to expire.",
        "metadata": {
            "phone_number": "+1987654321",
            "call_duration": "5 minutes",
            "agent_id": "agent_007",
            "call_priority": "high"
        }
    }
    
    ticket_id_3 = await orchestrator.handle_customer_contact(phone_contact)
    print(f"   📞 Phone ticket created: {ticket_id_3}")
    
    print(f"🔗 Customer context preserved across all channels")
    print(f"📊 Multi-channel workflow demonstrates unified experience")
    
    print()


async def example_analytics_and_insights(orchestrator: PACTSupportOrchestrator):
    """Example: Generate support analytics and insights"""
    
    print("📊 Example 6: Support Analytics & Insights")
    print("=" * 50)
    
    if "analytics" not in orchestrator.agents:
        print("❌ Analytics agent not available")
        return
    
    analytics_agent = orchestrator.agents["analytics"]
    
    # Generate mock interaction data
    print("📈 Generating support analytics...")
    
    # Simulate tracking several interactions
    sample_interactions = [
        {
            "ticket_id": "TICK_001",
            "channel": "email",
            "priority": "medium",
            "category": "billing_inquiry",
            "resolution_time": 45,
            "customer_satisfaction": 4.2,
            "escalated": False,
            "first_contact_resolution": True
        },
        {
            "ticket_id": "TICK_002", 
            "channel": "slack",
            "priority": "high",
            "category": "technical_support",
            "resolution_time": 120,
            "customer_satisfaction": 3.8,
            "escalated": True,
            "first_contact_resolution": False
        },
        {
            "ticket_id": "TICK_003",
            "channel": "whatsapp",
            "priority": "low",
            "category": "general_inquiry",
            "resolution_time": 15,
            "customer_satisfaction": 4.8,
            "escalated": False,
            "first_contact_resolution": True
        }
    ]
    
    # Track interactions
    for interaction in sample_interactions:
        await analytics_agent.execute_pact_action("analytics.track_interaction", interaction)
    
    # Generate insights
    insights_result = await analytics_agent.execute_pact_action("analytics.generate_insights", {
        "insight_type": "comprehensive",
        "time_period": "7_days"
    })
    
    if insights_result.get("success"):
        insights = insights_result["insights"]
        print(f"   ✅ Generated {insights['total_insights']} insights")
        print(f"   📊 Analysis period: {insights['analysis_period']}")
        print(f"   🎯 Data quality score: {insights['data_quality_score']:.2f}")
        
        if insights["insights"]:
            print(f"   💡 Sample insight: {insights['insights'][0]['title']}")
    
    # Generate resolution time analysis
    resolution_analysis = await analytics_agent.execute_pact_action("analytics.measure_resolution_time", {
        "time_period": "7_days"
    })
    
    if resolution_analysis.get("success"):
        analysis = resolution_analysis["resolution_time_analysis"]
        print(f"   ⏱️ Average resolution time: {analysis['avg_resolution_time_minutes']} minutes")
        print(f"   📈 Tickets analyzed: {analysis['total_tickets']}")
    
    print()


async def example_knowledge_base_search(orchestrator: PACTSupportOrchestrator):
    """Example: Knowledge base search and solution suggestions"""
    
    print("🧠 Example 7: Knowledge Base Search")
    print("=" * 50)
    
    if "knowledge" not in orchestrator.agents:
        print("❌ Knowledge agent not available")
        return
    
    knowledge_agent = orchestrator.agents["knowledge"]
    
    # Search for solutions
    search_queries = [
        "password reset",
        "API rate limits",
        "billing invoice",
        "account security"
    ]
    
    for query in search_queries:
        print(f"🔍 Searching for: '{query}'")
        
        search_result = await knowledge_agent.execute_pact_action("knowledge.search_solutions", {
            "query": query,
            "category": "general",
            "customer_context": {"technical_level": "medium"}
        })
        
        if search_result.get("success"):
            solutions = search_result["solutions"]
            print(f"   📚 Found {len(solutions)} relevant solutions")
            
            if solutions:
                best_solution = solutions[0]
                print(f"   🎯 Best match: {best_solution['title']} (confidence: {best_solution['confidence']:.2f})")
        
        await asyncio.sleep(0.5)
    
    print()


async def example_customer_profile_management(orchestrator: PACTSupportOrchestrator):
    """Example: Customer profile and history management"""
    
    print("👤 Example 8: Customer Profile Management")
    print("=" * 50)
    
    if "customer" not in orchestrator.agents:
        print("❌ Customer agent not available")
        return
    
    customer_agent = orchestrator.agents["customer"]
    
    # Get customer profile
    customer_id = "cust_profile_demo"
    
    print(f"👤 Managing profile for customer: {customer_id}")
    
    # Get profile
    profile_result = await customer_agent.execute_pact_action("customer.get_profile", {
        "customer_id": customer_id,
        "customer_name": "Demo Customer",
        "customer_email": "demo@example.com"
    })
    
    if profile_result.get("success"):
        profile = profile_result["customer_profile"]
        print(f"   📋 Profile loaded: {profile['name']}")
        print(f"   💎 VIP Status: {profile['vip_status']}")
        print(f"   💰 Lifetime Value: ${profile['lifetime_value']}")
        print(f"   📊 Satisfaction: {profile['satisfaction_score']}/5")
    
    # Update interaction history
    interaction_data = {
        "ticket_id": "TICK_DEMO_001",
        "channel": "email",
        "type": "support_request",
        "resolution_time": 30,
        "satisfaction_score": 4.5,
        "escalated": False,
        "resolved": True,
        "category": "billing_inquiry"
    }
    
    await customer_agent.execute_pact_action("customer.update_interaction_history", {
        "customer_id": customer_id,
        "interaction_data": interaction_data
    })
    
    print(f"   ✅ Interaction history updated")
    
    # Check VIP status
    vip_result = await customer_agent.execute_pact_action("customer.identify_vip_status", {
        "customer_id": customer_id
    })
    
    if vip_result.get("success"):
        vip_analysis = vip_result["vip_analysis"]
        print(f"   ⭐ VIP Analysis: {vip_analysis['vip_status']}")
        print(f"   🎯 VIP Score: {vip_analysis['vip_score']}")
    
    print()


async def demonstrate_support_scenarios():
    """Run all support scenario demonstrations"""
    
    print("🚀 PACT Cross-Platform Customer Support - Demo Scenarios")
    print("=" * 65)
    print()
    
    try:
        # Setup
        orchestrator = await setup_support_system()
        
        # Run examples
        await example_email_support(orchestrator)
        await example_slack_support(orchestrator)
        await example_whatsapp_support(orchestrator)
        await example_vip_customer_support(orchestrator)
        await example_multi_channel_conversation(orchestrator)
        await example_analytics_and_insights(orchestrator)
        await example_knowledge_base_search(orchestrator)
        await example_customer_profile_management(orchestrator)
        
        print("🎉 All support scenarios completed successfully!")
        print("=" * 65)
        print()
        print("💡 Key Benefits Demonstrated:")
        print("   • Unified experience across all communication channels")
        print("   • Intelligent triage and routing based on content analysis")
        print("   • Context preservation across channel switches")
        print("   • Automatic escalation for VIP customers and urgent issues")
        print("   • Real-time analytics and insights generation")
        print("   • Knowledge base integration for faster resolution")
        print("   • Complete customer interaction history tracking")
        print()
        print("🔧 Next Steps:")
        print("   • Integrate with your actual communication platforms")
        print("   • Configure escalation rules for your organization")
        print("   • Train the knowledge base with your support content")
        print("   • Set up monitoring and alerting")
        print("   • Customize notification templates")
        
        # Cleanup
        await orchestrator.shutdown()
        
    except Exception as e:
        print(f"❌ Demo execution failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the support system demo
    asyncio.run(demonstrate_support_scenarios())
