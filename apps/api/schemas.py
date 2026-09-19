from pydantic import BaseModel, Field
from typing import List, Optional

class OrchestrationRequest(BaseModel):
    user_query: str = Field(..., description="The Bengali text input from the user")
    location: Optional[str] = Field(None, description="User's current location")
    user_id: Optional[str] = Field(None, description="Unique identifier for the user")
    selected_agent: Optional[str] = Field(None, description="Manually selected agent override")

class ExtractedEntity(BaseModel):
    entity_type: str = Field(..., description="Type of entity (e.g., product, service, location, date, organization)")
    entity_value: str = Field(..., description="Value of the entity")

class OrchestrationResponse(BaseModel):
    agent_name: str = Field(..., description="Name of the selected agent (e.g., StudentAgent, ConsumerAgent, CitizenAgent, FarmerAgent, MarketAgent, WasteAgent, or None if unclear)")
    confidence_score: float = Field(..., description="Confidence score of the intent mapping (0.0 to 1.0)")
    extracted_entities: List[ExtractedEntity] = Field(default_factory=list, description="Entities extracted from the user query")
    next_action: str = Field(..., description="Next action to take, or fallback question in Bengali if intent is unclear")
    requires_clarification: bool = Field(..., description="True if the intent is unclear and fallback question is provided")
