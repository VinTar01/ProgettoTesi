import os
import json
import re
from rouge_score import rouge_scorer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


#metriche di similarità strutturale tra query generate LLM-Few SHot e Agente vs ottimali

##metriche di similarità strutturale tra query generate LLM-Few SHot e Agente vs UNWIND

# -----------------------------------------
# 1. SETUP E CONFIGURAZIONE PERCORSI E TEST
# -----------------------------------------
# SELETTORE MODALITÀ DI TEST:
# True  = Sostituisce i valori con placeholder  Test di Struttura/Topologia
# False = Mantiene i valori testuali crudi  Test End-to-End
USA_NORMALIZZAZIONE_PLACEHOLDER = False

CARTELLA_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
CARTELLA_JSON = os.path.join(CARTELLA_BASE, "Crew2", "casi_inseriti_db_react_pydantic")
CARTELLA_OUTPUT = os.path.join(CARTELLA_BASE, "Crew2", "test_rouge")

# Crea la cartella test_rouge se non esiste
os.makedirs(CARTELLA_OUTPUT, exist_ok=True)

FILE_REACT = os.path.join(CARTELLA_BASE, "Crew2", "test_crew2", "grafici_output_final", "query_agente_react.txt")
FILE_LLM = os.path.join(CARTELLA_BASE, "Crew2", "test_crew2", "grafici_output_final", "query_llm_puro.txt")

CASI_DATASET = [
    "delitto_di_cogne.json",
    "delitto_di_novi_ligure.json",
    "omicidio_di_alberto_brasili.json",
    "omicidio_di_giulia_cecchettin.json",
    "omicidio_di_marco_vannini.json",
    "omicidio_di_marta_russo.json"
]

def estrai_query_da_log(percorso_file):
    query_map = {}
    if not os.path.exists(percorso_file):
        print(f"[ERRORE CRITICO] File di log non trovato sul disco: {percorso_file}")
        return query_map
        
    with open(percorso_file, 'r', encoding='utf-8') as f:
        contenuto = f.read()
        
    # Divisione in base ai separatori dei log
    blocchi = re.split(r'--- CASO AGENTE ---|--- NUOVO CASO LLM PURO \(ZERO-SHOT\) ---', contenuto)
    
    for blocco in blocchi:
        blocco = blocco.strip()
        if not blocco: 
            continue
            
        blocco_lower = blocco.lower()
        
        # Associa il blocco al file JSON corretto gestendo anche le varianti di nome
        for nome_file in CASI_DATASET:
            chiave_base = nome_file.replace(".json", "") # es. omicidio_di_marco_vannini
            
            # Crea anche una chiave alternativa rimuovendo "_di_" per sicurezza
            chiave_alternativa = chiave_base.replace("_di_", "_") # es. omicidio_marco_vannini
            
            if chiave_base in blocco_lower or chiave_alternativa in blocco_lower:
                query_map[nome_file] = blocco
                break
                
    print(f"[INFO] Lette {len(query_map)} query valide su {len(CASI_DATASET)} dal file: {os.path.basename(percorso_file)}")
    return query_map

def genera_golden_monolitica_da_json(percorso_json):
    """
    Legge il JSON estratto e genera la query Cypher perfetta (Ground Truth).
    Questo file serve come standard per dimostrare le mancanze degli approcci generativi.
    """
    # Lettura e Parsing Strutturale: carica il JSON come dizionario Python
    with open(percorso_json, 'r', encoding='utf-8') as f:
        dati = json.load(f)
        
    query_parts = ["// --- NODI ---"]
    
    # --------------------------------------
    # FASE 1: Generazione Dinamica dei Nodi
    # --------------------------------------
    for e in dati.get("entities", []):
        label = e.get("label", "Entity")
        e_id = e.get("id", "")
        
        # Inizializza l'istruzione di base formattando id e label (es. MERGE (n_person_x:Person {id: "person_x"}))
        nodo_str = f'MERGE (n_{e_id}:{label} {{id: "{e_id}"}})'
        
        props = []
        # Scansiona le restanti chiavi dell'entità per formattare dinamicamente il blocco SET
        for key, value in e.items():
            if key not in ["id", "label"] and value is not None:
                # Riconoscimento automatico dei tipi di dato:
                # Evita gli apici per i booleani, applica i doppi apici (con escape) alle stringhe
                if isinstance(value, bool):
                    val_str = str(value).lower()
                else:
                    val_pulito = str(value).replace('"', '\\"')
                    val_str = f'"{val_pulito}"'
                
                props.append(f'n_{e_id}.{key} = {val_str}')
                
        # Se ci sono proprietà, aggiunge la clausola SET al MERGE del nodo
        if props:
            nodo_str += "\nSET " + ", ".join(props)
            
        query_parts.append(nodo_str)
        
    query_parts.append("\n// --- RELAZIONI ---")
    
    # ==========================================
    # FASE 2: Generazione Dinamica delle Relazioni
    # ==========================================
    for rel in dati.get("relationships", []):
        src_id = rel.get("source_id")
        tgt_id = rel.get("target_id")
        rel_type = rel.get("type")
        
        # Costrutto a due fasi: prima un MATCH per recuperare i due nodi tramite ID,
        # seguito da un MERGE direzionale per creare l'arco semantico
        rel_str = f'MATCH (s {{id: "{src_id}"}}), (t {{id: "{tgt_id}"}})\nMERGE (s)-[:{rel_type}]->(t)'
        query_parts.append(rel_str)
        
    return "\n".join(query_parts)

def elabora_testo_query(testo_query):
    if not testo_query: return ""
    # Pulizia di base (rimuove markdown, commenti e WITH *)
    q = re.sub(r'//.*', '', testo_query).replace("```cypher", "").replace("```", "").replace("WITH *", "")
    
    if USA_NORMALIZZAZIONE_PLACEHOLDER:
        # Sostituisce stringhe e variabili con placeholder
        q = re.sub(r"'(?:\\.|[^'\\])*'", "<STR>", q)
        q = re.sub(r'"(?:\\.|[^"\\])*"', "<STR>", q)
        q = re.sub(r'\b(true|false)\b', "<BOOL>", q, flags=re.IGNORECASE)
        q = re.sub(r'\b\d+\b', "<NUM>", q)
        q = re.sub(r'\b[a-zA-Z0-9_]+(:[A-Z][a-zA-Z0-9_]+)', r'<VAR>\1', q)
        q = re.sub(r'\b[a-zA-Z0-9_]+(\.[a-z_]+)', r'<VAR>\1', q)
    
    # Spaziatura uniforme
    q = re.sub(r'\s*(MERGE|MATCH|SET|CREATE)\b', r'\n\1', q)
    q = re.sub(r'[ \t]+', ' ', q).lower().strip()
    return q

def calcola_metriche(query_generata, query_golden):
    if not query_generata or not query_golden:
        return {"cosine": 0.0, "rougeL": 0.0}
    norm_gen = elabora_testo_query(query_generata)
    norm_gold = elabora_testo_query(query_golden)
    
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([norm_gen, norm_gold])
        cos_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except ValueError:
        cos_sim = 0.0

    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = scorer.score(norm_gold, norm_gen)
    return {"cosine": cos_sim, "rougeL": scores['rougeL'].fmeasure}

if __name__ == "__main__":
    map_react = estrai_query_da_log(FILE_REACT)
    map_llm = estrai_query_da_log(FILE_LLM)
    risultati = []
    
    # Suffisso file per distinguere i due report
    tipo_report = "NORMALIZZATO" if USA_NORMALIZZAZIONE_PLACEHOLDER else "CRUDO"

    for nome_file in CASI_DATASET:
        percorso_json = os.path.join(CARTELLA_JSON, nome_file)
        if not os.path.exists(percorso_json): continue
            
        nome_caso = nome_file.replace(".json", "")
        golden_query = genera_golden_monolitica_da_json(percorso_json)
        
        # SALVATAGGIO DELLA GOLDEN QUERY
        # GESTIONE DELLA GOLDEN QUERY
        file_golden = os.path.join(CARTELLA_OUTPUT, f"golden_{nome_caso}.cypher")
        
        if os.path.exists(file_golden):
            # Se esiste già, legge quella calcolata in precedenza
            with open(file_golden, "r", encoding="utf-8") as f:
                golden_query = f.read()
        else:
            # Se non esiste, la genera dal JSON e la salva
            golden_query = genera_golden_monolitica_da_json(percorso_json)
            with open(file_golden, "w", encoding="utf-8") as f:
                f.write(golden_query)
        
        query_react = map_react.get(nome_file, "")
        query_llm = map_llm.get(nome_file, "")
        
        score_react = calcola_metriche(query_react, golden_query)
        score_llm = calcola_metriche(query_llm, golden_query)
        
        risultati.append({
            "Caso": nome_caso,
            "ReAct_Coseno": score_react["cosine"],
            "ReAct_RougeL": score_react["rougeL"],
            "LLM_Coseno": score_llm["cosine"],
            "LLM_RougeL": score_llm["rougeL"]
        })

    # SALVATAGGIO REPORT
    file_report = os.path.join(CARTELLA_OUTPUT, f"report_metriche_{tipo_report}.txt")
    with open(file_report, "w", encoding="utf-8") as f:
        f.write(f"REPORT TIPO: {tipo_report}\n")
        f.write(f"{'CASO':<30} | {'REACT COS':<9} | {'REACT ROUGE':<11} | {'LLM COS':<9} | {'LLM ROUGE'}\n")
        f.write("-" * 80 + "\n")
        avg_react_cos = avg_react_rgl = avg_llm_cos = avg_llm_rgl = 0
        for r in risultati:
            f.write(f"{r['Caso']:<30} | {r['ReAct_Coseno']:<9.4f} | {r['ReAct_RougeL']:<11.4f} | {r['LLM_Coseno']:<9.4f} | {r['LLM_RougeL']:.4f}\n")
            avg_react_cos += r['ReAct_Coseno']
            avg_react_rgl += r['ReAct_RougeL']
            avg_llm_cos += r['LLM_Coseno']
            avg_llm_rgl += r['LLM_RougeL']
        if risultati:
            n = len(risultati)
            f.write("-" * 80 + "\n")
            f.write(f"{'MEDIA GLOBALE':<30} | {avg_react_cos/n:<9.4f} | {avg_react_rgl/n:<11.4f} | {avg_llm_cos/n:<9.4f} | {avg_llm_rgl/n:.4f}\n")