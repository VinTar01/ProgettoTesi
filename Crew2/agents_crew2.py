import os
from dotenv import load_dotenv
from crewai import Agent, LLM

# Importa i custom tools
from Crew2.tools_crew2 import *

load_dotenv()

# Configurazione del modello LLM
llm_neo4j = LLM(
    model="gemini-flash-lite-latest",
    api_key=os.getenv("GEMINI_API_KEY"), # 
    temperature=0.1 
)

# definisco l'agente amministratore db
agente_dba = Agent(
    role="Neo4j Database Administrator",
    goal="Take JSON structures containing entities, textual properties, and relationships and write them into a Neo4j graph database safely and efficiently.",
    backstory=(
        "You are a data engineer specialized in graph databases. "
        "You have complete mastery of the Cypher query language. Your top priority is idempotency: "
        "you ALWAYS use the MERGE command instead of CREATE to avoid duplicating nodes, "
        "and you cleanly map optional properties using the SET command, strictly ignoring null values. "
        "Before creating relationships, you ensure that both the source and target nodes exist."
    ),
    tools=[execute_cypher_tool, apoc_merge_entities_tool],
    llm=llm_neo4j,
    verbose=True,
    allow_delegation=False
)