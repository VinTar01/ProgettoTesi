import os
from crewai import Agent, LLM

def create_extractor_agent(tools: list):
    gemini_llm = LLM(
        model="gemini/gemini-flash-lite-latest",
        temperature=0,
        api_key=os.environ.get("GEMINI_API_KEY")
    )
    
    # # Inizializzazione dell'agente estrattore
    return Agent(
        role="Investigative Knowledge Graph Analyst",
        goal="Extract comprehensive entities and semantic relationships from true crime cases using the provided tools.",
        backstory="You are a meticulous data scientist extracting structured Knowledge Graph triples from unstructured text. You never invent information.",
        tools=tools,# Tool assegnati all'agente(CaseReaderTool)
        llm=gemini_llm,
        verbose=True, # Abilita il logging dettagliato del ciclo Thought-Action-Observation
        # Disabilito la delega perché in questo esperimento di isolamento l'agente 
        allow_delegation=False 
    )