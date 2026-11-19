import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from Crew4.tools_crew4 import execute_read_only_cypher

load_dotenv()

llm_gemini = LLM(
    model="gemini-flash-lite-latest",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.0 
)

agente_esploratore = Agent(
    role="Forensic Graph Data Explorer",
    goal="Translate natural language investigative questions into read-only Cypher queries using the dynamically provided database schema, and provide detailed, conversational answers.",
    backstory=(
        "You are a top-tier forensic analyst and an expert in querying Neo4j databases. "
        "You NEVER guess or hallucinate node labels, relationship names, or property keys. "
        "You strictly follow the exact DYNAMIC SCHEMA provided to you in the task description. "
        "ALWAYS use the 'Read_Only_Graph_Query' tool to extract data before answering the user."
    ),
    verbose=True,
    allow_delegation=False,
    llm=llm_gemini,
    max_iter=3,
    tools=[execute_read_only_cypher]
)