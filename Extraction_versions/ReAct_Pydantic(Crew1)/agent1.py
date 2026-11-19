import os
from crewai import Agent, LLM

def create_extractor_agent(tools: list):
    gemini_llm = LLM(
        model="gemini/gemini-flash-lite-latest",
        temperature=0,
        api_key=os.environ.get("GEMINI_API_KEY")
    )
    
    # Definisce l'agente e il suo perimetro operativo.
    return Agent(
        role="Investigative Knowledge Graph Analyst",
        goal="Extract comprehensive entities and semantic relationships from true crime cases using the provided tools.",
        backstory="You are a meticulous data scientist extracting structured Knowledge Graph triples from unstructured text. You never invent information.",
        tools=tools, # Passo la lista dei tool dinamicamente (conterrà il CaseReaderTool)
        llm=gemini_llm,
        verbose=True, #Ciclo TOA a schermo
        #non passa l'output ad altri agenti
        allow_delegation=False 
    )