import streamlit as st
import uuid
from main import run_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from state import AgentState
from nodes.trainer import collect_profile, search_exercises, process_resources, create_schedule, assess_feasibility, update_constraints
from nodes.nutrition_plan import generate_nutrition
from nodes.save_plan import save_plan
import os

# Page Config
st.set_page_config(page_title="AI Fitness Coach", page_icon="💪", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "schedule" not in st.session_state:
    st.session_state.schedule = None

if "nutrition" not in st.session_state:
    st.session_state.nutrition = None

if "app" not in st.session_state:
    # Re-create the graph here to persist it in session state if needed, 
    # or just re-compile it every time. Re-compiling is safer for statelessness unless we need the exact object.
    # However, MemorySaver is in-memory, so we need to keep the 'memory' object or the 'app' object alive 
    # if we want to use checkpointers.
    pass

# Graph Definition (Same as main.py but adapted for Streamlit)
@st.cache_resource
def get_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("collect_profile", collect_profile)
    workflow.add_node("search_exercises", search_exercises)
    workflow.add_node("process_resources", process_resources)
    workflow.add_node("assess_feasibility", assess_feasibility)
    workflow.add_node("create_schedule", create_schedule)
    workflow.add_node("generate_nutrition", generate_nutrition)
    workflow.add_node("update_constraints", update_constraints)
    workflow.add_node("save_plan", save_plan)

    workflow.set_entry_point("collect_profile")
    workflow.add_edge("collect_profile", "search_exercises")
    workflow.add_edge("search_exercises", "process_resources")
    workflow.add_edge("process_resources", "assess_feasibility")
    workflow.add_edge("assess_feasibility", "create_schedule")
    workflow.add_edge("assess_feasibility", "generate_nutrition")
    workflow.add_edge("generate_nutrition", "save_plan")

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
    
    workflow.add_edge("update_constraints", "assess_feasibility")
    workflow.add_edge("save_plan", END)

    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory, interrupt_after=["create_schedule"])
    return app

app = get_graph()
config = {"configurable": {"thread_id": st.session_state.thread_id}}

# Sidebar Inputs
with st.sidebar:
    st.title(" Your Profile")
    goal = st.text_input("Fitness Goal", key="eg. 1 muscle up")
    current_fitness = st.text_input("Current Level", key="eg. 10 pull ups")
    time_per_day = st.number_input("Mins/Day", min_value=10, value=30, step=5)
    days_per_week = st.number_input("Days/Week", min_value=1, max_value=7, value=3)
    equipment = st.text_input("Equipment", key="eg. dumbbell, pullup bar")
    include_youtube = st.checkbox("Include YouTube Links", value=True)
    
    start_btn = st.button("Generate Plan", type="primary")

# Main Content
st.title("AI Fitness Coach")

if start_btn:
    with st.spinner("Generating your personalized plan... This may take a minute."):
        user_input = (
            f"Goal: {goal}. "
            f"Current Level: {current_fitness}. "
            f"Time: {time_per_day} mins/day. "
            f"Days: {days_per_week} days/week. "
            f"Equipment: {equipment}."
        )
        
        initial_state = {
            "user_input": user_input, 
            "iteration_count": 0, 
            "resources": [],
            "include_youtube": include_youtube
        }
        
        # Run until interruption
        for event in app.stream(initial_state, config=config):
            pass # Just run it
            
        # Get state after run
        snapshot = app.get_state(config)
        if snapshot.values.get("schedule"):
            st.session_state.schedule = snapshot.values["schedule"]
            st.session_state.nutrition = snapshot.values.get("nutrition")
            st.session_state.needs_review = True
        else:
            st.error("Failed to generate schedule.")

# Display Plan
if st.session_state.get("needs_review"):
    schedule = st.session_state.schedule
    nutrition = st.session_state.nutrition
    
    st.success(f"Plan Generated! Estimated Time: {schedule.estimated_time}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Weekly Schedule")
        st.info(f"**Notes:** {schedule.notes}")
        for workout in schedule.workouts:
            with st.expander(f"**{workout.day}** ({workout.duration})"):
                for exercise in workout.exercises:
                    st.write(f"- {exercise}")

    with col2:
        if nutrition:
            st.subheader("Nutrition Plan")
            st.write(f"**Diet:** {nutrition.diet_type}")
            st.write(f"**Calories:** {nutrition.daily_calories}")
            st.write(f"**Macros:** {nutrition.macros}")
            st.write("**Meals:**")
            for meal in nutrition.meal_suggestions:
                st.write(f"- {meal}")
    
    st.divider()
    
    # Feedback Section
    st.subheader("Review & Approve")
    
    col_approve, col_modify = st.columns(2)
    
    with col_approve:
        if st.button("✅ Approve Plan"):
            with st.spinner("Saving plan..."):
                app.update_state(config, {"feedback": "approve"}, as_node="create_schedule")
                for event in app.stream(None, config=config):
                    pass
                st.session_state.needs_review = False
                st.success("Plan saved to `workout_plan.md`!")
                
                # Read and display the file content
                if os.path.exists("workout_plan.md"):
                    with open("workout_plan.md", "r") as f:
                        st.download_button("Download Plan", f, file_name="workout_plan.md")

    with col_modify:
        feedback_text = st.text_input("Request Changes (e.g., 'less days', 'more cardio')")
        if st.button("🔄 Update Plan"):
            if feedback_text:
                with st.spinner("Updating plan based on feedback..."):
                    app.update_state(config, {"feedback": feedback_text}, as_node="create_schedule")
                    for event in app.stream(None, config=config):
                        pass
                    
                    # Refresh state
                    snapshot = app.get_state(config)
                    if snapshot.values.get("schedule"):
                        st.session_state.schedule = snapshot.values["schedule"]
                        st.session_state.nutrition = snapshot.values.get("nutrition")
                        st.rerun()
            else:
                st.warning("Please enter feedback first.")
