from state import AgentState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from models import NutritionPlan

def generate_nutrition(state: AgentState):
    """Generates a nutrition plan based on the profile."""
    print("--- Generating Nutrition Plan ---")
    profile = state["profile"]
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    parser = PydanticOutputParser(pydantic_object=NutritionPlan)
    prompt = ChatPromptTemplate.from_template(
        "Generate a nutrition plan for a user with the following profile:\n"
        "{profile}\n"
        "The plan should support their fitness goal.\n"
        "{format_instructions}"
    )
    chain = prompt | llm | parser
    nutrition = chain.invoke({
        "profile": profile.model_dump_json(),
        "format_instructions": parser.get_format_instructions()
    })
    
    return {"nutrition": nutrition}