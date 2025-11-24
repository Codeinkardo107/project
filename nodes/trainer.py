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


def process_resources(state: AgentState):
    """This scrapes content, creates vector store, and retrieves key tips (RAG)."""
    print("--- Processing Resources ---")
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

