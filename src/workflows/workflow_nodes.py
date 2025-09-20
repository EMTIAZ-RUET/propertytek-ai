"""
LangGraph Workflow Nodes - Modular Structure with Visualization Tracking
"""

from .nodes.intent_analyzer import IntentAnalyzerNode
from .nodes.property_search import PropertySearchNode
from .nodes.appointment_scheduler import AppointmentSchedulerNode
from .nodes.user_info_collector import UserInfoCollectorNode
from .nodes.calendar_manager import CalendarManagerNode
from .nodes.sms_sender import SMSSenderNode
from .nodes.response_generator import ResponseGeneratorNode
from .nodes.reflection import ReflectionNode
from src.visualization.node_wrapper import track_node_execution


class WorkflowNodes:
    """Modular LangGraph workflow nodes using separate node classes"""
    
    def __init__(self):
        # Initialize all node instances
        self.intent_analyzer = IntentAnalyzerNode()
        self.property_search = PropertySearchNode()
        self.appointment_scheduler = AppointmentSchedulerNode()
        self.user_info_collector = UserInfoCollectorNode()
        self.calendar_manager = CalendarManagerNode()
        self.sms_sender = SMSSenderNode()
        self.response_generator = ResponseGeneratorNode()
        self.reflection = ReflectionNode()
    
    # Delegate methods to appropriate node instances with visualization tracking
    @track_node_execution("analyze_intent")
    async def analyze_intent(self, state, config=None):
        return await self.intent_analyzer.analyze_intent(state, config)
    
    @track_node_execution("search_properties")
    async def search_properties(self, state, config=None):
        return await self.property_search.search_properties(state, config)
    
    @track_node_execution("get_available_slots")
    async def get_available_slots(self, state, config=None):
        return await self.appointment_scheduler.get_available_slots(state, config)
    
    @track_node_execution("collect_user_info")
    async def collect_user_info(self, state, config=None):
        return await self.user_info_collector.collect_user_info(state, config)
    
    @track_node_execution("create_calendar_event")
    async def create_calendar_event(self, state, config=None):
        return await self.calendar_manager.create_calendar_event(state, config)
    
    @track_node_execution("send_sms_confirmation")
    async def send_sms_confirmation(self, state, config=None):
        return await self.sms_sender.send_sms_confirmation(state, config)
    
    @track_node_execution("generate_response")
    async def generate_response(self, state, config=None):
        return await self.response_generator.generate_response(state, config)

    @track_node_execution("reflect")
    async def reflect(self, state, config=None):
        return await self.reflection.reflect(state, config)