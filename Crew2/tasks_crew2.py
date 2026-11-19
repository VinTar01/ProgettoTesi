from crewai import Task
from Crew2.agents_crew2 import agente_dba

task_ingestion_db = Task(
    description=(
        "You are provided with the following JSON extracted from a news report:\n"
        "--------------------------------------------------\n"
        "{json_da_inserire}\n"
        "--------------------------------------------------\n\n"
        
        "Your task is to write and execute Cypher queries to populate the Neo4j database. "
        "RULES TO FOLLOW:\n"
        "1. MERGE STRATEGY (CRITICAL FOR DEDUPLICATION):\n"
        "   - For 'Case' and 'Person' nodes: ALWAYS use the id provided in the JSON as the key. Example: MERGE (n:Person {id: 'id_from_json'}) SET n.name = 'Name'.\n"
        "   - For 'Case', 'Weapon', 'Location', 'Motive', 'Evidence' and 'Charge' (shared entities): IGNORE the JSON id. Use the exact name converted to lowercase as the MERGE key on the 'id' property. Example (if the name is 'Pistol'): MERGE (w:Weapon {id: 'pistol'}) SET w.name = 'Pistol'. This ensures that weapons and locations converge into global unique nodes.\n"
        "2. OPTIONAL PROPERTIES MANAGEMENT: Nodes (especially 'Person') in the JSON may contain the properties 'role', 'gender', 'age', and 'profession'. "
        "If the JSON provides a valid text value (e.g., \"age\": \"26\"), add it to the SET clause. If the JSON provides a null value, IGNORE the property and DO NOT include it in Cypher.\n"
        "3. Create relationships using MERGE ONLY AFTER performing a MATCH of the two previously created nodes.\n"
        "4. Use the 'Esegui_Query_Cypher' tool to inject the data. Combine the MERGE statements into a single transaction to save time and tokens.\n"
        "5. If you notice anomalies or obvious possible duplicates that differ only by case (uppercase/lowercase), use the 'Deduplica_Entita_APOC' tool."
    ),
    expected_output="A message confirming the successful insertion into the database via the tool and the generated query",
    agent=agente_dba
)