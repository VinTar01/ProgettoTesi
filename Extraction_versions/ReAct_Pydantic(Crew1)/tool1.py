import json
import os
from crewai.tools import BaseTool
from pydantic import Field


class CaseReaderTool(BaseTool):
    # 'name' definisce il nome univoco del tool. Quando l'agente deciderà di fare un'azione (Action),
    # dovrà stampare esattamente questo nome per innescare lo strumento.
    name: str = "read_case_document"
    
    # 'description' viene iniettato nel prompt di sistema dell'agente.
    # Serve a spiegargli in linguaggio naturale a cosa serve questo strumento e quale argomento deve passargli.
    description: str = "Use this tool to read the full text of a true crime case. Pass the exact title of the case as the argument."
    
    # Uso Field di Pydantic per definire questa variabile di stato. I tre puntini '...' indicano 
    # che è un parametro obbligatorio in fase di inizializzazione della classe.
    dataset_path: str = Field(..., description="Path to the JSON raw dataset")

    # Questo è il cuore del tool: il metodo _run viene eseguito automaticamente da CrewAI 
    # quando l'agente invoca 'read_case_document' passando l'argomento 'title'.
    def _run(self, title: str) -> str:
        
        try:
            # Apro il file JSON locale usando il percorso nascosto all'agente
            with open(self.dataset_path, "r", encoding="utf-8") as f:
                dataset = json.load(f)
            
            # Ciclo sui casi nel database per cercare una corrispondenza
            for caso in dataset:
                if caso.get("title") == title or caso.get("id") == title:
                    # Ritorno l'intero testo del caso di cronaca all'agente come "Observation"
                    return caso["text"]
                    
            # Se il ciclo finisce senza risultati, non restituisco 'None', ma una frase esplicita.
            # In questo modo l'agente leggerà l'errore e capirà di aver sbagliato a scrivere il titolo.
            return "Error: Case not found. Check the title."
            
        except Exception as e:
            # Se l'apertura del file fallisce, restituisco l'eccezione come stringa.
            # L'agente leggerà l'errore tecnico come se fosse un'osservazione e non si bloccherà.
            return f"System error reading the document: {str(e)}"