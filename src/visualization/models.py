"""
Data models for workflow visualization
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    SKIPPED = "skipped"


class NodeType(Enum):
    START = "start"
    END = "end"
    PROCESSOR = "processor"
    DECISION = "decision"
    PARALLEL = "parallel"


@dataclass
class NodeExecution:
    """Represents a single node execution"""
    node_id: str
    node_type: NodeType
    status: NodeStatus
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    start_time: datetime
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    @property
    def duration_ms(self) -> Optional[int]:
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time).total_seconds() * 1000)
        return None


@dataclass
class WorkflowExecution:
    """Represents a complete workflow execution"""
    execution_id: str
    user_query: str
    user_id: Optional[str]
    start_time: datetime
    end_time: Optional[datetime] = None
    status: NodeStatus = NodeStatus.RUNNING
    nodes: List[NodeExecution] = None
    current_node: Optional[str] = None
    
    def __post_init__(self):
        if self.nodes is None:
            self.nodes = []
    
    @property
    def duration_ms(self) -> Optional[int]:
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time).total_seconds() * 1000)
        return None


@dataclass
class NodeDefinition:
    """Defines a node in the workflow graph"""
    id: str
    label: str
    description: str
    node_type: NodeType
    position: Dict[str, float]  # x, y coordinates
    dependencies: List[str]  # List of node IDs this depends on
    expected_inputs: List[str]  # Expected input fields
    expected_outputs: List[str]  # Expected output fields
    is_conditional: bool = False
    parallel_group: Optional[str] = None


# Complete workflow node definitions
WORKFLOW_NODES = [
    NodeDefinition(
        id="start",
        label="Start",
        description="Entry point for user queries",
        node_type=NodeType.START,
        position={"x": 100, "y": 300},
        dependencies=[],
        expected_inputs=["user_query", "user_id"],
        expected_outputs=["user_query", "user_id"]
    ),
    NodeDefinition(
        id="analyze_intent",
        label="Intent\nAnalyzer",
        description="Analyzes user intent and extracts entities",
        node_type=NodeType.PROCESSOR,
        position={"x": 250, "y": 300},
        dependencies=["start"],
        expected_inputs=["user_query"],
        expected_outputs=["intent", "entities", "confidence"]
    ),
    NodeDefinition(
        id="search_properties",
        label="Property\nSearch",
        description="Searches for properties based on criteria",
        node_type=NodeType.PROCESSOR,
        position={"x": 400, "y": 200},
        dependencies=["analyze_intent"],
        expected_inputs=["search_filters", "search_query"],
        expected_outputs=["properties", "search_results"]
    ),
    NodeDefinition(
        id="reflect",
        label="Reflection\nEngine",
        description="Reflects on search results and decides next steps",
        node_type=NodeType.DECISION,
        position={"x": 550, "y": 200},
        dependencies=["search_properties"],
        expected_inputs=["properties", "search_query"],
        expected_outputs=["reflection_notes", "next_step", "needs_more_research"],
        is_conditional=True
    ),
    NodeDefinition(
        id="get_available_slots",
        label="Available\nSlots",
        description="Retrieves available appointment slots",
        node_type=NodeType.PROCESSOR,
        position={"x": 400, "y": 400},
        dependencies=["analyze_intent"],
        expected_inputs=["property_id", "date_preferences"],
        expected_outputs=["available_slots", "slot_count"]
    ),
    NodeDefinition(
        id="collect_user_info",
        label="User Info\nCollection",
        description="Collects required user information for booking",
        node_type=NodeType.PROCESSOR,
        position={"x": 550, "y": 400},
        dependencies=["get_available_slots"],
        expected_inputs=["required_fields"],
        expected_outputs=["user_name", "user_email", "user_phone", "user_pets"]
    ),
    NodeDefinition(
        id="create_calendar_event",
        label="Calendar\nManager",
        description="Creates Google Calendar event for appointment",
        node_type=NodeType.PROCESSOR,
        position={"x": 700, "y": 350},
        dependencies=["collect_user_info"],
        expected_inputs=["appointment_details", "user_info"],
        expected_outputs=["calendar_event_id", "event_link"],
        parallel_group="booking_actions"
    ),
    NodeDefinition(
        id="send_sms_confirmation",
        label="SMS\nSender",
        description="Sends SMS confirmation to user",
        node_type=NodeType.PROCESSOR,
        position={"x": 700, "y": 450},
        dependencies=["create_calendar_event"],
        expected_inputs=["phone_number", "appointment_details"],
        expected_outputs=["sms_sent", "sms_result"],
        parallel_group="booking_actions"
    ),
    NodeDefinition(
        id="generate_response",
        label="Response\nGenerator",
        description="Generates final response for user",
        node_type=NodeType.PROCESSOR,
        position={"x": 850, "y": 300},
        dependencies=["reflect", "send_sms_confirmation"],
        expected_inputs=["final_state", "context"],
        expected_outputs=["response_message", "suggested_actions"]
    ),
    NodeDefinition(
        id="end",
        label="End",
        description="Workflow completion",
        node_type=NodeType.END,
        position={"x": 1000, "y": 300},
        dependencies=["generate_response"],
        expected_inputs=["response_message"],
        expected_outputs=[]
    )
]


def get_node_by_id(node_id: str) -> Optional[NodeDefinition]:
    """Get node definition by ID"""
    return next((node for node in WORKFLOW_NODES if node.id == node_id), None)


def get_dependent_nodes(node_id: str) -> List[NodeDefinition]:
    """Get all nodes that depend on the given node"""
    return [node for node in WORKFLOW_NODES if node_id in node.dependencies]


def get_parallel_nodes(node_id: str) -> List[NodeDefinition]:
    """Get all nodes in the same parallel group"""
    node = get_node_by_id(node_id)
    if not node or not node.parallel_group:
        return []
    return [n for n in WORKFLOW_NODES if n.parallel_group == node.parallel_group]
