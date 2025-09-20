"""
Integrated Workflow Visualizer - Direct LangGraph Integration
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    ERROR = "error"
    SKIPPED = "skipped"

@dataclass
class NodeExecution:
    node_id: str
    status: NodeStatus
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    timestamp: str
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None

@dataclass
class WorkflowExecution:
    id: str
    user_query: str
    user_id: str
    start_time: str
    end_time: Optional[str] = None
    status: str = "running"
    nodes: List[NodeExecution] = None
    current_node: Optional[str] = None

    def __post_init__(self):
        if self.nodes is None:
            self.nodes = []

class WorkflowVisualizer:
    """Integrated workflow visualizer that tracks LangGraph execution directly"""
    
    # Make NodeStatus accessible as class attribute
    NodeStatus = NodeStatus
    
    def __init__(self):
        self.executions: Dict[str, WorkflowExecution] = {}
        self.current_execution: Optional[WorkflowExecution] = None
        self.node_start_times: Dict[str, float] = {}
        
        # Complete workflow structure
        self.workflow_nodes = {
            "analyze_intent": {
                "label": "Intent Analyzer",
                "type": "processor",
                "dependencies": [],
                "expected_inputs": ["user_query", "user_id"],
                "expected_outputs": ["intent", "entities", "confidence"]
            },
            "search_properties": {
                "label": "Property Search", 
                "type": "processor",
                "dependencies": ["analyze_intent"],
                "expected_inputs": ["intent", "search_criteria"],
                "expected_outputs": ["properties", "search_results"]
            },
            "reflect": {
                "label": "Reflection Engine",
                "type": "decision",
                "dependencies": ["search_properties"],
                "expected_inputs": ["properties", "search_results"],
                "expected_outputs": ["next_step", "reflection_summary"]
            },
            "get_available_slots": {
                "label": "Available Slots",
                "type": "processor", 
                "dependencies": ["analyze_intent"],
                "expected_inputs": ["property_id", "date_range"],
                "expected_outputs": ["available_slots", "slot_count"]
            },
            "collect_user_info": {
                "label": "User Info Collection",
                "type": "processor",
                "dependencies": ["get_available_slots"],
                "expected_inputs": ["required_fields", "current_info"],
                "expected_outputs": ["user_info", "missing_fields", "validation_status"]
            },
            "create_calendar_event": {
                "label": "Calendar Manager",
                "type": "processor",
                "dependencies": ["collect_user_info"],
                "expected_inputs": ["appointment_details", "user_info"],
                "expected_outputs": ["calendar_event_id", "event_status"]
            },
            "send_sms_confirmation": {
                "label": "SMS Sender",
                "type": "processor",
                "dependencies": ["create_calendar_event"],
                "expected_inputs": ["phone_number", "appointment_details"],
                "expected_outputs": ["sms_sent", "sms_status"]
            },
            "generate_response": {
                "label": "Response Generator",
                "type": "processor",
                "dependencies": ["reflect", "send_sms_confirmation"],
                "expected_inputs": ["workflow_state", "results"],
                "expected_outputs": ["response_message", "suggested_actions"]
            }
        }
        
        # Workflow connections
        self.workflow_connections = [
            {"source": "analyze_intent", "target": "search_properties", "type": "conditional"},
            {"source": "analyze_intent", "target": "get_available_slots", "type": "conditional"},
            {"source": "analyze_intent", "target": "generate_response", "type": "conditional"},
            {"source": "search_properties", "target": "reflect", "type": "sequential"},
            {"source": "reflect", "target": "generate_response", "type": "conditional"},
            {"source": "reflect", "target": "search_properties", "type": "loop"},
            {"source": "get_available_slots", "target": "collect_user_info", "type": "sequential"},
            {"source": "collect_user_info", "target": "create_calendar_event", "type": "conditional"},
            {"source": "collect_user_info", "target": "generate_response", "type": "conditional"},
            {"source": "create_calendar_event", "target": "send_sms_confirmation", "type": "conditional"},
            {"source": "create_calendar_event", "target": "generate_response", "type": "conditional"},
            {"source": "send_sms_confirmation", "target": "generate_response", "type": "sequential"}
        ]

    async def start_execution(self, user_query: str, user_id: str) -> str:
        """Start tracking a new workflow execution"""
        execution_id = f"exec_{int(time.time() * 1000)}"
        
        execution = WorkflowExecution(
            id=execution_id,
            user_query=user_query,
            user_id=user_id,
            start_time=datetime.now().isoformat(),
            status="running"
        )
        
        self.executions[execution_id] = execution
        self.current_execution = execution
        
        # Track workflow start
        await self.track_node_execution("analyze_intent", NodeStatus.RUNNING, 
                                      {"user_query": user_query, "user_id": user_id})
        
        return execution_id

    async def track_node_execution(self, node_id: str, status: NodeStatus, 
                                 input_data: Dict[str, Any] = None, 
                                 output_data: Dict[str, Any] = None,
                                 error_message: str = None):
        """Track node execution with status updates"""
        if not self.current_execution:
            return
            
        # Calculate duration if completing a node
        duration_ms = None
        if status == NodeStatus.COMPLETED and node_id in self.node_start_times:
            duration_ms = int((time.time() - self.node_start_times[node_id]) * 1000)
            del self.node_start_times[node_id]
        elif status == NodeStatus.RUNNING:
            self.node_start_times[node_id] = time.time()
            
        # Find existing node execution or create new one
        existing_node = None
        for node in self.current_execution.nodes:
            if node.node_id == node_id:
                existing_node = node
                break
                
        if existing_node:
            # Update existing node
            existing_node.status = status
            existing_node.timestamp = datetime.now().isoformat()
            if output_data:
                existing_node.output_data.update(output_data)
            if duration_ms:
                existing_node.duration_ms = duration_ms
            if error_message:
                existing_node.error_message = error_message
        else:
            # Create new node execution
            node_execution = NodeExecution(
                node_id=node_id,
                status=status,
                input_data=input_data or {},
                output_data=output_data or {},
                timestamp=datetime.now().isoformat(),
                duration_ms=duration_ms,
                error_message=error_message
            )
            self.current_execution.nodes.append(node_execution)
            
        # Update current node
        if status == NodeStatus.RUNNING:
            self.current_execution.current_node = node_id
        elif status in [NodeStatus.COMPLETED, NodeStatus.ERROR, NodeStatus.SKIPPED]:
            self.current_execution.current_node = None

    async def complete_execution(self, final_data: Dict[str, Any] = None):
        """Complete the current workflow execution"""
        if not self.current_execution:
            return
            
        self.current_execution.end_time = datetime.now().isoformat()
        self.current_execution.status = "completed"
        
        # Ensure generate_response is marked as completed
        await self.track_node_execution("generate_response", NodeStatus.COMPLETED,
                                      output_data=final_data or {})

    def get_workflow_structure(self) -> Dict[str, Any]:
        """Get complete workflow structure for visualization"""
        return {
            "nodes": self.workflow_nodes,
            "connections": self.workflow_connections,
            "executions": {exec_id: asdict(execution) for exec_id, execution in self.executions.items()}
        }

    def get_current_execution_data(self) -> Dict[str, Any]:
        """Get current execution data for real-time updates"""
        if not self.current_execution:
            return {}
            
        return {
            "execution": asdict(self.current_execution),
            "workflow_structure": {
                "nodes": self.workflow_nodes,
                "connections": self.workflow_connections
            }
        }

    async def skip_unused_nodes(self, intent: str):
        """Mark nodes as skipped based on workflow path"""
        # Define which nodes are used for different intents
        intent_node_map = {
            "property_search": ["analyze_intent", "search_properties", "reflect", "generate_response"],
            "schedule_tour": ["analyze_intent", "get_available_slots", "collect_user_info", 
                            "create_calendar_event", "send_sms_confirmation", "generate_response"],
            "general_info": ["analyze_intent", "generate_response"]
        }
        
        used_nodes = intent_node_map.get(intent, ["analyze_intent", "generate_response"])
        
        # Skip unused nodes
        for node_id in self.workflow_nodes.keys():
            if node_id not in used_nodes:
                await self.track_node_execution(node_id, NodeStatus.SKIPPED)

# Global visualizer instance
workflow_visualizer = WorkflowVisualizer()
