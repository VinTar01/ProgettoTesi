import json
import os
import time
from typing import TypedDict, List
from dotenv import load_dotenv
from crewai import Crew, Process
from langgraph.graph import StateGraph, END

# import de componenti della nostra cartella
from tool1 import CaseReaderTool
from agent1 import create_extractor_agent
from task1 import create_structured_extraction_task
from schemas import SchemaGrafo

# 1. Configurazione dei percorsi
current_dir = os.path.dirname(os.path.abspath(__file__)) # .../ReAct_Pydantic
extraction_dir = os.path.dirname(current_dir)            # .../Extraction_versions
root_dir = os.path.dirname(extraction_dir)               # .../Thesis_New_Version

INPUT_JSON_PATH = os.path.join(root_dir, "data", "raw", "dataset_cronaca_completo.json")
OUTPUT_FOLDER = os.path.join(current_dir, "output_json")

load_dotenv(os.path.join(root_dir, ".env"))

# -----------------------------------------
# LO STATO GLOBALE (LANGGRAPH)
# -----------------------------------------
class GraphState(TypedDict):
    """La memoria condivisa del sistema che tiene traccia dell'avanzamento."""
    dataset_casi: List[dict]       # Tutti i casi caricati dal file JSON locale
    indice_corrente: int           # A che punto siamo dell'iterazione
    casi_completati: List[str]     # ID o titoli dei casi elaborati con successo
    casi_falliti: List[str]        # ID o titoli dei casi andati in errore


# ------------------------------------------
# I NODI DEL GRAFO
# ------------------------------------------

def inizializza_processo(state: GraphState):
    """
    NODO 1: Carica in memoria il dataset locale e prepara le liste di controllo nello Stato.
    """
    print("\n[NODO 1: Inizializzazione] Caricamento dataset locale...")
    if not os.path.exists(INPUT_JSON_PATH):
        print(f"[ERRORE] Dataset non trovato in {INPUT_JSON_PATH}")
        return {"dataset_casi": [], "indice_corrente": 0, "casi_completati": [], "casi_falliti": []}
        
    with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    print(f"[INFO] Dataset caricato con successo. Totale casi: {len(dataset)}")
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    return {
        "dataset_casi": dataset,
        "indice_corrente": 0,
        "casi_completati": [],
        "casi_falliti": []
    }


def elabora_prossimo_caso(state: GraphState):
    """
    NODO 2: Preleva un caso alla volta dalla lista basandosi sull'indice corrente, 
    verifica i checkpoint (skip se già fatto) ed esegue la Crew (ReAct + Pydantic).
    """
    dataset = state["dataset_casi"]
    indice = state["indice_corrente"]
    completati = state["casi_completati"].copy()
    falliti = state["casi_falliti"].copy()

    # Condizione di sicurezza se l'indice supera la dimensione del dataset
    if indice >= len(dataset):
        return state

    caso = dataset[indice]
    caso_id = caso.get("id", f"caso_{indice}")
    file_output = os.path.join(OUTPUT_FOLDER, f"{caso_id}.json")

    print(f"\n[NODO 2: Elaborazione] [{indice + 1}/{len(dataset)}] Caso: {caso['title']}")

    # se il file esiste già, lo saltiamo
    if os.path.exists(file_output):
        print(f"  -> [SKIP] File già esistente per {caso_id}")
        completati.append(caso_id)
        return {
            "indice_corrente": indice + 1,
            "casi_completati": completati,
            "casi_falliti": falliti
        }

    # Inizializza tool e agente per questo step
    reader_tool = CaseReaderTool(dataset_path=INPUT_JSON_PATH)
    analyst_agent = create_extractor_agent(tools=[reader_tool])
    

    #for i, caso in enumerate(dataset):
    # A ogni iterazione crea un task specifico per il caso
    task = create_structured_extraction_task(agent=analyst_agent, case_title=caso['title'])
    
    crew = Crew(
        agents=[analyst_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )

    try:
        # Avvio della Crew (ReAct + Pydantic)
        crew.kickoff()
        
        # Estrazione del dizionario JSON validato dall'output del task
        if task.output and task.output.json_dict:
            risultato_json = task.output.json_dict
        else:
            risultato_json = json.loads(task.output.raw)

        # Salvataggio del file JSON validato
        with open(file_output, "w", encoding="utf-8") as out_f:
            json.dump(risultato_json, out_f, indent=4, ensure_ascii=False)
            
        print(f"  -> [SUCCESSO] Salvato in {file_output}")
        completati.append(caso_id)

    except Exception as e:
        error_msg = str(e)
        # Intercettiamo il bug specifico di CrewAI/Pydantic
        if "validation error for TaskOutput" in error_msg and "json_dict" in error_msg:
            print("  -> [RECOVERY] Intercettato bug di conversione CrewAI. Recupero del JSON grezzo...")
            try:
                # estrae il testo grezzo saltando il parser difettoso di CrewAI
                raw_text = task.output.raw.strip()
                
                # pulizia eventuali markdown che Gemini potrebbe aver inserito
                if raw_text.startswith("```json"): raw_text = raw_text[7:]
                if raw_text.startswith("```"): raw_text = raw_text[3:]
                if raw_text.endswith("```"): raw_text = raw_text[:-3]
                
                risultato_json = json.loads(raw_text.strip())
                
                # Salviamo il file recuperato
                with open(file_output, "w", encoding="utf-8") as out_f:
                    json.dump(risultato_json, out_f, indent=4, ensure_ascii=False)
                    
                print(f"  -> [SUCCESSO - RECOVERY] File salvato superando il bug in {file_output}")
                completati.append(caso_id)
                
            except Exception as recovery_e:
                print(f"  -> [ERRORE FATALE] Impossibile recuperare il JSON: {recovery_e}")
                falliti.append(caso_id)
                error_payload = {"entities": [], "relationships": [], "error": f"Recovery failed: {recovery_e}"}
                with open(file_output, "w", encoding="utf-8") as out_f:
                    json.dump(error_payload, out_f, indent=4, ensure_ascii=False)
        else:
            # Check errore API normale o di connessione
            print(f"  -> [ERRORE] Fallimento esecuzione Crew: {e}")
            falliti.append(caso_id)
            error_payload = {"entities": [], "relationships": [], "error": str(e)}
            with open(file_output, "w", encoding="utf-8") as out_f:
                json.dump(error_payload, out_f, indent=4, ensure_ascii=False)

    
    print("  -> [ATTESA] Pausa di sicurezza di n secondi...")
    time.sleep(8)

    return {
        "indice_corrente": indice + 1,
        "casi_completati": completati,
        "casi_falliti": falliti
    }


def verifica_completamento(state: GraphState):
    """
    NODO DI CONTROLLO (Semaforo): Decide se il grafo deve continuare a elaborare casi 
    o se il dataset è terminato.
    """
    if state["indice_corrente"] >= len(state["dataset_casi"]):
        return "fine"
    return "continua"


# ----------------------------------
# COSTRUZIONE DEL GRAFO DI STATO
#-----------------------------------
workflow = StateGraph(GraphState)

workflow.add_node("inizializzazione", inizializza_processo)
workflow.add_node("elaborazione", elabora_prossimo_caso)

workflow.set_entry_point("inizializzazione")

# Collega l'inizializzazione direttamente al primo blocco di elaborazione
workflow.add_edge("inizializzazione", "elaborazione")

# Ciclo condizionale: ripete "elaborazione" finché ci sono casi, altrimenti esce (END)
workflow.add_conditional_edges(
    "elaborazione", 
    verifica_completamento, 
    {
        "continua": "elaborazione", 
        "fine": END
    }
)

app = workflow.compile()


# ----------------------------------------
# ESECUZIONE PRINCIPALE
# ------------------------------------------
if __name__ == "__main__":
    print("\n" + "="*50)
    print(" AVVIO PIPELINE LANGGRAPH: ReAct + Pydantic")
    print("="*50)
    
    # Avvia il grafo passando uno stato iniziale vuoto
    stato_finale = app.invoke({
        "dataset_casi": [], 
        "indice_corrente": 0, 
        "casi_completati": [], 
        "casi_falliti": []
    })
    
    print("\n" + "="*50)
    print(" REPORT FINALE DELLE OPERAZIONI ")
    print("="*50)
    print(f"Casi elaborati con successo: {len(stato_finale['casi_completati'])}")
    print(f"Casi andati in errore: {len(stato_finale['casi_falliti'])}")
    print(f"Cartella di output: {OUTPUT_FOLDER}")