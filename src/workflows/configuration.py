"""
Configuration schema for LangGraph workflow
"""

from pydantic import BaseModel, Field


class Configuration(BaseModel):
    """Runtime-tunable configuration for the workflow.

    Values can be overridden via LangGraph RunnableConfig["configurable"].
    """

    # LLM models
    intent_model: str = Field(default="gpt-4o-mini", description="Model for intent analysis")
    response_model: str = Field(default="gpt-4o-mini", description="Model for response generation")

    # Behavior flags
    enable_sms: bool = Field(default=True, description="Allow SMS confirmations")
    slot_duration_minutes: int = Field(default=60, description="Appointment duration in minutes")
    max_research_loops: int = Field(default=1, description="Max reflect/evaluate loops")
    parallel_fan_out: int = Field(default=1, description="Number of parallel searches")
    recursion_limit: int = Field(default=10, description="Maximum recursion depth to prevent infinite loops")
    max_search_iterations: int = Field(default=3, description="Maximum property search iterations")


