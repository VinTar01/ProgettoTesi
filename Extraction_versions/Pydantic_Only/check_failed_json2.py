import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(current_dir, "output_json")

def analizza_e_pulisci():
    if not os.path.exists(output_dir):
        print(f"La cartella {output_dir} non esiste!")
        return

    statistiche = {
        "validi": [],
        "errore_pydantic_crewai": [],
        "errore_api_server": [],
        "errore_generico": [],
        "malformati_rotti": []
    }

    for filename in os.listdir(output_dir):
        if not filename.endswith(".json"):
            continue
            
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                dati = json.load(f)
                
            if "error" in dati and dati["error"]:
                msg_errore = str(dati["error"]).lower()
                if "validation error for taskoutput" in msg_errore or "json_dict" in msg_errore:
                    statistiche["errore_pydantic_crewai"].append(filename)
                elif "429" in msg_errore or "503" in msg_errore or "quota" in msg_errore or "unavailable" in msg_errore:
                    statistiche["errore_api_server"].append(filename)
                else:
                    statistiche["errore_generico"].append(filename)
            elif "entities" in dati and "relationships" in dati:
                statistiche["validi"].append(filename)
            else:
                statistiche["errore_generico"].append(filename) 
                
        except json.JSONDecodeError:
            statistiche["malformati_rotti"].append(filename)
        except Exception as e:
            statistiche["errore_generico"].append(filename)

    totale = sum(len(v) for v in statistiche.values())
    
    file_da_cancellare = (
        statistiche["errore_pydantic_crewai"] + 
        statistiche["errore_api_server"] + 
        statistiche["errore_generico"] + 
        statistiche["malformati_rotti"]
    )

    print("\n" + "="*50)
    print(" REPORT ANALISI CARTELLA OUTPUT_JSON ")
    print("="*50)
    print(f"Totale file analizzati: {totale}")
    print(f"File VALIDI e completi: {len(statistiche['validi'])}")
    print(f"Errori Bug Pydantic/CrewAI: {len(statistiche['errore_pydantic_crewai'])}")
    print(f"Errori Server/API (Alta domanda): {len(statistiche['errore_api_server'])}")
    print(f"Errori generici: {len(statistiche['errore_generico'])}")
    print(f"File corrotti (Non JSON): {len(statistiche['malformati_rotti'])}")

    if file_da_cancellare:
        print("\n--- DETTAGLIO FILE DIFETTOSI ---")
        for f in file_da_cancellare:
            print(f" - {f}")
            
        scelta = input(f"\nVuoi cancellare automaticamente questi {len(file_da_cancellare)} file? [Y/N]: ")
        
        if scelta.strip().lower() == 'y':
            cancellati_con_successo = 0
            for filename in file_da_cancellare:
                filepath = os.path.join(output_dir, filename)
                try:
                    os.remove(filepath)
                    cancellati_con_successo += 1
                except Exception as e:
                    print(f"Impossibile cancellare {filename}: {e}")
            
            print(f"\nPulizia completata! Eliminati {cancellati_con_successo} file.")
            print("Ora puoi rilanciare l'orchestratore per recuperarli.")
        else:
            print("\nOperazione annullata. Nessun file è stato cancellato.")
    else:
        print("\nNon ci sono file difettosi da cancellare. Il dataset estratto è perfetto!")

if __name__ == "__main__":
    analizza_e_pulisci()