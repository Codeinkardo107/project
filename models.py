from pydantic import BaseModel, Field
from typing import List, Optional

class UserProfile(BaseModel):
    goal: str = Field(description="The user's specific fitness goal (e.g., '1 muscleup', 'handstand').")
    current_fitness: str = Field(description="User's current fitness level (e.g., '10 pushups', '20 pullups').")
    time_per_day: int = Field(default=30, description="Time available per day in minutes.")
    days_per_week: int = Field(default=3, description="Number of workout days per week.")
    equipment: List[str] = Field(default_factory=list, description="List of available equipment.")

class ExerciseResource(BaseModel):
    title: str = Field(description="Title of the resource or video.")
    url: str = Field(description="URL of the resource.")
    key_tips: List[str] = Field(default_factory=list, description="Key form cues or tips extracted from the resource.")

class DailyWorkout(BaseModel):
    day: str = Field(description="Day of the week (e.g., 'Monday', 'Day 1').")
    exercises: List[str] = Field(description="List of exercises to perform.")
    duration: str = Field(description="Estimated duration of the workout.")

class WeeklySchedule(BaseModel):
    workouts: List[DailyWorkout] = Field(description="List of daily workouts for the week.")
    notes: Optional[str] = Field(description="General notes or focus for the week.")
    estimated_time: str = Field(description="Estimated time to achieve the goal (e.g., '3 months').")
