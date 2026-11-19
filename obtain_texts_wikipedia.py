import os
import wikipediaapi
import json
import time


#Codice per estrarre i titoli e i tesi da wikipedia e formare un unico json

# un user-agent fittizio per bypassare le policy wikipedia
wiki_wiki = wikipediaapi.Wikipedia(
    user_agent='KGCrimeExtractor/1.0 (email@studenti.uni.it)',
    language='it',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)

# Blacklist per escludere biografie pure (non criminali) e opere di finzione
BLACK_LIST_TERMS = [
    "film", "romanzo", "serie televisiva", "episodio", "miniserie", 
    "cinema", "fiction", "album", "brano", "cantante", "attore",
    "nato il", "nata il", "politico", "deputato", "giornalista", 
    "avvocato", "magistrato"
]

def is_valid_crime_case(page) -> bool:
    """Filtra le pagine per isolare solo i casi di cronaca o i criminali."""
    testo = page.summary.lower()
    categorie = [c.lower() for c in page.categories.keys()]
    
    # 1. Scarta le pagine troppo corte (stub)
    if len(page.text) < 500:
        return False
        
    # 2. Controllo Blacklist nel testo introduttivo
    if any(term in testo for term in BLACK_LIST_TERMS):
        return False
        
    # 3. Controllo Categorie per evitare politici, finzione, ecc.
    cat_blacklist = ["film", "romanzi", "televisione", "deputati", "politici", "nati nel", "morti nel", "sport", "calcio"]
    if any(bad_cat in cat for cat in categorie for bad_cat in cat_blacklist):
        return False
        
    return True

def estrai_tutto_ricorsivo(nome_categoria: str, visited_cats=None, dataset_dict=None):
    """Esplora ricorsivamente tutte le sottocategorie e salva le pagine valide."""
    if visited_cats is None:
        visited_cats = set()
    if dataset_dict is None:
        dataset_dict = {}

    # Standardizza il prefisso
    if not nome_categoria.startswith("Categoria:"):
        cat_full_name = f"Categoria:{nome_categoria}"
    else:
        cat_full_name = nome_categoria

    # Previene i loop infiniti
    if cat_full_name in visited_cats:
        return dataset_dict
        
    visited_cats.add(cat_full_name)
    print(f"\n[esplorazione] {cat_full_name} | Trovati finora: {len(dataset_dict)}")
    
    try:
        cat = wiki_wiki.page(cat_full_name)
        
        for c in cat.categorymembers.values():
            if c.ns == wikipediaapi.Namespace.CATEGORY:
                # Esclude sottocategorie non pertinenti (politica, storia, intrattenimento), mantenendo quelle relative ai crimini
                cat_lower = c.title.lower()
                if any(x in cat_lower for x in ["deputati", "politici", "partito", "storia", "film", "musica", "calcio", "romanzi"]):
                    continue # Salta questa sottocategoria
                    
                estrai_tutto_ricorsivo(c.title, visited_cats, dataset_dict)
                
            elif c.ns == wikipediaapi.Namespace.MAIN:
                # Se è una pagina standard, elaborala
                page_id = c.title.replace(" ", "_").lower()
                
                # Evita di scaricare e filtrare pagine già processate
                if page_id not in dataset_dict and is_valid_crime_case(c):
                    dataset_dict[page_id] = {
                        "id": page_id,
                        "title": c.title,
                        "text": c.text,
                        "url": c.fullurl
                    }
                    print(f"  + Aggiunto: {c.title}")
                    time.sleep(0.1) 
                    
    except Exception as e:
        print(f"Errore durante l'accesso a {cat_full_name}: {e}")
        
    return dataset_dict

if __name__ == "__main__":
    print("Avvio crawler Wikipedia...")
    dataset_finale = estrai_tutto_ricorsivo("Casi_di_omicidio_in_Italia")
    
    dataset_list = list(dataset_finale.values())
    
    # 1. Crea la cartella se non esiste
    os.makedirs("data/raw", exist_ok=True)
    
    # 2. Salva il file
    with open("data/raw/dataset_cronaca_completo.json", "w", encoding="utf-8") as f:
        json.dump(dataset_list, f, indent=4, ensure_ascii=False)
        
    print(f"\nEstrazione completata! Totale casi unici estratti: {len(dataset_list)}")