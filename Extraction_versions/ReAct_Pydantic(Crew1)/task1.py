import sys
import os
from crewai import Task, Agent

# Setup dei percorsi per importare prompt e schema
current_dir = os.path.dirname(os.path.abspath(__file__))
extraction_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(extraction_dir)

sys.path.append(extraction_dir)
sys.path.append(root_dir)

from prompt import PROMPT_BASE
from schemas import SchemaGrafo  

def create_structured_extraction_task(agent: Agent, case_title: str):
    # Istruzione per forzare l'uso del tool di lettura testo
    testo_sostitutivo = f"Use the 'read_case_document' tool with the argument '{case_title}' to read the text."
    
    # Utilizza esclusivamente il prompt base (lo schema JSON è gestito da output_json)
    prompt_completo = PROMPT_BASE.replace("{testo_caso}", testo_sostitutivo)

    return Task(
        description=f"Process the case titled '{case_title}'.\n\nRules to strictly follow:\n{prompt_completo}",
        expected_output="A structured JSON object matching the SchemaGrafo definition.",
        agent=agent,
        output_json=SchemaGrafo  # CrewAI forza l'output in questo schema Pydantic
    )