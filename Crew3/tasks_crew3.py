from crewai import Task
from Crew3.agents_crew3 import agente_ricercatore_lod

task_ricerca_wikidata = Task(
    description="""
    You have received the entity "{nome_entita}" (Label in Neo4j: "{label_entita}") associated with the Q-ID: {q_id}.
    
    STEP 1 (Ontological Validation):
    Use the 'Ispeziona_Wikidata_QID' tool passing the Q-ID {q_id} to inspect its nature, description, and class of belonging (P31).
    - If the inspection reveals a clear 'Semantic Shift' (e.g., an entity of a completely unrelated type to the label "{label_entita}"), stop the extraction and return a JSON with {"trovato": false}.
    
    STEP 2 (Data Extraction):
    If the entity is compatible, proceed to use the 'Interroga_Wikidata_SPARQL' tool to extract properties based on the Label:
    
    - If the Label is 'Case': retrieve P585 (event date) and P276 (location).
    - If the Label is 'Weapon': retrieve P279 (subclass) and P17/P176 (country/manufacturer).
    - If the Label is 'Location': retrieve P625 (coordinates) and P131 (administrative entity).
    
    ALWAYS use OPTIONAL clauses in your SPARQL queries.
    """,
    expected_output="""A valid and well-formed JSON block. 
    Example in case of success: {"wikidata_id": "Q123", "coordinates": "Point(12.49 41.89)"}
    Example in case of Semantic Shift or not found: {"trovato": false}""",
    agent=agente_ricercatore_lod
)