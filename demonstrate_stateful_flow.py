#!/usr/bin/env python3
"""
Demonstrate LangGraph Stateful Flow
Shows how state evolves through each node
"""

import json
import sys
import os
from typing import Dict, Any

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def simulate_stateful_flow():
    """Simulate how state flows through the workflow"""
    print("🔄 LangGraph Stateful Flow Demonstration")
    print("=" * 60)
    print("Query: 'Show me vacant space in Houston'")
    print("=" * 60)
    
    # Initial state
    print("\n📋 INITIAL STATE (Workflow Start):")
    print("-" * 40)
    initial_state = {
        "user_query": "Show me vacant space in Houston",
        "user_id": "user123",
        "conversation_history": None,
        "intent": None,
        "entities": {},
        "confidence": None,
        "properties": [],
        "search_filters": {},
        "available_slots": [],
        "response_message": "",
        "suggested_actions": [],
        "next_step": None,
        "workflow_complete": False
    }
    print_state_changes(initial_state, highlight_fields=[])
    
    # After analyze_intent
    print("\n🧠 AFTER analyze_intent NODE:")
    print("-" * 40)
    after_intent = initial_state.copy()
    after_intent.update({
        "intent": "property_search",
        "entities": {"city": "Houston", "state": "TX"},
        "confidence": "high",
        "next_step": "search_properties"
    })
    print_state_changes(after_intent, highlight_fields=["intent", "entities", "confidence", "next_step"])
    
    # After search_properties
    print("\n🏠 AFTER search_properties NODE:")
    print("-" * 40)
    after_search = after_intent.copy()
    after_search.update({
        "properties": [
            {
                "id": "prop_123",
                "address": "123 Main St, Houston, TX 77001",
                "bedrooms": 2,
                "rent": 1500.0,
                "available": "Available now",
                "pets": "Dogs allowed"
            },
            {
                "id": "prop_456", 
                "address": "456 Oak Ave, Houston, TX 77002",
                "bedrooms": 1,
                "rent": 1200.0,
                "available": "Sep 2025",
                "pets": "no pets"
            }
        ],
        "search_filters": {"address": "Houston"},
        "next_step": "generate_response"
    })
    print_state_changes(after_search, highlight_fields=["properties", "search_filters", "next_step"])
    
    # After generate_response
    print("\n💬 AFTER generate_response NODE:")
    print("-" * 40)
    final_state = after_search.copy()
    final_state.update({
        "response_message": "I found 2 vacant properties in Houston. Here are your options:\n\n1. A 2-bedroom apartment at 123 Main St for $1500/month\n2. A 1-bedroom condo at 456 Oak Ave for $1200/month",
        "suggested_actions": [
            "Schedule a tour for any property",
            "Get more details about a specific property",
            "Refine your search criteria"
        ],
        "next_step": None,
        "workflow_complete": True
    })
    print_state_changes(final_state, highlight_fields=["response_message", "suggested_actions", "workflow_complete"])
    
    print("\n" + "=" * 60)
    print("🎯 KEY OBSERVATIONS:")
    print("✅ State ACCUMULATES information (never loses previous data)")
    print("✅ Each node READS current state and UPDATES relevant fields")
    print("✅ 'next_step' field CONTROLS workflow routing")
    print("✅ All context AVAILABLE to every node")
    print("✅ Final state contains COMPLETE conversation context")


def print_state_changes(state: Dict[str, Any], highlight_fields: list = []):
    """Print state with highlighted changes"""
    for key, value in state.items():
        if key in highlight_fields:
            if isinstance(value, (dict, list)) and value:
                print(f"🔥 {key}: {json.dumps(value, indent=2)}")
            else:
                print(f"🔥 {key}: {value}")
        else:
            if value is not None and value != "" and value != [] and value != {}:
                if isinstance(value, (dict, list)):
                    print(f"   {key}: {json.dumps(value, indent=2)}")
                else:
                    print(f"   {key}: {value}")


def demonstrate_booking_flow():
    """Demonstrate multi-step booking flow with state accumulation"""
    print("\n\n🎯 MULTI-STEP BOOKING FLOW DEMONSTRATION")
    print("=" * 60)
    print("Scenario: User books a property tour")
    print("=" * 60)
    
    # Step 1: Initial booking request
    print("\n📅 STEP 1: User says 'I want to schedule a tour'")
    print("-" * 50)
    booking_state_1 = {
        "user_query": "I want to schedule a tour",
        "intent": "schedule_tour",
        "entities": {},
        "next_step": "get_available_slots",
        "workflow_complete": False
    }
    print_state_changes(booking_state_1, highlight_fields=["intent", "next_step"])
    
    # Step 2: After getting slots
    print("\n📅 STEP 2: After get_available_slots")
    print("-" * 50)
    booking_state_2 = booking_state_1.copy()
    booking_state_2.update({
        "available_slots": [
            {"formatted_time": "Saturday, August 23 at 11:00 AM"},
            {"formatted_time": "Saturday, August 23 at 12:00 PM"},
            {"formatted_time": "Saturday, August 23 at 01:00 PM"}
        ],
        "next_step": "collect_user_info"
    })
    print_state_changes(booking_state_2, highlight_fields=["available_slots", "next_step"])
    
    # Step 3: After collecting user info
    print("\n👤 STEP 3: After collect_user_info")
    print("-" * 50)
    booking_state_3 = booking_state_2.copy()
    booking_state_3.update({
        "user_name": "John Doe",
        "user_email": "john@example.com",
        "user_phone": "+1234567890",
        "user_pets": "Dogs",
        "next_step": "create_calendar_event"
    })
    print_state_changes(booking_state_3, highlight_fields=["user_name", "user_email", "user_phone", "user_pets", "next_step"])
    
    # Step 4: After creating calendar event
    print("\n📆 STEP 4: After create_calendar_event")
    print("-" * 50)
    booking_state_4 = booking_state_3.copy()
    booking_state_4.update({
        "calendar_event_id": "cal_event_123",
        "appointment_details": {
            "property_address": "123 Main St, Houston, TX",
            "formatted_date": "Saturday, August 23 at 11:00 AM",
            "id": "cal_event_123"
        },
        "next_step": "send_sms_confirmation"
    })
    print_state_changes(booking_state_4, highlight_fields=["calendar_event_id", "appointment_details", "next_step"])
    
    # Step 5: After SMS confirmation
    print("\n📱 STEP 5: After send_sms_confirmation")
    print("-" * 50)
    booking_state_5 = booking_state_4.copy()
    booking_state_5.update({
        "sms_sent": True,
        "sms_result": {"success": True, "message_sid": "SMS123"},
        "next_step": "generate_response"
    })
    print_state_changes(booking_state_5, highlight_fields=["sms_sent", "sms_result", "next_step"])
    
    # Final step: Response generation
    print("\n💬 STEP 6: After generate_response (FINAL)")
    print("-" * 50)
    booking_final = booking_state_5.copy()
    booking_final.update({
        "response_message": "🎉 Booking confirmed! Your appointment for Saturday, August 23 at 11:00 AM has been scheduled. Calendar event created and SMS confirmation sent.",
        "suggested_actions": [
            "Ask about property features",
            "Get directions to the property",
            "Modify appointment time"
        ],
        "next_step": None,
        "workflow_complete": True
    })
    print_state_changes(booking_final, highlight_fields=["response_message", "suggested_actions", "workflow_complete"])
    
    print("\n" + "=" * 60)
    print("🎯 BOOKING FLOW OBSERVATIONS:")
    print("✅ State PRESERVES all information from previous steps")
    print("✅ User info ACCUMULATED across multiple interactions")
    print("✅ Calendar and SMS results STORED in state")
    print("✅ Final response has ACCESS to complete booking context")
    print("✅ Each node BUILDS upon previous node's work")


def show_context_awareness():
    """Show how nodes are context-aware"""
    print("\n\n🧠 CONTEXT AWARENESS DEMONSTRATION")
    print("=" * 60)
    
    print("📋 Example: generate_response node has access to ALL context:")
    print("-" * 60)
    
    full_context_state = {
        "user_query": "Show me vacant space in Houston",
        "intent": "property_search",
        "entities": {"city": "Houston", "state": "TX"},
        "properties": [{"id": "prop_123", "address": "123 Main St, Houston"}],
        "user_name": "John Doe",
        "user_email": "john@example.com",
        "calendar_event_id": "cal_123",
        "sms_sent": True
    }
    
    print("🔍 Available context in generate_response node:")
    for key, value in full_context_state.items():
        print(f"   • {key}: {value}")
    
    print("\n💡 This allows generate_response to create intelligent responses like:")
    print("   'Hi John! I found properties in Houston and scheduled your tour.'")
    print("   'Your calendar event cal_123 is confirmed and SMS sent!'")
    
    print("\n🎯 Without stateful architecture, each node would be isolated!")
    print("❌ No context sharing between nodes")
    print("❌ No progressive information building")
    print("❌ No intelligent, contextual responses")


def main():
    """Main demonstration"""
    simulate_stateful_flow()
    demonstrate_booking_flow()
    show_context_awareness()
    
    print("\n\n🎊 CONCLUSION:")
    print("=" * 60)
    print("LangGraph's STATEFUL architecture enables:")
    print("✅ Progressive information accumulation")
    print("✅ Context-aware decision making")
    print("✅ Intelligent workflow routing")
    print("✅ Rich, contextual responses")
    print("✅ Multi-step conversation flows")
    print("\nThis is what makes your PropertyTek chatbot so powerful! 🚀")


if __name__ == "__main__":
    main()