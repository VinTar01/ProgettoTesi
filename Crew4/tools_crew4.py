import os
from crewai.tools import tool 
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

# Inizializzazione del driver
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"), 
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

@tool("Read_Only_Graph_Query")
def execute_read_only_cypher(query: str) -> str:
    """
    Executes a read-only Cypher query on the Neo4j database.
    
    WARNING: Pass the arguments as a JSON dictionary using EXCLUSIVELY the "query" key.
    Correct example: {"query": "MATCH (p:Person)-[:IS_VICTIM_OF]->(c:Case) RETURN p.name, c.name"}
    """
    
    # Salvo la query nei log per l'Ablation Study della tesi
    #with open("query_esplorative_agente.txt", "a", encoding="utf-8") as log_file:
        #log_file.write(f"\n--- AGENT GENERATED QUERY ---\n{query}\n")
        
    query_upper = query.upper()
    
    # Livello 1: Lexical Filter di Sicurezza (Read-Only)
    forbidden_keywords = ["CREATE", "MERGE", "SET", "DELETE", "DROP", "REMOVE", "DETACH"]
    if any(keyword in query_upper for keyword in forbidden_keywords):
        return (
            "SECURITY ERROR: Execution blocked. You attempted to alter the database. "
            "Use EXCLUSIVELY read-only clauses (MATCH, WHERE, WITH, RETURN, LIMIT, ORDER BY). "
            "Reformulate the query."
        )

    # Livello 2: Esecuzione con cattura degli errori (Innesco ReAct)
    try:
        with driver.session() as session:
            result = session.run(query)
            records = [record.data() for record in result]
            
            # Se la query è corretta ma troppo restrittiva
            if not records:
                return (
                    "0 results. INFO: The query is syntactically correct but no data was found. "
                    "Do NOT loop endlessly. Try loosening the constraints ONCE (e.g., remove WHERE clauses). "
                    "If still 0 results, STOP and answer the investigator that no matching data is present."
                )
                
            return str(records)
            
    except Exception as e:
        # Se c'è un errore sintattico (es. parentesi mancante, tipo errato)
        return (
            f"SYNTAX ERROR details: {e}. "
            "Analyze the error carefully. Check your relationship names and syntax. "
            "If you fail again, DO NOT retry. STOP and output: 'Unable to formulate a valid query'."
        )




#funzione statica
def get_database_schema_text() -> str:
    """Interroga Neo4j per costruire una rappresentazione testuale dello schema reale."""
    schema_info = []
    
    try:
        with driver.session() as session:
            # 1. Recupera Nodi e Proprietà
            nodes_res = session.run("CALL db.schema.nodeTypeProperties()")
            nodes_dict = {}
            for rec in nodes_res:
                # Pulisce i nomi delle label (es. ":`Person`" -> "Person")
                label = rec["nodeType"].replace(":`", "").replace("`", "")
                prop = rec["propertyName"]
                if prop:
                    nodes_dict.setdefault(label, []).append(prop)
            
            schema_info.append("--- NODE LABELS & PROPERTIES ---")
            for label, props in nodes_dict.items():
                schema_info.append(f"- {label}: {', '.join(props)}")
                
            # 2. Recupera i Tipi di Relazione
            rels_res = session.run("CALL db.relationshipTypes()")
            rels = [rec[0] for rec in rels_res]
            
            schema_info.append("\n--- RELATIONSHIP TYPES ---")
            schema_info.append(", ".join(rels))
            
        return "\n".join(schema_info)
    except Exception as e:
        return f"Schema retrieval error: {e}"