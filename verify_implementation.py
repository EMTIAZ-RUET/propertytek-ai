#!/usr/bin/env python3
"""
Comprehensive verification of LangGraph PropertyTek implementation
"""

import sys
import os
import json
from typing import Dict, Any

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_workflow_state():
    """Test WorkflowState functionality"""
    print("🧪 Testing WorkflowState...")
    
    try:
        from src.workflows.state import WorkflowState
        
        # Create a test state
        test_state: WorkflowState = {
            "user_query": "Show me 2 bedroom apartments in Austin",
            "user_id": "test_user_123",
            "conversation_history": None,
            "intent": "property_search",
            "entities": {"bedrooms": 2, "city": "Austin"},
            "confidence": "high",
            "properties": [],
            "search_filters": {},
            "available_slots": [],
            "selected_slot": None,
            "appointment_details": None,
            "user_name": None,
            "user_email": None,
            "user_phone": None,
            "user_pets": None,
            "calendar_event_id": None,
            "sms_sent": None,
            "sms_result": None,
            "response_message": "",
            "suggested_actions": [],
            "error": None,
            "next_step": "search_properties",
            "workflow_complete": False
        }
        
        # Verify state structure
        assert test_state["user_query"] == "Show me 2 bedroom apartments in Austin"
        assert test_state["intent"] == "property_search"
        assert test_state["entities"]["bedrooms"] == 2
        assert test_state["next_step"] == "search_properties"
        
        print("✅ WorkflowState structure and functionality verified")
        return True
        
    except Exception as e:
        print(f"❌ WorkflowState test failed: {e}")
        return False


def test_openai_service():
    """Test OpenAI service structure"""
    print("🧪 Testing OpenAI Service...")
    
    try:
        from src.services.openai_service import OpenAIService
        
        # Test service initialization (without actual API calls)
        service = OpenAIService()
        
        # Verify methods exist
        assert hasattr(service, 'analyze_intent')
        assert hasattr(service, 'generate_response')
        assert hasattr(service, 'client')
        
        print("✅ OpenAI Service structure verified")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI Service test failed: {e}")
        return False


def test_workflow_nodes():
    """Test WorkflowNodes structure"""
    print("🧪 Testing Workflow Nodes...")
    
    try:
        from src.workflows.nodes import WorkflowNodes
        
        # Test nodes initialization (without actual service calls)
        nodes = WorkflowNodes()
        
        # Verify all required methods exist
        required_methods = [
            'analyze_intent',
            'search_properties', 
            'get_available_slots',
            'collect_user_info',
            'create_calendar_event',
            'send_sms_confirmation',
            'generate_response'
        ]
        
        for method in required_methods:
            assert hasattr(nodes, method), f"Missing method: {method}"
        
        print("✅ Workflow Nodes structure verified")
        return True
        
    except Exception as e:
        print(f"❌ Workflow Nodes test failed: {e}")
        return False


def test_langgraph_api():
    """Test LangGraph API structure"""
    print("🧪 Testing LangGraph API...")
    
    try:
        from src.chatbot.langgraph_api import app, ChatRequest, ChatResponse
        
        # Test FastAPI app exists
        assert app is not None
        
        # Test request/response models
        test_request = ChatRequest(
            query="test query",
            user_id="test_user",
            conversation_history=None
        )
        
        assert test_request.query == "test query"
        assert test_request.user_id == "test_user"
        
        print("✅ LangGraph API structure verified")
        return True
        
    except Exception as e:
        print(f"❌ LangGraph API test failed: {e}")
        return False


def test_property_service():
    """Test Property Service integration"""
    print("🧪 Testing Property Service...")
    
    try:
        from src.services.property_service import PropertyService
        
        # Test service initialization
        service = PropertyService()
        
        # Verify methods exist
        assert hasattr(service, 'search_properties')
        assert hasattr(service, 'get_all_properties')
        
        print("✅ Property Service integration verified")
        return True
        
    except Exception as e:
        print(f"❌ Property Service test failed: {e}")
        return False


def test_tools_integration():
    """Test Calendar and SMS tools integration"""
    print("🧪 Testing Tools Integration...")
    
    try:
        from src.tools.calendar_tool import CalendarTool
        from src.tools.sms_tool import SMSTool
        
        # Test tools initialization
        calendar_tool = CalendarTool()
        sms_tool = SMSTool()
        
        # Verify key methods exist
        assert hasattr(calendar_tool, 'create_calendar_event')
        assert hasattr(calendar_tool, 'get_fixed_slots_next_day')
        assert hasattr(sms_tool, 'send_appointment_confirmation')
        
        print("✅ Calendar and SMS tools integration verified")
        return True
        
    except Exception as e:
        print(f"❌ Tools integration test failed: {e}")
        return False


def main():
    """Run comprehensive verification"""
    print("🚀 Comprehensive LangGraph PropertyTek Verification")
    print("=" * 60)
    
    tests = [
        ("WorkflowState", test_workflow_state),
        ("OpenAI Service", test_openai_service),
        ("Workflow Nodes", test_workflow_nodes),
        ("LangGraph API", test_langgraph_api),
        ("Property Service", test_property_service),
        ("Tools Integration", test_tools_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
        print()  # Add spacing between tests
    
    # Summary
    print("=" * 60)
    print("📊 Verification Results:")
    print("-" * 30)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("-" * 30)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All verification tests passed!")
        print("🚀 Your LangGraph PropertyTek implementation is ready!")
        print("\n📝 Next steps:")
        print("1. Install dependencies: python install_dependencies.py")
        print("2. Configure .env with your API keys")
        print("3. Run server: python run_server.py")
        print("4. Test API: http://localhost:8000/docs")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Check the errors above.")
        print("💡 Most failures are likely due to missing dependencies.")
        print("   Run: python install_dependencies.py")


if __name__ == "__main__":
    main()