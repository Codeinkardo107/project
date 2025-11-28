from state import AgentState
from tools import save_workout_plan

def save_plan(state: AgentState):
    """Saves the plan to a file (MCP)."""
    print("--Saving Plan")
    schedule = state["schedule"]
    nutrition = state.get("nutrition")
    
    if schedule:
        content = f"# Weekly Workout Plan\n\n"
        content += f"**Goal:** {state['profile'].goal}\n"
        content += f"**Estimated Time:** {schedule.estimated_time}\n\n"
        
        if nutrition:
            content += "\n## Nutrition Plan\n"
            content += f"- **Diet Type:** {nutrition.diet_type}\n"
            content += f"- **Calories:** {nutrition.daily_calories} kcal\n"
            content += f"- **Macros:** {nutrition.macros}\n"
            content += f"- **Hydration:** {nutrition.hydration_tips}\n"
            content += "**\nMeal Suggestions:**\n"
            for meal in nutrition.meal_suggestions:
                content += f"- {meal}\n"
            content += "\n"
            
            content += "\n"
            
        # Add Resources Section
        resources = state.get("resources", [])
        if resources:
            content += "\n## Recommended Resources\n"
            include_youtube = state.get("include_youtube", False)
            for res in resources:
                if include_youtube:
                    content += f"- [{res.title}]({res.url})\n"
                if res.key_tips:
                    for tip in res.key_tips:
                        content += f"  - *Tip:* {tip}\n"
            content += "\n"

        content += f"\n\n## Schedule Notes\n{schedule.notes}\n\n"
        for workout in schedule.workouts:
            content += f"## {workout.day} ({workout.duration})\n"
            for exercise in workout.exercises:
                content += f"- {exercise}\n"
            content += "\n"
        
        result = save_workout_plan.invoke(content)
        return {"feedback": result}
    return {"feedback": "No schedule to save."}
