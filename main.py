import os
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from state import AgentState
from nodes.trainer import collect_profile, search_exercises, process_resources, create_schedule, assess_feasibility, update_constraints
from nodes.nutrition_plan import generate_nutrition
from nodes.save_plan import save_plan
import subprocess
import base64
import requests
import atexit

# For opening output file.
def open_md_file():
    filename = "workout_plan.md"
    if os.path.exists(filename):
        os.startfile(filename)

# Load environment variables
load_dotenv()

def run_agent(user_input: str, include_youtube: bool = False, thread_id: str = "1"):
    # Define Graph
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("collect_profile", collect_profile)
    workflow.add_node("search_exercises", search_exercises)
    workflow.add_node("process_resources", process_resources)
    workflow.add_node("assess_feasibility", assess_feasibility)
    workflow.add_node("create_schedule", create_schedule)
    workflow.add_node("generate_nutrition", generate_nutrition)
    workflow.add_node("update_constraints", update_constraints)
    workflow.add_node("save_plan", save_plan)

    # Define Edges
    workflow.set_entry_point("collect_profile")
    workflow.add_edge("collect_profile", "search_exercises")
    workflow.add_edge("search_exercises", "process_resources")
    workflow.add_edge("process_resources", "assess_feasibility")
    
    # Parallel Execution: Assess -> Schedule AND Assess -> Nutrition
    workflow.add_edge("assess_feasibility", "create_schedule")
    workflow.add_edge("assess_feasibility", "generate_nutrition")
    
    # Nutrition flows to save_plan directly
    workflow.add_edge("generate_nutrition", "save_plan")
    
    # Conditional Edge Logic
    def check_feedback(state: AgentState):
        feedback = state.get("feedback", "")
        if feedback == "approve":
            return "save_plan"
        return "update_constraints"

    workflow.add_conditional_edges(
        "create_schedule",
        check_feedback,
        {
            "save_plan": "save_plan",
            "update_constraints": "update_constraints"
        }
    )
    
    workflow.add_edge("update_constraints", "create_schedule") # Cycle back
    workflow.add_edge("save_plan", END)

    



if __name__ == "__main__":
    print("--- AI Fitness Coach Setup ---")
    import uuid
    from langgraph.types import Command
    
    thread_id = str(uuid.uuid4())
    
    if 'goal' not in locals():
        goal = input("Enter your fitness goal (e.g., '1 muscleup'): ")
        current = input("Enter your current fitness level (comma separated values; e.g., '10 pushups'): ")
        time = input("Time available per day (in mins, default 30): ") or "30"
        days = input("Workout days per week (default 3): ") or "3"
        equipment = input("Equipment available (e.g., 'pullup bar', default 'none'): ") or "none"
        youtube = input("Do you want YouTube video links? (y/n): ").lower().startswith('y')

    user_in = (
        f"Goal: {goal}. "
        f"Current Level: {current}. "
        f"Time: {time} mins/day. "
        f"Days: {days} days/week. "
        f"Equipment: {equipment}."
    )
    
    run_agent(user_in, include_youtube=youtube, thread_id=thread_id)

    # For opening the output file.
    atexit.register(open_md_file)