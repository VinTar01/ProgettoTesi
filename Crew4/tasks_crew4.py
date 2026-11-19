from crewai import Task
from Crew4.agents_crew4 import agente_esploratore


task_risposta_domanda = Task(
    description=(
        "The investigator asked you the following question: '{domanda_utente}'\n\n"
        "Here is the DYNAMIC SCHEMA of the graph database currently active:\n"
        "--------------------------------------------------\n"
        "{schema_grafo}\n"
        "--------------------------------------------------\n\n"
        "Your task follows a rigorous logical process:\n"
        "1. Translate the question into a valid Cypher query.\n"
        "   - CYPHER RULE 1 (People & Roles): For generic questions about people involved, use the full pattern: MATCH (p:Person)-[:IS_SUSPECTED_IN|COMMITTED|INVOLVED_IN|IS_VICTIM_OF]-(c:Case). HOWEVER, if the user explicitly asks for a specific role like 'vittima' (victim), YOU MUST strictly use ONLY the [:IS_VICTIM_OF] relationship to avoid extracting suspects or witnesses.\n"
        "   - CYPHER RULE 2 (Locations): To find where an event occurred, FIRST try to traverse the relationship: MATCH (c:Case)-[:OCCURRED_AT]-(l:Location). IF AND ONLY IF this returns 0 results, fallback to checking the `location_label` or `locationLabel` properties directly inside the Case node.\n"
        "   - CYPHER RULE 3 (Aggregations): If asked for items in 'more than one distinct case', use `WITH w, count(DISTINCT c) AS case_count WHERE case_count > 1`.\n"
        "   - CYPHER RULE 4 (Direction): ALWAYS use directionless relationships `-[:REL_NAME]-` with the exact relationship type in brackets.\n"
        "   - CYPHER RULE 5 (Matching): ALWAYS use case-insensitive matching: `WHERE toLower(n.name) CONTAINS 'keyword'`.\n"
        "2. Execute the query using the 'Read_Only_Graph_Query' tool.\n"
        "3. If you get 0 results, check if you missed a relationship type or used a wrong property name. Broaden the MATCH clause and retry (MAX 2 TIMES).\n"
        "4. CRITICAL FORMAT RULE: Your FINAL output MUST be a conversational answer in natural Italian. YOU ARE STRICTLY FORBIDDEN from outputting internal system logs like 'Thought:', 'Action:', or JSON formats.\n\n"
        "IMPORTANT: At the end of your final Italian answer, you MUST append the final Cypher query used, enclosed in a ```cypher``` markdown code block."
    ),
    max_retries=3,
    expected_output="A clear, exhaustive conversational text answer in Italian detailing ALL retrieved results, ending with the ```cypher``` code block.",
    agent=agente_esploratore
)