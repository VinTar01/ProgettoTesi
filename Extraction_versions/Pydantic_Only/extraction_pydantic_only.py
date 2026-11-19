import json
import os
import sys
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv


# uguale all'estrazione fatta con LLM puro ma agganciando lo schema pydantic



current_dir = os.path.dirname(os.path.abspath(__file__)) # .../Pydantic_Only
extraction_dir = os.path.dirname(current_dir)            # .../Extraction_versions
root_dir = os.path.dirname(extraction_dir)               # .../Thesis_New_Version


sys.path.append(extraction_dir) # Necessario per importare prompt.py
sys.path.append(root_dir)       # Necessario per importare schemas.py dalla root



from prompt import PROMPT_BASE
from schemas import SchemaGrafo

INPUT_JSON_PATH = os.path.join(root_dir, "data", "raw", "dataset_cronaca_completo.json")
OUTPUT_FOLDER = os.path.join(current_dir, "output_json")

load_dotenv(os.path.join(root_dir, ".env"))


def estrai_informazioni_strutturate(testo_caso: str, client: genai.Client, max_retries: int = 3) -> dict:
    """Esegue l'estrazione forzando l'output JSON tramite schema Pydantic (Structured Outputs)."""
    
    prompt_completo = PROMPT_BASE.replace("{testo_caso}", testo_caso)
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-flash-lite-latest',
                contents=prompt_completo,
                config=types.GenerateContentConfig(
                    temperature=0,
                    # Vincolo dell'output JSON allo schema Pydantic SchemaGrafo
                    response_mime_type="application/json",
                    response_schema=SchemaGrafo,
                ),
            )
            
            return json.loads(response.text)
            
        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "UNAVAILABLE" in error_msg or "429" in error_msg:
                wait_time = (attempt + 1) * 15
                print(f"  [Server Occupato] Tentativo {attempt + 1}/{max_retries} fallito. Attesa di {wait_time} s...")
                time.sleep(wait_time)
            else:
                print(f"  [Errore API Irreversibile] {e}")
                return {"entities": [], "relationships": [], "error": str(e)}
                
    return {"entities": [], "relationships": [], "error": "Max retries exceeded"}


def main():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    print(f"Cartella di output pronta: {OUTPUT_FOLDER}")

    if not os.path.exists(INPUT_JSON_PATH):
        print(f"Errore: File dataset non trovato in {INPUT_JSON_PATH}")
        return

    with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    print(f"Trovati {len(dataset)} casi. Avvio estrazione strutturata (Pydantic)...")

    for i, caso in enumerate(dataset):
        caso_id = caso.get("id", f"caso_{i}")
        file_output = os.path.join(OUTPUT_FOLDER, f"{caso_id}.json")
        
        if os.path.exists(file_output):
            print(f"[{i+1}/{len(dataset)}] Skipped (già estratto): {caso_id}")
            continue
            
        print(f"\n[{i+1}/{len(dataset)}] Elaborazione: {caso['title']}...")
        
        risultato_json = estrai_informazioni_strutturate(caso["text"], client)
        
        with open(file_output, "w", encoding="utf-8") as out_f:
            json.dump(risultato_json, out_f, indent=4, ensure_ascii=False)
            
        time.sleep(5)

if __name__ == "__main__":
    main()