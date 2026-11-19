import json
import os
import time
from dotenv import load_dotenv
from crewai import Crew, Process

# Moduli locali della pipeline ReAct
from tool import CaseReaderTool
from agent import create_extractor_agent
from task import create_extraction_task

# 1. Configurazione dei percorsi
current_dir = os.path.dirname(os.path.abspath(__file__)) # .../ReAct_Only
extraction_dir = os.path.dirname(current_dir)            # .../Extraction_versions
root_dir = os.path.dirname(extraction_dir)               # .../Thesis_New_Version

INPUT_JSON_PATH = os.path.join(root_dir, "data", "raw", "dataset_cronaca_completo.json")

OUTPUT_FOLDER = os.path.join(current_dir, "output_json")

# Caricamento dele variabili d'ambiente
load_dotenv(os.path.join(root_dir, ".env"))

def main():
    # Creo la cartella di destinazione se non esiste
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    print(f"Cartella di output pronta: {OUTPUT_FOLDER}")

    # Controllo di sicurezza sull'esistenza del dataset
    if not os.path.exists(INPUT_JSON_PATH):
        print(f"Errore: Dataset non trovato in {INPUT_JSON_PATH}")
        return

    # Carica in memoria tutti i testi estratti da Wikipedia
    with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # Inizializzazione del tool con percorso del dataset incapsulato
    reader_tool = CaseReaderTool(dataset_path=INPUT_JSON_PATH)
    
    # Istanziazione unica dell'agente riutilizzata per l'intero dataset
    analyst_agent = create_extractor_agent(tools=[reader_tool])

    print(f"Trovati {len(dataset)} casi nel dataset. Avvio pipeline ReAct...")

    for i, caso in enumerate(dataset):
        caso_id = caso.get("id", f"caso_{i}")
        file_output = os.path.join(OUTPUT_FOLDER, f"{caso_id}.json")
        
        # se l'estrazione cade, ripartirà saltando i file già generati
        if os.path.exists(file_output):
            print(f"[{i+1}/{len(dataset)}] Skipped (già estratto): {caso_id}")
            continue
            
        print(f"\n[{i+1}/{len(dataset)}] Elaborazione ReAct: {caso['title']}...")
        
        # Creazione dinamica del task per il caso corrente
        # È qui che il template sostituisce {testo_caso} con l'istruzione logica di usare il tool.
        task = create_extraction_task(agent=analyst_agent, case_title=caso['title'])
        
        # Configurazione ed esecuzione sequenziale TOA della Crew
        crew = Crew(
            agents=[analyst_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            
            result = crew.kickoff()
            raw_text = str(result.raw).strip()
            
            # Pulizia delimitatori
            if raw_text.startswith("```json"): 
                raw_text = raw_text[7:]
            elif raw_text.startswith("```"): 
                raw_text = raw_text[3:]
            if raw_text.endswith("```"): 
                raw_text = raw_text[:-3]
            
            # Trasforma la stringa pulita in un dizionario Python
            risultato_json = json.loads(raw_text.strip())
            
        except json.JSONDecodeError:
            print(f"  [Errore Parsing] L'agente non ha formattato bene il JSON finale.")
            risultato_json = {"entities": [], "relationships": [], "error": "JSONDecodeError"}
        except Exception as e:
            # Catturo errori di timeout o cadute delle API
            print(f"  [Errore CrewAI] {e}")
            risultato_json = {"entities": [], "relationships": [], "error": str(e)}

        # Salva il dizionario nel file JSON di output
        with open(file_output, "w", encoding="utf-8") as out_f:
            json.dump(risultato_json, out_f, indent=4, ensure_ascii=False)
            
        
        time.sleep(8)

if __name__ == "__main__":
    main()