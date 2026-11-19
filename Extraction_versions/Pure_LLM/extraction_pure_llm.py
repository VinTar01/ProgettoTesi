import json
import os
import sys
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

#Definizione dei percorsi
current_dir = os.path.dirname(os.path.abspath(__file__)) 
extraction_dir = os.path.dirname(current_dir)            
root_dir = os.path.dirname(extraction_dir)               

# Aggiunge Extraction_versions al path per poter importare prompt.py
sys.path.append(extraction_dir)
from prompt import PROMPT_BASE, PROMPT_STRUTTURA

# Setup percorsi file puntando alla root corretta
INPUT_JSON_PATH = os.path.join(root_dir, "data", "raw", "dataset_cronaca_completo.json")
OUTPUT_FOLDER = os.path.join(current_dir, "output_json")

# Inizializzazione API: carica il .env dalla root principale
load_dotenv(os.path.join(root_dir, ".env"))


def estrai_informazioni_caso(testo_caso: str, client: genai.Client) -> dict:
    """Combina i prompt ed esegue l'estrazione per un singolo caso."""
    prompt_template = PROMPT_BASE + "\n\n" + PROMPT_STRUTTURA
    prompt_completo = prompt_template.replace("{testo_caso}", testo_caso)
    
    try:
        # invocazione modello
        response = client.models.generate_content(
            model='gemini-flash-lite-latest',
            contents=prompt_completo,
            config=types.GenerateContentConfig(
                temperature=0,
            ),
        )
        
        raw_text = response.text.strip()
        
        # Pulizia backtick Markdown
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:]
            
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        return json.loads(raw_text.strip())
        
    except json.JSONDecodeError as e:
        print(f"  [Errore Parsing JSON] L'LLM non ha generato un JSON valido: {e}")
        return {"entities": [], "relationships": [], "error": "JSONDecodeError"}
    except Exception as e:
        print(f"  [Errore API] {e}")
        return {"entities": [], "relationships": [], "error": str(e)}


def main():
    # Creazione cartella di output dentro Pure_LLM
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    print(f"Cartella di output pronta: {OUTPUT_FOLDER}")

    # Verifica esistenza del file di input
    if not os.path.exists(INPUT_JSON_PATH):
        print(f"Errore: File dataset non trovato in {INPUT_JSON_PATH}")
        return

    with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    print(f"Trovati {len(dataset)} casi nel dataset. Avvio estrazione...")

    # Inizializzazione del client Google GenAI tramite variabile d'ambiente
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    for i, caso in enumerate(dataset):
        caso_id = caso.get("id", f"caso_{i}")
        file_output = os.path.join(OUTPUT_FOLDER, f"{caso_id}.json")
        
        # Salta i casi già processati (utile se l'esecuzione si interrompe e va ripresa)
        if os.path.exists(file_output):
            print(f"[{i+1}/{len(dataset)}] Skipped (già estratto): {caso_id}")
            continue
            
        print(f"[{i+1}/{len(dataset)}] Elaborazione: {caso['title']}...")
        
        # Esecuzione LLM passando il nuovo client
        risultato_json = estrai_informazioni_caso(caso["text"], client)
        
        # Salvataggio su file
        with open(file_output, "w", encoding="utf-8") as out_f:
            json.dump(risultato_json, out_f, indent=4, ensure_ascii=False)
            
        # Pausa per rispettare i rate limit delle api Google
        time.sleep(5)
        
    print("\nElaborazione completata.")

if __name__ == "__main__":
    main()