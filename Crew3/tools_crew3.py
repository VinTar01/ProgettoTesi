import requests
import re
from crewai.tools import tool

# ----------------------------------------
# TOOL: INTERFACCIA ENDPOINT SPARQL
# ----------------------------------------
# Questo strumento incapsula la comunicazione HTTP con il cloud Wikidata.

@tool("Interroga_Wikidata_SPARQL")
def interroga_wikidata_sparql(query: str) -> str:
    """
    Esegue una query SPARQL sull'endpoint pubblico di Wikidata.
    
    ATTENZIONE: L'invocazione di questo tool richiede un dizionario JSON valido, 
    utilizzando esclusivamente la chiave "query". 
    Esempio di sintassi accettata: {"query": "SELECT ?prop WHERE { ... }"}
    """
    url = "https://query.wikidata.org/sparql"
    
    # Intestazioni obbligatorie per l'identificazione e la negoziazione del formato
    headers = {
        "User-Agent": "GraceMultiAgent/1.0 (Python/Requests)",
        "Accept": "application/sparql-results+json"
    }
    try:
        response = requests.get(url, params={'query': query}, headers=headers)
        response.raise_for_status()
        dati = response.json()
        
        # Filtraggio del payload per l'estrazione esclusiva dei dati relazionali
        risultati_puliti = dati.get("results", {}).get("bindings", [])
        return str(risultati_puliti)
        
    except Exception as e:
        # Il passaggio dell'eccezione come stringa innesca il meccanismo di 
        # auto-riflessione dell'agente (ReAct), consentendo correzioni dinamiche della query.
        return f"Fallimento esecuzione SPARQL. Dettaglio eccezione: {e}"


#-------------------

@tool("Ispeziona_Wikidata_QID")
def ispeziona_qid(q_id: str) -> str:
    """
    Restituisce etichetta, descrizione e classi di appartenenza (instance of, P31)
    di un Q-ID di Wikidata. Da usare PRIMA di estrarre qualsiasi proprietà,
    per verificare che l'entità sia coerente con il nodo locale.
    Sintassi accettata: {"q_id": "Q12345"}
    """
    if not re.fullmatch(r"Q\d+", q_id.strip()):
        return "Q-ID non valido."
    q_id = q_id.strip()
    query = f"""
    SELECT ?itemLabel ?itemDescription ?classeLabel WHERE {{
      BIND(wd:{q_id} AS ?item)
      OPTIONAL {{ ?item wdt:P31 ?classe . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "it,en". }}
    }}
    """
    try:
        r = requests.get(
            "https://query.wikidata.org/sparql",
            params={"query": query},
            headers={"User-Agent": "GraceMultiAgent/1.0 (Python/Requests)",
                     "Accept": "application/sparql-results+json"},
            timeout=30,
        )
        r.raise_for_status()
        return str(r.json().get("results", {}).get("bindings", []))
    except Exception as e:
        return f"Fallimento ispezione Q-ID: {e}"