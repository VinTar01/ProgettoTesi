import os
import sys
from dotenv import load_dotenv
from Crew4.tools_crew4 import get_database_schema_text


# configurazione percorsi progetto
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

from Crew4.crew4_qa import crew_esploratore_grafo

# Carica le credenziali 
load_dotenv()

def main():
    print("="*50)
    print(" AVVIO ESPLORATORE GRAFO INVESTIGATIVO ")
    print("="*50)

    # ESTRAZIONE SCHEMA ALL'AVVIO
    print("\nEstrazione schema dinamico da Neo4j in corso...")
    current_schema = get_database_schema_text()
    print("Schema acquisito con successo!")


    print("Digita la tua domanda. Scrivi 'esci' o 'exit' per terminare.\n")

    while True:
        # Acquisizione dinamica della domanda da terminale
        domanda_di_prova = input("\nInvestigatore > ")

        # Condizione di uscita
        if domanda_di_prova.lower() in ['esci', 'exit', 'quit']:
            print("Chiusura dell'esploratore. Arrivederci!")
            break

        # Controllo input vuoto
        if not domanda_di_prova.strip():
            continue

        print("\nElaborazione in corso... L'agente sta formulando la query Cypher e interrogando Neo4j...\n")

        try:
            # Esecuzione della Crew
            risultato = crew_esploratore_grafo.kickoff(inputs={
                "domanda_utente": domanda_di_prova,
                "schema_grafo": current_schema
            })

            print("\n" + "="*50)
            print(" RISPOSTA DELL'AGENTE ")
            print("="*50)
            print(risultato)

        except Exception as e:
            print(f"\n[ERRORE] Esecuzione fallita: {e}")

if __name__ == "__main__":
    main()