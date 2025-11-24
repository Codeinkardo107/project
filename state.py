from typing import List, Optional, TypedDict, Annotated
from models import UserProfile, ExerciseResource, WeeklySchedule, Assessment, NutritionPlan
import operator

class AgentState(TypedDict):
    user_input: str
    profile: Optional[UserProfile]
    resources: Annotated[List[ExerciseResource], operator.add] # Append resources if needed
    schedule: Optional[WeeklySchedule]
    assessment: Optional[Assessment] # Feasibility check result
    nutrition: Optional[NutritionPlan] # Nutrition plan
    feedback: Optional[str] # User feedback for modifications
    iteration_count: int # To prevent infinite loops
    include_youtube: bool # Whether to include YouTube links
