import os
import re
import dateparser
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "myThesis" 

# Dizionario per i numeri testuali e i suffissi "-enne"
NUMERI_TESTUALI = {
    "zero": 0, "un": 1, "uno": 1, "una": 1, "due": 2, "tre": 3, "quattro": 4, 
    "cinque": 5, "sei": 6, "sette": 7, "otto": 8, "nove": 9, "dieci": 10,
    "undici": 11, "dodici": 12, "tredici": 13, "quattordici": 14, 
    "quindici": 15, "sedici": 16, "diciassette": 17, "diciotto": 18, 
    "diciannove": 19, "venti": 20, "ventuno": 21, "ventidue": 22,
    "diciannovenne": 19, "ventenne": 20, "trentenne": 30, "quarantenne": 40,
    "cinquantenne": 50, "sessantenne": 60, "settantenne": 70, "ottantenne": 80,
    "novantenne": 90
}

def normalizza_eta_avanzata(eta_str):
    """Parsa cifre, stringhe testuali e casi limite per estrarre l'età in intero."""
    if not eta_str:
        return None
        
    eta_str = str(eta_str).lower().strip()
    
    # 1. Casi limite specifici
    if "un anno e mezzo" in eta_str:
        return 1
    if "mesi" in eta_str and "anni" not in eta_str:
        return 0 # Neonati (sotto l'anno di età)
        
    # 2. Cerca cifre arabe (es. "18" in "diciotto (18 anni)")
    match_num = re.search(r'\d+', eta_str)
    if match_num:
        return int(match_num.group())
        
    # 3. Cerca stringhe testuali
    # Ordiniamo le chiavi per lunghezza decrescente così "diciannovenne" 
    # viene intercettato prima di "diciannove" o "nove"
    for parola in sorted(NUMERI_TESTUALI.keys(), key=len, reverse=True):
        if parola in eta_str:
            return NUMERI_TESTUALI[parola]
            
    return None

def standardizza_grafo():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    
    with driver.session() as session:
        # ==========================================
        # 1. STANDARDIZZAZIONE ETÀ (Logica Avanzata)
        # ==========================================
        print("-> Estrazione interi per l'età...")
        result_eta = session.run("MATCH (p:Person) WHERE p.age IS NOT NULL RETURN elementId(p) AS id, p.age AS age")
        
        aggiornati_eta = 0
        for record in result_eta:
            if isinstance(record["age"], str):
                nuova_eta = normalizza_eta_avanzata(record["age"])
                
                if nuova_eta is not None:
                    session.run("MATCH (p) WHERE elementId(p) = $id SET p.age = $nuova_eta", 
                                id=record["id"], nuova_eta=nuova_eta)
                    aggiornati_eta += 1
        print(f"   [OK] Età convertite: {aggiornati_eta}")

        # ==========================================
        # 2. STANDARDIZZAZIONE DATE (Uso standard dateparser)
        # ==========================================
        print("-> Parsing semantico delle date...")
        result_date = session.run("MATCH (n) WHERE n.date IS NOT NULL RETURN elementId(n) AS id, n.date AS data")
        
        aggiornati_date = 0
        for record in result_date:
            if isinstance(record["data"], str):
                data_parsata = dateparser.parse(record["data"], languages=['it'])
                
                if data_parsata:
                    data_iso = data_parsata.strftime("%Y-%m-%d")
                    session.run("MATCH (n) WHERE elementId(n) = $id SET n.date = $data_iso", 
                                id=record["id"], data_iso=data_iso)
                    aggiornati_date += 1
        print(f"   [OK] Date standardizzate: {aggiornati_date}")


    # ==========================================
        # 3. STANDARDIZZAZIONE DATE DI DECESSO
        # ==========================================
        print("-> Parsing date di decesso...")
        result_death = session.run("MATCH (p:Person) WHERE p.date_of_death IS NOT NULL RETURN elementId(p) AS id, p.date_of_death AS data")
        
        aggiornati_death = 0
        for record in result_death:
            if isinstance(record["data"], str):
                data_parsata = dateparser.parse(record["data"], languages=['it'])
                if data_parsata:
                    data_iso = data_parsata.strftime("%Y-%m-%d")
                    session.run("MATCH (p) WHERE elementId(p) = $id SET p.date_of_death = $data_iso", 
                                id=record["id"], data_iso=data_iso)
                    aggiornati_death += 1
        print(f"   [OK] Date di decesso standardizzate: {aggiornati_death}")


    # ==========================================
        # 4. STANDARDIZZAZIONE DATE DI NASCITA
        # ==========================================
        print("-> Parsing date di nascita...")
        result_birth = session.run("MATCH (p:Person) WHERE p.date_of_birth IS NOT NULL RETURN elementId(p) AS id, p.date_of_birth AS data")
        
        aggiornati_birth = 0
        for record in result_birth:
            if isinstance(record["data"], str):
                data_parsata = dateparser.parse(record["data"], languages=['it'])
                if data_parsata:
                    data_iso = data_parsata.strftime("%Y-%m-%d")
                    session.run("MATCH (p) WHERE elementId(p) = $id SET p.date_of_birth = $data_iso", 
                                id=record["id"], data_iso=data_iso)
                    aggiornati_birth += 1
        print(f"   [OK] Date di nascita standardizzate: {aggiornati_birth}")

    driver.close()
    print("-> Pulizia completata.")

if __name__ == "__main__":
    standardizza_grafo()