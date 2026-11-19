import os
from dotenv import load_dotenv
from crewai import Agent, LLM

# import dei tool
from Crew3.tools_crew3 import interroga_wikidata_sparql, ispeziona_qid

load_dotenv()

llm_gemini = LLM(
    model="gemini-flash-lite-latest",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.0
)

agente_ricercatore_lod = Agent(
    role="Semantic Web Data Extractor & Validator",
    goal="Validate the identity of a Q-ID through ontological inspection and subsequently extract specific properties from Wikidata.",
    backstory=(
        "You are an engineer specialized in Linked Open Data and the Semantic Web. "
        "Before extracting any property, your core rule is to use the 'Ispeziona_Wikidata_QID' tool "
        "on the received Q-ID to verify its class (P31), label, and description, in order to discard "
        "any 'Semantic Shift' or ambiguous entities. "
        "Once identity is validated, you use the 'Interroga_Wikidata_SPARQL' tool with OPTIONAL clauses to extract "
        "structured data without ever hallucinating results."
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm_gemini,
    tools=[ispeziona_qid, interroga_wikidata_sparql]
)