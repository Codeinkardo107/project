from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.documents import Document
from models import UserProfile, WeeklySchedule, ExerciseResource, Assessment
from state import AgentState
from tools import web_search
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM and Embeddings
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings()

def collect_profile(state: AgentState):
    """Extracts user profile from natural language input."""
    print("--- Collecting Profile ---")
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
    print("--- Searching Exercises ---")
    profile = state["profile"]
    if not profile:
        return {}
    
    query = f"how to achieve {profile.goal} progression exercises tutorial"
    # Placeholder for actual search logic if needed, but process_resources does the heavy lifting
    return {"resources": []} 
