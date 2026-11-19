import sys
import os
from crewai import Task, Agent

current_dir = os.path.dirname(os.path.abspath(__file__))
extraction_dir = os.path.dirname(current_dir)
sys.path.append(extraction_dir)

# Importa le costanti dei prompt originali 
from prompt import PROMPT_BASE, PROMPT_STRUTTURA

def create_extraction_task(agent: Agent, case_title: str):
    # Invece di passare l'intero testo di Wikipedia di migliaia di parole (come in Variante 1),
    # creo un'istruzione operativa usando il titolo dinamico del caso passato dall'orchestratore.
    testo_sostitutivo = f"Use the 'read_case_document' tool with the argument '{case_title}' to read the text."
    
    # Questo è il passaggio per innescare il loop ReAct: sostituisco il segnaposto {testo_caso} 
    # nel prompt originale con la mia istruzione. L'agente leggerà il prompt, vedrà che non 
    # c'è il testo ma c'è l'indicazione di usare il tool, e inizierà a ragionare.
    prompt_completo = PROMPT_BASE.replace("{testo_caso}", testo_sostitutivo)
    prompt_completo += "\n\n" + PROMPT_STRUTTURA

    # Restituisco l'oggetto Task nativo di CrewAI, vincolandolo a produrre il JSON
    return Task(
        description=f"Process the case titled '{case_title}'.\n\nRules to strictly follow:\n{prompt_completo}",
        expected_output="A raw, valid JSON string containing exactly the 'entities' and 'relationships' keys.",
        agent=agent
    )