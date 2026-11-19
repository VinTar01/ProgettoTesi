import os
import sys
import json
import time
import re
import pandas as pd
from dotenv import load_dotenv



#CHIAMA LA CREW SULLE QUERY OTTIMALI DEFINITE E CREA I REPORT CON LE INFO PER IL CONFRONTO


# ==========================================
# 1. FIX IMPORT PATH
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
crew4_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(crew4_dir)
sys.path.append(root_dir)

# ==========================================
# 2. IMPORT CREW4
# ==========================================
from Crew4.tools_crew4 import get_database_schema_text
from Crew4.crew4_qa import crew_esploratore_grafo

load_dotenv()

CSV_OUT = os.path.join(current_dir, "report_valutazione_crew4_llm_pydantic2.csv")
LOG_OUT = os.path.join(current_dir, "log_confronto_query_afterClean_llm_pydantic2.txt")


def estrai_cypher(testo: str) -> str:
    match = re.search(r"```(?:cypher)?\n?(.*?)```", testo, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return "Cypher non esplicitato (o formattato diversamente) nella risposta."

def valuta_risposta(risposta_agente: str, attesi: list) -> bool:
    risposta_lower = str(risposta_agente).lower()
    negazioni = [
        "non è stato possibile", "non risulta", "nessun record", 
        "non sono stati", "non è stato trovato", "non ci sono", "0 risultati", 
        "non ha restituito", "nessuna registrazione", "non esistono",
        "zero risultati", "nessun percorso", "isolati", "nessun risultato"
    ]
    is_negative = any(neg in risposta_lower for neg in negazioni)
    
    if not attesi:
        return is_negative
    if is_negative:
        return False
        
    for atteso in attesi:
        if isinstance(atteso, dict):
            for val in atteso.values():
                if str(val).lower() not in risposta_lower:
                    return False
        elif isinstance(atteso, str):
            if atteso.lower() not in risposta_lower:
                return False
    return True

def esegui_elaborazione_item(item, current_schema, max_retries=3):
    domanda = item["domanda_naturale"]
    atteso = item["risultato_atteso"]
    
    start_time = time.time()
    risposta_str = ""
    cypher_generato = "N/A"
    is_corretto = False
    esito = "ERRORE"

    for tentativo in range(max_retries):
        try:
            risultato = crew_esploratore_grafo.kickoff(inputs={
                "domanda_utente": domanda, 
                "schema_grafo": current_schema
            })
            risposta_str = str(risultato).strip()
            is_corretto = valuta_risposta(risposta_str, atteso)
            cypher_generato = estrai_cypher(risposta_str)
            
            esito = "SUPERATO" if is_corretto else "FALLITO"
            break

        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                print(f" -> [RATE LIMIT 429] Attesa di 65 secondi (Tentativo {tentativo + 2}/{max_retries})...")
                time.sleep(65)
            else:
                risposta_str = f"ERRORE RUNTIME: {e}"
                break
                
    elapsed = round(time.time() - start_time, 2)
    return esito, is_corretto, cypher_generato, risposta_str, elapsed

def log_risultato(f_log, item, esito, cypher_generato, risposta_str, elapsed):
    f_log.write(f"[{item['id']}] Livello: {item['livello']}\n")
    f_log.write(f"DOMANDA NATURALE: {item['domanda_naturale']}\n")
    f_log.write("-" * 80 + "\n")
    f_log.write(f"CYPHER GOLDEN (Ottimale):\n{item['cypher_ottimale']}\n\n")
    f_log.write(f"RISULTATO ATTESO: {item['risultato_atteso']}\n")
    f_log.write("-" * 80 + "\n")
    f_log.write(f"CYPHER GENERATO DALL'AGENTE:\n{cypher_generato}\n\n")
    f_log.write(f"RISPOSTA AGENTE:\n{risposta_str}\n")
    f_log.write("-" * 80 + "\n")
    f_log.write(f"ESITO: {esito} (Tempo: {elapsed}s)\n")
    f_log.write("=" * 80 + "\n\n")

def aggiorna_csv(nuovo_dato: dict):
    """Aggiorna la singola riga nel CSV o la aggiunge se non esiste."""
    if os.path.exists(CSV_OUT):
        df = pd.read_csv(CSV_OUT)
        # Se l'ID esiste già, lo aggiorna
        if nuovo_dato['ID_Query'] in df['ID_Query'].values:
            idx = df.index[df['ID_Query'] == nuovo_dato['ID_Query']][0]
            for key, value in nuovo_dato.items():
                df.at[idx, key] = value
            print(f" -> File CSV: Riga {nuovo_dato['ID_Query']} AGGIORNATA.")
        else:
            # Se l'ID non esiste, lo aggiunge
            df = pd.concat([df, pd.DataFrame([nuovo_dato])], ignore_index=True)
            print(f" -> File CSV: Riga {nuovo_dato['ID_Query']} AGGIUNTA.")
    else:
        # Se il file non esiste, lo crea
        df = pd.DataFrame([nuovo_dato])
        print(f" -> File CSV: Creato nuovo file con {nuovo_dato['ID_Query']}.")
    
    df.to_csv(CSV_OUT, index=False)

def esegui_benchmark(target_id=None):
    print("\nEstrazione schema dinamico da Neo4j in corso...")
    current_schema = get_database_schema_text()

    dataset_path = os.path.join(current_dir, "golden_dataset_crew4_extra_llm_version.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # MODALITA' COMPLETA
    if not target_id:
        print("=" * 80 + "\n AVVIO BENCHMARK COMPLETO \n" + "=" * 80)
        report = []
        successi = 0
        
        with open(LOG_OUT, "w", encoding="utf-8") as f_log:
            f_log.write("=" * 80 + "\n LOG CONFRONTO CYPHER E RISPOSTE - CREW 4\n" + "=" * 80 + "\n\n")

        for idx, item in enumerate(dataset, 1):
            print(f"\n[{idx}/{len(dataset)}] Elaborazione {item['id']} ({item['livello']})...")
            esito, is_corretto, cypher_generato, risposta_str, elapsed = esegui_elaborazione_item(item, current_schema)
            if is_corretto: successi += 1
                
            with open(LOG_OUT, "a", encoding="utf-8") as f_log:
                log_risultato(f_log, item, esito, cypher_generato, risposta_str, elapsed)

            report.append({
                "ID_Query": item["id"], "Difficolta": item["livello"], "Esito_Superato": is_corretto,
                "Tempo_Esecuzione_s": elapsed, "Domanda": item["domanda_naturale"],
                "Cypher_Ottimale": item["cypher_ottimale"], "Cypher_Generato": cypher_generato,
                "Risultato_Atteso": str(item["risultato_atteso"]), "Risposta_Agente": risposta_str
            })
            print(f" -> Esito: [{esito}] in {elapsed}s")
            if idx < len(dataset):
                print(" -> Attesa 60s...")
                time.sleep(60)

        pd.DataFrame(report).to_csv(CSV_OUT, index=False)
        print(f"\nBenchmark completato! Accuracy: {(successi/len(dataset))*100:.1f}%")

    # MODALITA' SINGOLA
    else:
        print("=" * 80 + f"\n AVVIO TEST SINGOLO: {target_id} \n" + "=" * 80)
        item = next((i for i in dataset if i["id"] == target_id), None)
        if not item:
            print(f"[ERRORE] ID '{target_id}' non trovato nel dataset JSON.")
            return
            
        esito, is_corretto, cypher_generato, risposta_str, elapsed = esegui_elaborazione_item(item, current_schema)
        
        print(f"\nCYPHER GENERATO:\n{cypher_generato}\nESITO: {esito} in {elapsed}s")
        
        # Aggiorna il test log (in append)
        with open(LOG_OUT, "a", encoding="utf-8") as f_log:
            f_log.write(f"--- RE-RUN SINGOLO: {target_id} ---\n")
            log_risultato(f_log, item, esito, cypher_generato, risposta_str, elapsed)
        print(f" -> File di log testuale aggiornato (append).")

        # Aggiorna il CSV
        nuovo_dato = {
            "ID_Query": item["id"], "Difficolta": item["livello"], "Esito_Superato": is_corretto,
            "Tempo_Esecuzione_s": elapsed, "Domanda": item["domanda_naturale"],
            "Cypher_Ottimale": item["cypher_ottimale"], "Cypher_Generato": cypher_generato,
            "Risultato_Atteso": str(item["risultato_atteso"]), "Risposta_Agente": risposta_str
        }
        aggiorna_csv(nuovo_dato)


if __name__ == "__main__":
    # -------------------------------------------------------------
    # Se TARGET_QUERY_ID è None allora esegue tutte le query nel dataset
    # Se c'è l'ID, esegue solo quella singolarmente
    # -------------------------------------------------------------
    TARGET_QUERY_ID = "None"
    
    esegui_benchmark(target_id=TARGET_QUERY_ID)