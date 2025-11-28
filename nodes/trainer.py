from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from state import AgentState
from tools import web_search
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.documents import Document
from models import UserProfile, WeeklySchedule, ExerciseResource, Assessment
load_dotenv()

# Initialize LLM and Embeddings
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings()

def collect_profile(state: AgentState):
    """Extracts user profile from natural language input."""
    print("--Collecting Profile")
    parser = PydanticOutputParser(pydantic_object=UserProfile)
    prompt = ChatPromptTemplate.from_template(
        "Extract the user's fitness profile from the following description.\n"
        "{format_instructions}\n\n"
        "User Input: {user_input}"
    )

    chain = prompt | llm | parser
    try:
        profile = chain.invoke({
            "user_input": state["user_input"],
            "format_instructions": parser.get_format_instructions()
        })
        return {"profile": profile}
    except Exception as e:
        print(f"Error extracting profile: {e}")
        return {"profile": None} 

def search_exercises(state: AgentState):
    """This searches for exercises based on the goal."""
    print("--Searching Exercises")
    profile = state["profile"]
    if not profile:
        return {}
    
    query = f"how to achieve {profile.goal} progression exercises tutorial"
    # Placeholder for actual search logic if needed, but process_resources does the heavy lifting
    return {"resources": []} 


def process_resources(state: AgentState):
    """This scrapes content, creates vector store, and retrieves key tips (RAG)."""
    print("--Processing Resources")
    profile = state["profile"]
    include_youtube = state.get("include_youtube", False)
    
    if include_youtube:
        links_query = f"best youtube tutorials for {profile.goal}"
    else:
        links_query = f"best articles or written tutorials for {profile.goal}"
        
    search_results = web_search.invoke(links_query)
    
    docs = []
    resources = []
    
    for result in search_results:
        content = result.get("content", "")
        url = result.get("url", "")
        
        if not include_youtube and "youtube.com" in url:
            continue
            
        docs.append(Document(page_content=content, metadata={"source": url}))
        
        resources.append(ExerciseResource(
            title=f"Resource for {profile.goal}",
            url=url,
            key_tips=[] 
        ))

    if not docs:
        return {"resources": []}

    vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings, collection_name="fitness_rag")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    
    relevant_docs = retriever.invoke(f"tips and form cues for {profile.goal}")
    context = "\n".join([d.page_content for d in relevant_docs])
    tip_prompt = ChatPromptTemplate.from_template(
        "Based on the following text, extract 3 key form tips for {goal}.\n"
        "Text: {context}"
    )
    tip_chain = tip_prompt | llm
    tips_response = tip_chain.invoke({"goal": profile.goal, "context": context})
    
    if resources:
        resources[0].key_tips = [tips_response.content]
    
    return {"resources": resources}

def assess_feasibility(state: AgentState):
    """Estimates time to goal and checks feasibility (< 2 years)."""
    print("--Assessing Feasibility")
    profile = state["profile"]
    
    parser = PydanticOutputParser(pydantic_object=Assessment)
    prompt = ChatPromptTemplate.from_template(
        "Assess the feasibility of the following fitness goal.\n"
        "Profile: {profile}\n"
        "1. Analyze the gap between Current Fitness and Goal.\n"
        "2. Consider general conditioning: A user with high reps in other areas (e.g., 100+ pushups) has high work capacity and should be assigned a SHORTER estimated time compared to someone with lower general fitness, even for unrelated skills.\n"
        "3. **CRITICAL: Factor in Training Volume**:\n"
        "   - **Days per Week**: Training 6-7 days/week should result in a significantly FASTER timeline (approx 30-40% faster) than training 2-3 days/week, assuming recovery is managed.\n"
        "   - **Time per Day**: More time allows for more volume/accessory work, further accelerating progress.\n"
        "4. Provide a REALISTIC time estimate based on progressive overload.\n"
        "Examples:\n"
        "- 10 -> 50 pushups (3 days/week): 8-10 weeks\n"
        "- 10 -> 50 pushups (6 days/week): 5-7 weeks\n"
        "- 0 -> 10 pullups (3 days/week): 4-5 months\n"
        "- 0 -> 10 pullups (6 days/week): 2.5-3.5 months\n"
        "Is it achievable within 2 years with the given time constraints?\n"
        "{format_instructions}"
    )
    chain = prompt | llm | parser
    assessment = chain.invoke({
        "profile": profile.model_dump_json(),
        "format_instructions": parser.get_format_instructions()
    })
    
    return {"assessment": assessment}

def create_schedule(state: AgentState):
    """Generates the weekly schedule."""
    print("--Creating Schedule")
    profile = state["profile"]
    resources = state["resources"]
    assessment = state["assessment"]
    
    parser = PydanticOutputParser(pydantic_object=WeeklySchedule)
    prompt = ChatPromptTemplate.from_template(
        "Create a weekly workout schedule for a user with the following profile:\n"
        "{profile}\n\n"
        "Estimated Time to Goal: {estimated_time}\n"
        "Incorporate these key tips/resources:\n"
        "{resources}\n\n"
        "{format_instructions}"
    )
    chain = prompt | llm | parser
    schedule = chain.invoke({
        "profile": profile.model_dump_json(),
        "estimated_time": assessment.estimated_time,
        "resources": [r.model_dump_json() for r in resources],
        "format_instructions": parser.get_format_instructions()
    })
    schedule.estimated_time = assessment.estimated_time
    return {"schedule": schedule}

def update_constraints(state: AgentState):
    """Updates user constraints based on feedback."""
    print("--Updating Constraints")
    profile = state["profile"]
    feedback = state.get("feedback", "")
    
    if not feedback:
        return {}

    parser = PydanticOutputParser(pydantic_object=UserProfile)
    prompt = ChatPromptTemplate.from_template(
        "Update the following user fitness profile based on the user's feedback.\n"
        "Current Profile:\n{profile}\n\n"
        "User Feedback: {feedback}\n\n"
        "Update the profile fields (e.g., time_per_day, days_per_week, equipment) to reflect the feedback.\n"
        "Keep other fields unchanged unless the feedback explicitly contradicts them.\n"
        "{format_instructions}"
    )
    
    chain = prompt | llm | parser
    try:
        updated_profile = chain.invoke({
            "profile": profile.model_dump_json(),
            "feedback": feedback,
            "format_instructions": parser.get_format_instructions()
        })
        print(f"Updated Profile: {updated_profile}")
        return {
            "profile": updated_profile, 
            "iteration_count": state["iteration_count"] + 1,
            "feedback": None # Clear feedback after processing
        }
    except Exception as e:
        print(f"Error updating profile: {e}")
        return {"iteration_count": state["iteration_count"] + 1}