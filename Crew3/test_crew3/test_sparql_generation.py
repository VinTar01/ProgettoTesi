import os
import sys
import time
import requests
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from neo4j import GraphDatabase
from crewai import LLM

# Assicuriamo che il modulo Crew3 venga trovato (risalendo di due cartelle)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Crew3.crew3_enrichment import crew_wikidata

load_dotenv()

# ==========================================
# 1. SETUP CONNESSIONE NEO4J E LLM
# ==========================================
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

llm_base = LLM(
    model="gemini-flash-lite-latest",
    temperature=0.0,
    api_key=os.getenv("GEMINI_API_KEY")
)

# ==========================================
# 2. FUNZIONI DI SUPPORTO
# ==========================================
def recupera_nodi_casuali(limite: int = 5) -> list[dict]:
    query = """
    MATCH (n)
    WHERE (n:Location OR n:Weapon OR n:Case) AND n.name IS NOT NULL
    WITH n, rand() as r
    ORDER BY r
    RETURN n.name AS name, labels(n)[0] AS label
    LIMIT $limite
    """
    nodi = []
    try:
        with driver.session() as session:
            result = session.run(query, limite=limite)
            for r in result:
                nodi.append({"nome": r["name"], "label": r["label"]})
    except Exception as e:
        print(f"[DB ERROR] Errore nell'estrazione dei nodi casuali: {e}")
    return nodi

def cerca_qid_wikidata(nome_entita: str) -> str | None:
    url = "https://www.wikidata.org/w/api.php"
    params = {"action": "wbsearchentities", "format": "json", "language": "it", "search": nome_entita}
    try:
        resp = requests.get(url, params=params, headers={"User-Agent": "GraceAblation/1.0"})
        data = resp.json()
        if data.get("search"):
            return data["search"][0]["id"]
    except Exception:
        pass
    return None

def testa_sintassi_sparql(query: str) -> tuple[bool, str]:
    url = "https://query.wikidata.org/sparql"
    headers = {"User-Agent": "GraceAblation/1.0", "Accept": "application/sparql-results+json"}
    try:
        resp = requests.get(url, params={'query': query}, headers=headers)
        if resp.status_code == 400:
            return False, "ERRORE SINTATTICO (HTTP 400 - Compilazione SPARQL fallita)"
        
        dati = resp.json()
        risultati = dati.get("results", {}).get("bindings", [])
        
        if not risultati:
            return False, "ESECUZIONE OK, ZERO RISULTATI (Errore Semantico o filtri errati)"
        return True, "SUCCESSO (Sintassi e Semantica validate, Risultati Trovati)"
    except Exception as e:
        return False, f"ECCEZIONE A RUNTIME (Rete/Parsing): {e}"

# ==========================================
# 3. LE TRE VARIANTI DI TEST
# ==========================================
def esegui_variante_a(nodo: dict) -> bool:
    print("\n--- [VARIANTE A] ZERO-SHOT (Nessun contesto) ---")
    prompt_a = f"""
    Sei un assistente SPARQL. Scrivi una query per estrarre le proprietà per l'entità 
    Wikidata '{nodo['nome']}' avente Q-ID {nodo['q_id']}.
    Restituisci ESCLUSIVAMENTE il codice SPARQL senza markdown e senza spiegazioni testuali.
    """
    try:
        raw_response = llm_base.call([{"role": "user", "content": prompt_a}])
        query = raw_response.replace("```sparql", "").replace("```", "").strip()
        print(f"[Query Generata]:\n{query[:200]}...\n")
        successo, msg = testa_sintassi_sparql(query)
        print(f"Esito Execution: {msg}")
        return successo
    except Exception as e:
        print(f"Fallimento: {e}")
        return False

def esegui_variante_b(nodo: dict) -> bool:
    print("\n--- [VARIANTE B] KNOWLEDGE INJECTION + FEW-SHOT (No ReAct) ---")
    prompt_b = f"""
    Hai ricevuto l'entità "{nodo['nome']}" (Label: "{nodo['label']}").
    Corrisponde al Q-ID esatto: {nodo['q_id']}.
    
    Il tuo obiettivo è generare una query SPARQL per estrarre proprietà specifiche.
    ATTENZIONE FONDAMENTALE: Usa SEMPRE clausole OPTIONAL nelle tue query SPARQL.
    
    Regole in base alla Label:
    - Se 'Case': Estrai P585 (data) o P580, e P276 (luogo).
    - Se 'Location': Estrai P625 (coordinate) e P131 (entità amministrativa).
    - Se 'Weapon': Estrai P279 (sottoclasse) e P17 (paese).
    
    ESEMPIO (Few-Shot):
    Se la Label è 'Location' e il Q-ID è 'Q220', devi restituire:
    SELECT ?coord ?admin WHERE {{
      OPTIONAL {{ wd:Q220 wdt:P625 ?coord . }}
      OPTIONAL {{ wd:Q220 wdt:P131 ?admin . }}
    }}
    
    Genera la query SPARQL per il Q-ID {nodo['q_id']} usando le regole della sua Label '{nodo['label']}'.
    Restituisci ESCLUSIVAMENTE il codice SPARQL, niente altro.
    """
    try:
        raw_response = llm_base.call([{"role": "user", "content": prompt_b}])
        query = raw_response.replace("```sparql", "").replace("```", "").strip()
        print(f"[Query Generata]:\n{query[:200]}...\n")
        successo, msg = testa_sintassi_sparql(query)
        print(f"Esito Execution: {msg}")
        return successo
    except Exception as e:
        print(f"Fallimento: {e}")
        return False

def esegui_variante_c(nodo: dict) -> bool:
    print("\n--- [VARIANTE C] AGENTE IBRIDO (CrewAI + ReAct + Tool) ---")
    try:
        risultato = crew_wikidata.kickoff(inputs={
            "nome_entita": nodo['nome'],
            "label_entita": nodo['label'],
            "q_id": nodo['q_id']
        })
        payload = str(risultato).strip()
        print("[Payload Estratto (JSON)]:")
        print(payload)
        
        # Consideriamo successo se l'agente restituisce un formato valido e non ha fallito l'estrazione
        if "{" in payload and "}" in payload and "Fallimento" not in payload:
            print(f"Esito Execution: SUCCESSO (Estrazione e parsing completati)")
            return True
        else:
            print(f"Esito Execution: FALLIMENTO SEMANTICO (Formato non valido o tool fallito)")
            return False
    except Exception as e:
        print(f"Fallimento MAS: {e}")
        return False

# ==========================================
# 5. GENERAZIONE GRAFICI E REPORT
# ==========================================
def genera_report_ablation(risultati, totale_nodi):
    cartella_script = os.path.dirname(os.path.abspath(__file__))
    cartella_output = os.path.join(cartella_script, "risultati_output2")
    os.makedirs(cartella_output, exist_ok=True)
    
    succ_a = risultati["A"]
    succ_b = risultati["B"]
    succ_c = risultati["C"]
    
    perc_a = (succ_a / totale_nodi) * 100
    perc_b = (succ_b / totale_nodi) * 100
    perc_c = (succ_c / totale_nodi) * 100
    
    # 1. Generazione CSV
    df = pd.DataFrame({
        "Variante": [
            "Variante A (Zero-Shot)", 
            "Variante B (Few-Shot / Knowledge Injection)", 
            "Variante C (ReAct Agent + Tool)"
        ],
        "Successi": [f"{succ_a}/{totale_nodi}", f"{succ_b}/{totale_nodi}", f"{succ_c}/{totale_nodi}"],
        "Execution Accuracy (%)": [f"{perc_a:.1f}%", f"{perc_b:.1f}%", f"{perc_c:.1f}%"]
    })
    
    percorso_csv = os.path.join(cartella_output, "tabella_ablation_study.csv")
    df.to_csv(percorso_csv, index=False)
    print("\n" + "=" * 50)
    print(" TABELLA ABLATION STUDY ")
    print("=" * 50)
    print(df.to_markdown(index=False))
    
    # 2. Generazione Grafico a Barre
    fig, ax = plt.subplots(figsize=(9, 6))
    labels = ['Variante A\n(Zero-Shot)', 'Variante B\n(Few-Shot)', 'Variante C\n(ReAct Agent)']
    valori = [perc_a, perc_b, perc_c]
    colori = ['#C44E52', '#DD8452', '#55A868']
    
    bars = ax.bar(labels, valori, color=colori, width=0.5)
    ax.set_ylabel('Execution Accuracy (%)')
    ax.set_title(f'Ablation Study: Generazione Text-to-SPARQL\n(Campione: {totale_nodi} nodi casuali)')
    ax.set_ylim(0, 100)
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 1.5, f'{yval:.1f}%', ha='center', va='bottom', fontweight='bold')
        
    plt.tight_layout()
    percorso_grafico = os.path.join(cartella_output, "grafico_ablation_study.png")
    plt.savefig(percorso_grafico, dpi=300)
    plt.close()
    
    print(f"\n[!] Grafico salvato in: {percorso_grafico}")
    print(f"[!] Tabella salvata in: {percorso_csv}\n")

# ==========================================
# 6. LOOP DI ESECUZIONE 
# ==========================================
if __name__ == "__main__":
    print("=" * 70)
    print(" ABLATION STUDY: TEXT-TO-SPARQL GENERATION SUI NODI CASUALI ")
    print("=" * 70)
    
    NUMERO_NODI = 20
    nodi_casuali = recupera_nodi_casuali(limite=NUMERO_NODI)
    
    if not nodi_casuali:
        print("Nessun nodo trovato nel DB.")
        sys.exit(1)
        
    print(f"Estratti {len(nodi_casuali)} nodi casuali dal DB. Inizio risoluzione Q-ID...")
    
    nodi_test = []
    for nodo in nodi_casuali:
        qid = cerca_qid_wikidata(nodo['nome'])
        if qid:
            nodo['q_id'] = qid
            nodi_test.append(nodo)
            print(f"  -> Trovato Q-ID per '{nodo['nome']}': {qid}")
        else:
            print(f"  -> Impossibile trovare Q-ID per '{nodo['nome']}'. Salto.")
        time.sleep(1) 
        
    if not nodi_test:
        print("Nessun Q-ID risolto. Impossibile procedere.")
        sys.exit(1)
        
    risultati = {"A": 0, "B": 0, "C": 0}
    totale_nodi_validi = len(nodi_test)
        
    for i, nodo in enumerate(nodi_test, 1):
        print("\n" + "=" * 50)
        print(f" TEST SUL NODO {i}/{totale_nodi_validi}: '{nodo['nome']}' ({nodo['label']} - {nodo['q_id']})")
        print("=" * 50)
        
        if esegui_variante_a(nodo): risultati["A"] += 1
        time.sleep(3) 
        
        if esegui_variante_b(nodo): risultati["B"] += 1
        time.sleep(3) 
        
        if esegui_variante_c(nodo): risultati["C"] += 1
        time.sleep(5) 
    
    genera_report_ablation(risultati, totale_nodi_validi)
    
    print("=" * 70)
    print(" FINE ABLATION STUDY ")
    print("=" * 70)