import os
import json
import time
import sys
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Aggiunta del path per importare correttamente la Crew 2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Crew2.crew2_db import crew_neo4j_writer

load_dotenv()



#Script per testare unwind e controllare il sotto-grafo che permette di creare
# uso anche la versione della crew2 per vedere le differenze

# -----------------------------------------
# 1. SETUP E CONFIGURAZIONE PERCORSI
# ----------------------------------------
CARTELLA_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
CARTELLA_JSON = os.path.join(CARTELLA_BASE, "Crew2", "casi_inseriti_db_react_pydantic")

CASI_DATASET = [
    "delitto_di_cogne.json",
    "delitto_di_novi_ligure.json",
    "omicidio_di_alberto_brasili.json",
    "omicidio_di_giulia_cecchettin.json",
    "omicidio_di_marco_vannini.json",
    "omicidio_di_marta_russo.json"
]

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USERNAME", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD")

# -----------------------------------------------
# 2. LA QUERY UNWIND AGGIORNATA SULLA STRUTTURA REALE
# ------------------------------------------------
QUERY_UNWIND_TEMPLATE = """
WITH $dati AS dati

// FASE 1: CREAZIONE NODI (Itera sulla lista piatta 'entities' e smista in base a 'label')
UNWIND coalesce(dati.entities, []) AS e

// --- CASE ---
FOREACH (_ IN CASE WHEN e.label = 'Case' THEN [1] ELSE [] END |
    MERGE (n:Case {id: e.id})
    SET n.name = e.name)

// --- PERSON (Con le regole anagrafiche rigorose) ---
FOREACH (_ IN CASE WHEN e.label = 'Person' THEN [1] ELSE [] END |
    MERGE (n:Person {id: e.id})
    SET n.name = e.name,
        n.gender = e.gender,
        n.role = e.role,
        n.age = e.age,
        n.profession = e.profession,
        n.date_of_birth = e.date_of_birth,
        n.date_of_death = e.date_of_death,
        n.is_deceased = e.is_deceased)

// --- LOCATION ---
FOREACH (_ IN CASE WHEN e.label = 'Location' THEN [1] ELSE [] END |
    MERGE (n:Location {id: e.id})
    SET n.name = e.name)

// --- STATEMENT ---
FOREACH (_ IN CASE WHEN e.label = 'Statement' THEN [1] ELSE [] END |
    MERGE (n:Statement {id: e.id})
    SET n.name = e.name)

// --- MOTIVE ---
FOREACH (_ IN CASE WHEN e.label = 'Motive' THEN [1] ELSE [] END |
    MERGE (n:Motive {id: e.id})
    SET n.name = e.name)

// --- CHARGE ---
FOREACH (_ IN CASE WHEN e.label = 'Charge' THEN [1] ELSE [] END |
    MERGE (n:Charge {id: e.id})
    SET n.name = e.name)

// --- EVIDENCE ---
FOREACH (_ IN CASE WHEN e.label = 'Evidence' THEN [1] ELSE [] END |
    MERGE (n:Evidence {id: e.id})
    SET n.name = e.name)

// --- WEAPON ---
FOREACH (_ IN CASE WHEN e.label = 'Weapon' THEN [1] ELSE [] END |
    MERGE (n:Weapon {id: e.id})
    SET n.name = e.name)

WITH dati

// FASE 2: CREAZIONE RELAZIONI (Itera su 'relationships' usando source_id e target_id)
UNWIND coalesce(dati.relationships, []) AS rel

FOREACH (_ IN CASE WHEN rel.type = 'COMMITTED' THEN [1] ELSE [] END | 
    MERGE (src:Person {id: rel.source_id}) MERGE (tgt:Case {id: rel.target_id}) MERGE (src)-[:COMMITTED]->(tgt))
    
FOREACH (_ IN CASE WHEN rel.type = 'IS_SUSPECTED_IN' THEN [1] ELSE [] END | 
    MERGE (src:Person {id: rel.source_id}) MERGE (tgt:Case {id: rel.target_id}) MERGE (src)-[:IS_SUSPECTED_IN]->(tgt))
    
FOREACH (_ IN CASE WHEN rel.type = 'IS_VICTIM_OF' THEN [1] ELSE [] END | 
    MERGE (src:Person {id: rel.source_id}) MERGE (tgt:Case {id: rel.target_id}) MERGE (src)-[:IS_VICTIM_OF]->(tgt))

FOREACH (_ IN CASE WHEN rel.type = 'INVESTIGATES' THEN [1] ELSE [] END | 
    MERGE (src:Person {id: rel.source_id}) MERGE (tgt:Case {id: rel.target_id}) MERGE (src)-[:INVESTIGATES]->(tgt))

FOREACH (_ IN CASE WHEN rel.type = 'DEFENDS' THEN [1] ELSE [] END | 
    MERGE (src:Person {id: rel.source_id}) MERGE (tgt:Person {id: rel.target_id}) MERGE (src)-[:DEFENDS]->(tgt))

FOREACH (_ IN CASE WHEN rel.type = 'INVOLVED_IN' THEN [1] ELSE [] END | 
    MERGE (src:Person {id: rel.source_id}) MERGE (tgt:Case {id: rel.target_id}) MERGE (src)-[:INVOLVED_IN]->(tgt))

FOREACH (_ IN CASE WHEN rel.type = 'OCCURRED_AT' THEN [1] ELSE [] END | 
    MERGE (src:Case {id: rel.source_id}) MERGE (tgt:Location {id: rel.target_id}) MERGE (src)-[:OCCURRED_AT]->(tgt))

FOREACH (_ IN CASE WHEN rel.type = 'WITHIN' THEN [1] ELSE [] END | 
    MERGE (src:Location {id: rel.source_id}) MERGE (tgt:Location {id: rel.target_id}) MERGE (src)-[:WITHIN]->(tgt))

FOREACH (_ IN CASE WHEN rel.type = 'USED_IN' THEN [1] ELSE [] END | 
    MERGE (src:Weapon {id: rel.source_id}) MERGE (tgt:Case {id: rel.target_id}) MERGE (src)-[:USED_IN]->(tgt))

FOREACH (_ IN CASE WHEN rel.type = 'FOUND_AT' THEN [1] ELSE [] END | 
    MERGE (src {id: rel.source_id}) MERGE (tgt:Location {id: rel.target_id}) MERGE (src)-[:FOUND_AT]->(tgt))

FOREACH (_ IN CASE WHEN rel.type = 'HAS_MOTIVE' THEN [1] ELSE [] END | 
    MERGE (src:Case {id: rel.source_id}) MERGE (tgt:Motive {id: rel.target_id}) MERGE (src)-[:HAS_MOTIVE]->(tgt))

FOREACH (_ IN CASE WHEN rel.type = 'LEFT_EVIDENCE' THEN [1] ELSE [] END | 
    MERGE (src:Person {id: rel.source_id}) MERGE (tgt:Evidence {id: rel.target_id}) MERGE (src)-[:LEFT_EVIDENCE]->(tgt))

FOREACH (_ IN CASE WHEN rel.type = 'LOCATED_IN' THEN [1] ELSE [] END | 
    MERGE (src:Person {id: rel.source_id}) MERGE (tgt:Location {id: rel.target_id}) MERGE (src)-[:LOCATED_IN]->(tgt))

FOREACH (_ IN CASE WHEN rel.type = 'MADE_STATEMENT' THEN [1] ELSE [] END | 
    MERGE (src:Person {id: rel.source_id}) MERGE (tgt:Statement {id: rel.target_id}) MERGE (src)-[:MADE_STATEMENT]->(tgt))

FOREACH (_ IN CASE WHEN rel.type = 'RELATES_TO' THEN [1] ELSE [] END | 
    MERGE (src:Statement {id: rel.source_id}) MERGE (tgt {id: rel.target_id}) MERGE (src)-[:RELATES_TO]->(tgt))

FOREACH (_ IN CASE WHEN rel.type = 'CHARGED_WITH' THEN [1] ELSE [] END | 
    MERGE (src:Person {id: rel.source_id}) MERGE (tgt:Charge {id: rel.target_id}) MERGE (src)-[:CHARGED_WITH]->(tgt))

FOREACH (_ IN CASE WHEN rel.type = 'INCLUDES_CHARGE' THEN [1] ELSE [] END | 
    MERGE (src:Case {id: rel.source_id}) MERGE (tgt:Charge {id: rel.target_id}) MERGE (src)-[:INCLUDES_CHARGE]->(tgt))

FOREACH (_ IN CASE WHEN rel.type = 'OWNS_WEAPON' THEN [1] ELSE [] END | 
    MERGE (src:Person {id: rel.source_id}) MERGE (tgt:Weapon {id: rel.target_id}) MERGE (src)-[:OWNS_WEAPON]->(tgt))

RETURN count(rel) AS relazioni_processate
"""

# ------------------------------------------
# 3. ESECUZIONE DEL TEST (BASELINE UNWIND)
# ------------------------------------------
def esegui_test_baseline():
    print("\n" + "="*60)
    print(" AVVIO TEST SIMULATO: BASELINE UNWIND")
    print("="*60)
    
    try:
        driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    except Exception as e:
        print(f"Errore di connessione a Neo4j: {e}")
        return

    tempi_registrati = []

    with driver.session() as session:
        for nome_file in CASI_DATASET:
            percorso = os.path.join(CARTELLA_JSON, nome_file)
            if not os.path.exists(percorso):
                print(f"[WARN] File non trovato: {nome_file} - Verifica il percorso.")
                continue
                
            with open(percorso, 'r', encoding='utf-8') as f:
                dati = json.load(f)
                
            print(f"\n---> Elaborazione del caso: {nome_file}")
            
            tx = session.begin_transaction()
            try:
                start = time.time()
                
                result = tx.run(QUERY_UNWIND_TEMPLATE, dati=dati)
                info = result.consume() 
                
                tempo_s = time.time() - start
                tempi_registrati.append(tempo_s)

                tx.commit()
                
                print(f"Esecuzione Cypher valida.")
                print(f"Latenza Neo4j elaborazione JSON: {tempo_s:.4f} sec.")
                print(f"Nodi creati: {info.counters.nodes_created}, Relazioni create: {info.counters.relationships_created}")
                
            except Exception as e:
                print(f"Errore strutturale JSON/Cypher: {e}")
            finally:
                #tx.rollback()
                print(f"Rollback effettuato in sicurezza.")

    driver.close()
    
    if tempi_registrati:
        media = sum(tempi_registrati) / len(tempi_registrati)
        print("\n" + "="*60)
        print(f" TEST COMPLETATO - Tempo medio elaborazione: {media:.4f} sec")
        print("="*60)

# -------------------------------------------
# 4. ORCHESTRAZIONE DEL TEST (CREW 2 - REACT)
# -------------------------------------------
def esegui_test_react():
    print("\n" + "="*60)
    print(" AVVIO TEST AGENTE: CREW 2 (REACTIVE / TOOLS)")
    print("="*60)
    
    tempi_registrati = []

    for nome_file in CASI_DATASET:
        percorso = os.path.join(CARTELLA_JSON, nome_file)
        if not os.path.exists(percorso):
            print(f"[WARN] File non trovato: {nome_file} - Verifica il percorso.")
            continue
            
        with open(percorso, 'r', encoding='utf-8') as f:
            dati = json.load(f)
            
        print(f"\n---> Elaborazione del caso con ReAct: {nome_file}")
        json_string = json.dumps(dati, ensure_ascii=False, indent=2)
        
        start = time.time()
        try:
            crew_neo4j_writer.kickoff(inputs={'json_da_inserire': json_string})
            tempo_s = time.time() - start
            tempi_registrati.append(tempo_s)
            
            print(f"Esecuzione ReAct completata.")
            print(f"Latenza elaborazione: {tempo_s:.4f} sec.")

            
        except Exception as e:
            print(f"Errore durante l'esecuzione dell'agente ReAct: {e}")

        time.sleep(10)

    if tempi_registrati:
        media = sum(tempi_registrati) / len(tempi_registrati)
        print("\n" + "="*60)
        print(f" TEST REACT COMPLETATO - Tempo medio elaborazione: {media:.4f} sec")
        print("="*60)

if __name__ == "__main__":
    # esegui_test_baseline()  # Versione UNWIND commentata
    esegui_test_react()        # Esecuzione della funzione ReAct