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