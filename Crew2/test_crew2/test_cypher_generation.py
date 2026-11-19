import os
import json
import sys
import time
import pandas as pd
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Crew2.crew2_db import crew_neo4j_writer 
from crewai import LLM 

load_dotenv()

# ==========================================
# SETUP E CONFIGURAZIONE
# ==========================================
MODELLO = "gemini-flash-lite-latest"
CARTELLA_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
CARTELLA_JSON = os.path.join(CARTELLA_BASE, "Extraction_versions", "ReAct_Pydantic(Crew1)", "output_json")

CASI_DATASET = [
    "delitto_di_cogne.json",
    "delitto_di_novi_ligure.json",
    "omicidio_di_alberto_brasili.json",
    "omicidio_di_giulia_cecchettin.json",
    "omicidio_di_marco_vannini.json",
    "omicidio_di_marta_russo.json"
]

llm_baseline = LLM(
    model=MODELLO, 
    temperature=0.1, 
    api_key=os.getenv("GEMINI_API_KEY")
)

# ==========================================
# FUNZIONI DI ESECUZIONE
# ==========================================
def esegui_variante_a_crew2(json_data):
    """TEST A: Approccio Multi-Agente (ReAct + Tool Python + Esecuzione reale DB)"""
    start = time.time()
    json_string = json.dumps(json_data, ensure_ascii=False, indent=2) 
    
    esito = True
    errori = []
    try:
        crew_neo4j_writer.kickoff(inputs={'json_da_inserire': json_string}) 
    except Exception as e:
        esito = False
        errori.append(f"Fallimento architettura multi-agente: {str(e)}")
    
    tempo = time.time() - start
    return {"variante": "ReAct + Python Tools", "tempo_s": tempo, "successo": esito, "errori": errori}

def esegui_variante_b_raw_cypher(json_data):
    """TEST B: Approccio Generativo Statico (Stesse regole, no ReAct, no Tool DB)"""
    start = time.time()
    
    # PROMPT ARRICCHITO: Stesse identiche istruzioni fornite all'agente
    prompt = f"""
    Hai a disposizione il seguente JSON estratto da un caso di cronaca:
    --------------------------------------------------
    {json.dumps(json_data, ensure_ascii=False, indent=2)}
    --------------------------------------------------

    Il tuo compito è tradurre questo JSON in un'unica query Cypher eseguibile per Neo4j.
    REGOLE DA RISPETTARE:
    1. Usa SEMPRE 'MERGE (n:Label {{id: "id_nodo"}})' per i nodi, impostando le proprietà di base con 'SET n.name = "nome"'.
    2. GESTIONE DELLE PROPRIETÀ OPZIONALI: I nodi (in particolare 'Person') nel JSON possono contenere le proprietà 'role', 'gender', 'age' e 'profession'. 
    Se il JSON riporta un valore testuale valido (es. "age": "26"), aggiungilo alla clausola SET. 
    Se il JSON riporta il valore null, DEVI IGNORARE quella proprietà e NON inserirla nella query Cypher (NON scrivere SET n.age = "null").
    3. Crea le relazioni usando MERGE dopo aver fatto il MATCH dei due nodi.
    
    Restituisci ESCLUSIVAMENTE il codice Cypher valido. Non aggiungere spiegazioni.
    """
    
    errori_sospetti = []
    successo = True
    
    try:
        risposta = llm_baseline.call([{"role": "user", "content": prompt}])
        query_generata = risposta.strip()
        
        if query_generata.startswith("```cypher"): query_generata = query_generata[9:]
        if query_generata.startswith("```"): query_generata = query_generata[3:]
        if query_generata.endswith("```"): query_generata = query_generata[:-3]
        
        with open("query_llm_puro3.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"\n--- NUOVO CASO LLM PURO (PROMPT EQUO) ---\n{query_generata}\n")
        
        query_upper = query_generata.upper()
        if "MERGE" not in query_upper:
            errori_sospetti.append("Omissione MERGE")
            successo = False
        if query_generata.count("(") != query_generata.count(")"):
            errori_sospetti.append("Sbilanciamento Parentesi (AST)")
            successo = False
        if "'" in query_generata and '"' in query_generata and "\\'" not in query_generata:
            errori_sospetti.append("Conflitto Escaping")
            successo = False
        if "CREATE" in query_upper and "MERGE" not in query_upper:
            errori_sospetti.append("Uso di CREATE invece di MERGE")
            successo = False
            
    except Exception as e:
        errori_sospetti.append(f"Fallimento API: {str(e)}")
        successo = False
        
    tempo = time.time() - start
    return {"variante": "Static Text-to-Cypher (Prompt Equo)", "tempo_s": tempo, "successo": successo, "errori": errori_sospetti}

# ==========================================
# GENERAZIONE GRAFICI
# ==========================================
def genera_grafici_comparativi(risultati_totali):
    os.makedirs("grafici_output2", exist_ok=True)
    
    casi = [r["caso"].replace(".json", "").replace("_", " ").title() for r in risultati_totali]
    tempi_zero_shot = [r["zero_shot"]["tempo_s"] for r in risultati_totali]
    tempi_agent = [r["agent"]["tempo_s"] for r in risultati_totali]
    
    succ_zero_shot = sum([1 for r in risultati_totali if r["zero_shot"]["successo"]])
    succ_agent = sum([1 for r in risultati_totali if r["agent"]["successo"]])
    
    # Grafico 1: Latenza
    x = range(len(casi))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar([i - width/2 for i in x], tempi_zero_shot, width, label='Zero-Shot (LLM Puro)', color='#DD8452')
    ax.bar([i + width/2 for i in x], tempi_agent, width, label='ReAct + Python Tools', color='#4C72B0')
    
    ax.set_ylabel('Tempo di Esecuzione (secondi)')
    ax.set_title('Confronto Latenza per Caso: Zero-Shot vs Architettura Agentica')
    ax.set_xticks(x)
    ax.set_xticklabels(casi, rotation=15, ha='right')
    ax.legend()
    plt.tight_layout()
    plt.savefig('grafici_output2/latenza_test2.png', dpi=300)
    plt.close()
    
    # Grafico 2: Execution Accuracy
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    ax1.pie([succ_zero_shot, 6 - succ_zero_shot], labels=['Successo', 'Fallimento/Errori'], autopct='%1.1f%%', colors=['#55A868', '#C44E52'], startangle=90)
    ax1.set_title('Execution Accuracy: Zero-Shot')
    
    ax2.pie([succ_agent, 6 - succ_agent], labels=['Successo', 'Fallimento/Errori'], autopct='%1.1f%%', colors=['#55A868', '#C44E52'], startangle=90)
    ax2.set_title('Execution Accuracy: ReAct + Tools')
    
    plt.tight_layout()
    plt.savefig('grafici_output2/accuracy_test2.png', dpi=300)
    plt.close()

# ==========================================
# ORCHESTRAZIONE DEL TEST
# ==========================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print(" AVVIO TEST COMPARATIVO: TEXT-TO-CYPHER (AGENTE 2) ")
    print("="*50)
    
    risultati_totali = []
    
    for nome_file in CASI_DATASET:
        percorso = os.path.join(CARTELLA_JSON, nome_file)
        if not os.path.exists(percorso):
            print(f"[WARN] File non trovato, salto: {nome_file}")
            continue
            
        print(f"\n---> Analisi del caso: {nome_file}")
        with open(percorso, 'r', encoding='utf-8') as f:
            dati = json.load(f)
            
        print("     Esecuzione LLM Zero-Shot in corso...")
        res_zero_shot = esegui_variante_b_raw_cypher(dati)
        
        print("     Esecuzione Agente (ReAct + Tools) in corso...")
        res_agent = esegui_variante_a_crew2(dati)
        
        risultati_totali.append({
            "caso": nome_file,
            "zero_shot": res_zero_shot,
            "agent": res_agent
        })
        
        time.sleep(8) 
        
    genera_grafici_comparativi(risultati_totali)
    
    print("\n" + "="*50)
    print(" TEST COMPLETATO. GRAFICI SALVATI IN 'grafici_output2/' ")
    print("="*50)