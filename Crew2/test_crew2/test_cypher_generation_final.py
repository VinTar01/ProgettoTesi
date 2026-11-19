import os
import json
import sys
import time
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Crew2.crew2_db import crew_neo4j_writer 
from crewai import LLM 

load_dotenv()

# -----------------------------------
# SETUP E CONFIGURAZIONE
# ------------------------------------
MODELLO = "gemini-flash-lite-latest"
CARTELLA_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
CARTELLA_JSON = os.path.join(CARTELLA_BASE, "Extraction_versions", "ReAct_Pydantic(Crew1)", "output_json")
CARTELLA_OUTPUT_FINAL = "grafici_output_final"

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

# Creazione cartella output in anticipo per salvare i file di testo
os.makedirs(CARTELLA_OUTPUT_FINAL, exist_ok=True)

# -----------------------------------------
# FUNZIONI DI ESECUZIONE
# ----------------------------------------

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
    """TEST B: Approccio Generativo Statico (Zero-Shot puro con Prompt Equo)"""
    start = time.time()
    
    prompt = f"""
    You are provided with the following JSON extracted from a news case:
    --------------------------------------------------
    {json.dumps(json_data, ensure_ascii=False, indent=2)}
    --------------------------------------------------

    Your task is to translate this JSON into a single executable Cypher query for Neo4j.
    RULES TO FOLLOW:
    1. ALWAYS use 'MERGE (n:Label {{id: "node_id"}})' for nodes, setting basic properties with 'SET n.name = "name"'.
    2. OPTIONAL PROPERTIES MANAGEMENT: Nodes (especially 'Person') in the JSON may contain the properties 'role', 'gender', 'age', and 'profession'. 
    If the JSON provides a valid text value (e.g., "age": "26"), add it to the SET clause. 
    If the JSON provides a null value, YOU MUST IGNORE that property and DO NOT include it in the Cypher query (DO NOT write SET n.age = "null").
    3. Create relationships using MERGE after matching the two nodes.
    
    Return EXCLUSIVELY the valid Cypher code. Do not add any explanations.
    """
    
    errori_sospetti = []
    successo = True
    
    try:
        risposta = llm_baseline.call([{"role": "user", "content": prompt}])
        query_generata = risposta.strip()
        
        if query_generata.startswith("```cypher"): query_generata = query_generata[9:]
        if query_generata.startswith("```"): query_generata = query_generata[3:]
        if query_generata.endswith("```"): query_generata = query_generata[:-3]
        
        with open(os.path.join(CARTELLA_OUTPUT_FINAL, "query_llm_puro.txt"), "a", encoding="utf-8") as log_file:
            log_file.write(f"\n--- NUOVO CASO LLM PURO (ZERO-SHOT) ---\n{query_generata}\n")
        
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
    return {"variante": "Zero-Shot Text-to-Cypher", "tempo_s": tempo, "successo": successo, "errori": errori_sospetti}

def esegui_variante_c_cot_cypher(json_data):
    """TEST C: Approccio Generativo con Chain-of-Thought (CoT)"""
    start = time.time()
    
    prompt = f"""
    You are provided with the following JSON extracted from a news case:
    --------------------------------------------------
    {json.dumps(json_data, ensure_ascii=False, indent=2)}
    --------------------------------------------------

    Your task is to translate this JSON into a single executable Cypher query for Neo4j.
    RULES TO FOLLOW:
    1. ALWAYS use 'MERGE (n:Label {{id: "node_id"}})' for nodes, setting basic properties with 'SET n.name = "name"'.
    2. OPTIONAL PROPERTIES MANAGEMENT: Nodes (especially 'Person') in the JSON may contain the properties 'role', 'gender', 'age', and 'profession'. 
    If the JSON provides a valid text value (e.g., "age": "26"), add it to the SET clause. If it provides null, IGNORE IT.
    3. Create relationships using MERGE after matching the two nodes.
    
    CRITICAL INSTRUCTION:
    BEFORE writing the Cypher code, perform step-by-step reasoning (Chain-of-Thought). List which nodes you need to create and which relationships connect them. 
    FINALLY, write EXCLUSIVELY the final query inside a ```cypher ... ``` block.
    """
    
    errori_sospetti = []
    successo = True
    
    try:
        risposta = llm_baseline.call([{"role": "user", "content": prompt}])
        testo_generato = risposta.strip()
        
        # Estrazione del solo codice Cypher dal blocco markdown generato dopo il ragionamento
        if "```cypher" in testo_generato:
            query_generata = testo_generato.split("```cypher")[1].split("```")[0].strip()
        else:
            query_generata = testo_generato # Fallback
            
        with open(os.path.join(CARTELLA_OUTPUT_FINAL, "query_llm_cot.txt"), "a", encoding="utf-8") as log_file:
            log_file.write(f"\n--- NUOVO CASO CoT (RAGIONAMENTO + QUERY) ---\n{testo_generato}\n")
        
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
            
    except Exception as e:
        errori_sospetti.append(f"Fallimento API: {str(e)}")
        successo = False
        
    tempo = time.time() - start
    return {"variante": "Chain-of-Thought Text-to-Cypher", "tempo_s": tempo, "successo": successo, "errori": errori_sospetti}

# --------------------------------------------
# GENERAZIONE GRAFICI COMPARATIVI (3 Varianti)
# -----------------------------------------
def genera_grafici_comparativi(risultati_totali):
    casi = [r["caso"].replace(".json", "").replace("_", " ").title() for r in risultati_totali]
    
    tempi_zero_shot = [r["zero_shot"]["tempo_s"] for r in risultati_totali]
    tempi_cot = [r["cot"]["tempo_s"] for r in risultati_totali]
    tempi_agent = [r["agent"]["tempo_s"] for r in risultati_totali]
    
    succ_zero = sum([1 for r in risultati_totali if r["zero_shot"]["successo"]])
    succ_cot = sum([1 for r in risultati_totali if r["cot"]["successo"]])
    succ_agent = sum([1 for r in risultati_totali if r["agent"]["successo"]])
    
    # 1. Grafico a Barre: Confronto Latenza (3 Barre)
    x = np.arange(len(casi))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(x - width, tempi_zero_shot, width, label='Zero-Shot', color='#DD8452')
    ax.bar(x, tempi_cot, width, label='Chain-of-Thought', color='#8C564B')
    ax.bar(x + width, tempi_agent, width, label='ReAct + Tools', color='#4C72B0')
    
    ax.set_ylabel('Tempo di Esecuzione (secondi)')
    ax.set_title('Confronto Latenza: Zero-Shot vs CoT vs Architettura Agentica')
    ax.set_xticks(x)
    ax.set_xticklabels(casi, rotation=15, ha='right')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(CARTELLA_OUTPUT_FINAL, 'latenza_test_3.png'), dpi=300)
    plt.close()
    
    # 2. Grafico a Torta: Execution Accuracy (3 Torte)
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    
    ax1.pie([succ_zero, 6 - succ_zero], labels=['Successo', 'Fallimento/Errori'], autopct='%1.1f%%', colors=['#55A868', '#C44E52'], startangle=90)
    ax1.set_title('Zero-Shot')
    
    ax2.pie([succ_cot, 6 - succ_cot], labels=['Successo', 'Fallimento/Errori'], autopct='%1.1f%%', colors=['#55A868', '#C44E52'], startangle=90)
    ax2.set_title('Chain-of-Thought')
    
    ax3.pie([succ_agent, 6 - succ_agent], labels=['Successo', 'Fallimento/Errori'], autopct='%1.1f%%', colors=['#55A868', '#C44E52'], startangle=90)
    ax3.set_title('ReAct + Tools')
    
    plt.tight_layout()
    plt.savefig(os.path.join(CARTELLA_OUTPUT_FINAL, 'accuracy_test_3.png'), dpi=300)
    plt.close()

# -------------------------------------------
# ORCHESTRAZIONE DEL TEST
# -------------------------------------------
if __name__ == "__main__":
    print("\n" + "="*50)
    print(" AVVIO TEST COMPARATIVO COMPLETO (3 VARIANTI) ")
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
            
        print("     1. Esecuzione Zero-Shot (Regole Base)...")
        res_zero_shot = esegui_variante_b_raw_cypher(dati)
        
        print("     2. Esecuzione Chain-of-Thought (Ragionamento)...")
        res_cot = esegui_variante_c_cot_cypher(dati)
        
        print("     3. Esecuzione Agente (ReAct + Tools)...")
        res_agent = esegui_variante_a_crew2(dati)
        
        risultati_totali.append({
            "caso": nome_file,
            "zero_shot": res_zero_shot,
            "cot": res_cot,
            "agent": res_agent
        })
        
        time.sleep(8) # Pausa per rate limit API
        
    genera_grafici_comparativi(risultati_totali)
    
    print("\n" + "="*50)
    print(f" TEST COMPLETATO. GRAFICI E LOG SALVATI IN '{CARTELLA_OUTPUT_FINAL}/' ")
    print("="*50)