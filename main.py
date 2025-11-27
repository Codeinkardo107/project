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
load_dotenv()

# For opening output file.
def open_md_file():
    filename = "workout_plan.md"
    if os.path.exists(filename):
        os.startfile(filename)

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

    # Edges
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

    
    # Compile with Checkpointer and Interrupt
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory, interrupt_after=["create_schedule"])

    # Save Graph Image
    try:
        # mermaid code
        mermaid_code = app.get_graph().draw_mermaid()
        
        # Save mermaid code to file
        with open("graph.mmd", "w") as f:
            f.write(mermaid_code)
        
        cli_success = False
        try:
            result = subprocess.run(
                ["mmdc", "-i", "graph.mmd", "-o", "output_graph.jpg"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                cli_success = True
        except FileNotFoundError:
            pass 

        if not cli_success:
            try:
                graphbytes = mermaid_code.encode("utf8")
                base64_bytes = base64.b64encode(graphbytes)
                base64_string = base64_bytes.decode("ascii")
                
                url = "https://mermaid.ink/img/" + base64_string
                response = requests.get(url)
                
                if response.status_code == 200:
                    with open("output_graph.png", "wb") as f:
                        f.write(response.content)
                else:
                    print(f"Remote rendering failed: {response.status_code}")
            except Exception as e:
                print(f"Remote rendering error: {e}")

    except Exception as e:
        print(f"Graph generation failed: {e}")

    # Config for this thread
    config = {"configurable": {"thread_id": thread_id}}

    print(f"Starting Agent with input: {user_input}")
    initial_state = {
        "user_input": user_input, 
        "iteration_count": 0, 
        "resources": [],
        "include_youtube": include_youtube
    }
    
    # 1. Run until Schedule is created
    app.invoke(initial_state, config=config)
    
    # Loop for feedback
    while True:
        snapshot = app.get_state(config)
        if not snapshot.values.get("schedule"):
            print("Error: No schedule generated.")
            break
            
        schedule = snapshot.values["schedule"]
        print("\n--- Generated Schedule ---")
        print(f"Estimated Time: {schedule.estimated_time}")
        print(f"Notes: {schedule.notes}")
        # Print first day as preview
        if schedule.workouts:
            w = schedule.workouts[0]
            print(f"Preview ({w.day}): {', '.join(w.exercises[:3])}...")
            
        choice = input("\nDo you approve this plan? (y/n): ").lower()
        
        if choice.startswith('y'):
            print("Approving plan...")
            # Update state explicitly before resuming
            app.update_state(config, {"feedback": "approve"}, as_node="create_schedule")
            # Resume execution
            app.invoke(None, config=config) 
            break # Done
        else:
            print("Requesting changes...")
            new_constraints = input("What would you like to change? (e.g., 'more days', 'less time'): ")
            # Update state with new feedback
            app.update_state(config, {"feedback": new_constraints}, as_node="create_schedule")
            # Resume execution
            app.invoke(None, config=config)
            # The graph will run update_constraints -> create_schedule and interrupt again
            continue


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