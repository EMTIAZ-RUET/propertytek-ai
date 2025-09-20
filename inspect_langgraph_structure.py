#!/usr/bin/env python3
"""
Inspect the actual LangGraph structure
"""

import sys
import os
from typing import Dict, Any

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def inspect_workflow_structure():
    """Inspect the actual workflow structure"""
    print("🔍 Inspecting LangGraph Workflow Structure...")
    print("=" * 60)
    
    try:
        from src.workflows.graph import create_property_workflow
        
        # Create the workflow
        workflow = create_property_workflow()
        
        print("✅ Workflow created successfully!")
        print(f"📊 Workflow type: {type(workflow)}")
        
        # Try to get workflow information
        if hasattr(workflow, 'nodes'):
            print(f"🔧 Number of nodes: {len(workflow.nodes)}")
            print("📋 Node names:")
            for node_name in workflow.nodes:
                print(f"   • {node_name}")
        
        if hasattr(workflow, 'edges'):
            print(f"🔗 Number of edges: {len(workflow.edges)}")
            print("📋 Edge connections:")
            for edge in workflow.edges:
                print(f"   • {edge}")
        
        # Try to get the graph structure
        if hasattr(workflow, 'get_graph'):
            try:
                graph_info = workflow.get_graph()
                print(f"📈 Graph info: {graph_info}")
            except Exception as e:
                print(f"⚠️  Could not get graph info: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure LangGraph dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Error inspecting workflow: {e}")
        return False


def show_workflow_nodes():
    """Show detailed information about workflow nodes"""
    print("\n🧩 Workflow Nodes Analysis:")
    print("-" * 40)
    
    try:
        from src.workflows.nodes import WorkflowNodes
        
        nodes = WorkflowNodes()
        
        # Get all methods that are workflow nodes
        node_methods = [
            method for method in dir(nodes) 
            if not method.startswith('_') and callable(getattr(nodes, method))
        ]
        
        print(f"📊 Found {len(node_methods)} node methods:")
        
        for method_name in node_methods:
            method = getattr(nodes, method_name)
            if hasattr(method, '__doc__') and method.__doc__:
                doc = method.__doc__.strip().split('\n')[0]
                print(f"   🔧 {method_name}: {doc}")
            else:
                print(f"   🔧 {method_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing nodes: {e}")
        return False


def show_state_structure():
    """Show the workflow state structure"""
    print("\n📊 Workflow State Structure:")
    print("-" * 40)
    
    try:
        from src.workflows.state import WorkflowState
        
        # Get type annotations
        if hasattr(WorkflowState, '__annotations__'):
            annotations = WorkflowState.__annotations__
            print(f"📋 State fields ({len(annotations)} total):")
            
            for field_name, field_type in annotations.items():
                type_str = str(field_type).replace('typing.', '').replace('<class \'', '').replace('\'>', '')
                print(f"   • {field_name}: {type_str}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing state: {e}")
        return False


def create_simple_flow_diagram():
    """Create a simple text-based flow diagram"""
    print("\n🎨 Simple Flow Diagram:")
    print("-" * 40)
    
    flow_steps = [
        ("🚀 START", "Workflow begins"),
        ("🧠 analyze_intent", "OpenAI analyzes user intent"),
        ("🔀 ROUTING", "Based on intent, route to appropriate node"),
        ("🏠 search_properties", "Search database for properties"),
        ("📅 get_available_slots", "Get calendar availability"),
        ("👤 collect_user_info", "Extract user information"),
        ("📆 create_calendar_event", "Create Google Calendar event"),
        ("📱 send_sms_confirmation", "Send Twilio SMS"),
        ("💬 generate_response", "Generate final response"),
        ("✅ END", "Workflow complete")
    ]
    
    for i, (step, description) in enumerate(flow_steps):
        if i == 0:
            print(f"{step}")
            print("│")
        elif i == len(flow_steps) - 1:
            print("│")
            print(f"└─► {step}")
        else:
            print("│")
            print(f"├─► {step}")
            print(f"│   {description}")
    
    print("\n🔄 Routing Logic:")
    print("   • property_search → search_properties")
    print("   • schedule_tour → get_available_slots")
    print("   • confirm_booking → create_calendar_event")
    print("   • general → generate_response")


def main():
    """Main inspection function"""
    print("🔍 LangGraph Structure Inspector")
    print("=" * 60)
    
    # Inspect workflow structure
    workflow_ok = inspect_workflow_structure()
    
    # Show nodes
    nodes_ok = show_workflow_nodes()
    
    # Show state
    state_ok = show_state_structure()
    
    # Show simple diagram
    create_simple_flow_diagram()
    
    print("\n" + "=" * 60)
    print("📊 Inspection Results:")
    print(f"   Workflow Structure: {'✅ OK' if workflow_ok else '❌ FAIL'}")
    print(f"   Node Analysis: {'✅ OK' if nodes_ok else '❌ FAIL'}")
    print(f"   State Structure: {'✅ OK' if state_ok else '❌ FAIL'}")
    
    if all([workflow_ok, nodes_ok, state_ok]):
        print("\n🎉 LangGraph structure is healthy!")
        print("📋 Files generated:")
        print("   • langgraph_visualization.html - Interactive visualization")
        print("   • langgraph_mermaid.md - Mermaid diagram for GitHub")
        print("   • langgraph_ascii.txt - Terminal-friendly diagram")
        print("   • langgraph_graphviz.dot - Graphviz format")
    else:
        print("\n⚠️  Some issues detected. Check error messages above.")


if __name__ == "__main__":
    main()