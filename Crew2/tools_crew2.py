import os
from crewai.tools import tool 
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# INIZIALIZZAZIONE DRIVER DATABASE
# ==========================================
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"), 
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

# ==========================================
# TOOL 1: ESECUZIONE CYPHER CON CONTROLLO
# ==========================================
# In alternativa a tool generici nativi, questo tool
# personalizzato funge da Lexical Filter.
# Ispeziona la stringa generata dall'agente prima dell'invio al database,
# intercettando e neutralizzando tentativi di esecuzione di comandi DML distruttivi 
# (DELETE, DROP, DETACH). Se rilevati, solleva un'eccezione morbida che costringe 
# l'agente (grazie al loop ReAct) a riformulare la query in modo costruttivo.

@tool("Esegui_Query_Cypher")
def execute_cypher_tool(query: str) -> str:
    """
    Executes a Cypher query on the Neo4j database.
    Use this tool ONLY to insert new nodes and relationships (CREATE/MERGE).
    
    WARNING: You must call this tool by passing the arguments as a valid JSON dictionary,
    using EXCLUSIVELY the "query" key.
    Correct example: {"query": "MERGE (p:Person {id: 'person_mario'}) RETURN p"}
    """

    # Salva la query dell'agente in un file di testo per ispezione
    with open(f"query_agente_react.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"\n--- CASO AGENTE ---\n{query}\n")
    query_upper = query.upper()
    
    # Livello 1: Lexical Filtering di Sicurezza
    if "DELETE" in query_upper or "DROP" in query_upper:
        return "SECURITY ERROR: Execution blocked by the system. Destructive queries are not allowed in this domain. Reformulate using MERGE."

    # Livello 2: Esecuzione Transazionale
    try:
        with driver.session() as session:
            session.run(query)
            return "SUCCESS: Cypher transaction executed and persisted on the database."
    except Exception as e:
        # Il ritorno dell'eccezione come stringa alimenta l'Observation dell'agente
        # abilitando la capacità di self-correction a runtime.
        return f"EXCEPTION: Cypher execution failed. Error details: {e}"