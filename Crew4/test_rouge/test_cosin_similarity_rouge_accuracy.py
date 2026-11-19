import json
import os
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rouge_score import rouge_scorer



#TEST SULL'ACCURACY DI RECUPERO DELLE QUERY GENERATE PER ENTRAMBI I GRAFI
# E APPLICAIONE COSIN SIMILARITY E ROUGE TRA QUERY GENERATE E OTTIMALI PER ENTRAMBI I GRAFICI

BASE_DIR = os.path.join("Crew4", "test_rouge")
OUTPUT_DIR = os.path.join(BASE_DIR, "risultati2")


# crea la cartella risultati se non esiste
os.makedirs(OUTPUT_DIR, exist_ok=True)


SCENARI = {
    "React_Parte1": os.path.join(BASE_DIR, "dati_query_react1.json"),
    "React_Parte2": os.path.join(BASE_DIR, "dati_query_react2.json"), 
    "LLM_Pydantic_Parte1": os.path.join(BASE_DIR, "dati_query_llm1.json"),
    "LLM_Pydantic_Parte2": os.path.join(BASE_DIR, "dati_query_llm2.json")
}
# Inizializzatore per ROUGE (ROUGE-1, ROUGE-2 per ROUGE-N, e ROUGE-L)
scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=False)

def calcola_coseno(testo1, testo2):
    """Calcola la similarità del coseno tra due stringhe usando TF-IDF."""
    if not testo1 or not testo2:
        return 0.0
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([testo1, testo2])
        return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except ValueError:
        # Gestisce il caso in cui il vocabolario sia vuoto
        return 0.0

def safe_int(value):
    """Converte un valore in intero in modo sicuro (gestisce stringhe sporche)."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

# --------------------------=---------------
# FUNZIONE PRINCIPALE DI ELABORAZIONE
# ----------------------------------------
def elabora_scenario(nome_scenario, file_json):
    if not os.path.exists(file_json):
        print(f"File non trovato per {nome_scenario}: {file_json}")
        return

    with open(file_json, 'r', encoding='utf-8') as f:
        dati = json.load(f)

    report_sintassi = []
    report_accuracy = []

    # Variabili per calcolare le medie
    somma_coseno = somma_r1 = somma_r2 = somma_rl = somma_accuracy = somma_nlg = 0
    tot_query = len(dati)

    for item in dati:
        id_query = item.get("id", "N/D")
        livello = item.get("livello", "N/D")
        
        # 1. METRICHE DI SINTASSI E TESTO (Cypher Ottimale vs Cypher Generato)
        cypher_ottimale = item.get("cypher_ottimale", "")
        cypher_generato = item.get("cypher_generato", "")
        
        coseno = calcola_coseno(cypher_ottimale, cypher_generato)
        punteggi_rouge = scorer.score(cypher_ottimale, cypher_generato)
        
        r1 = punteggi_rouge['rouge1'].fmeasure
        r2 = punteggi_rouge['rouge2'].fmeasure
        rl = punteggi_rouge['rougeL'].fmeasure

        report_sintassi.append({
            "ID": id_query,
            "Livello": livello,
            "Coseno": round(coseno, 4),
            "ROUGE-1": round(r1, 4),
            "ROUGE-2": round(r2, 4),
            "ROUGE-L": round(rl, 4)
        })

        somma_coseno += coseno
        somma_r1 += r1
        somma_r2 += r2
        somma_rl += rl

        # 2. METRICHE DI RECUPERO (Accuracy e NLG Completeness)
        attesi = safe_int(item.get("numero_risultati_attesi", 0))
        ottenuti = safe_int(item.get("numero_risultati_ottenuti_query", 0))
        llm_risposti = safe_int(item.get("numero_risultati_in_risposta_llm", 0))

        # Accuracy di Recupero (Rapporto normalizzato [0,1])
        accuracy = min(1.0, ottenuti / attesi) if attesi > 0 else 0.0
        
        # NLG Completeness (Quanti dei risultati estratti l'LLM ha effettivamente scritto nel testo?)
        nlg_completeness = min(1.0, llm_risposti / ottenuti) if ottenuti > 0 else 0.0

        report_accuracy.append({
            "ID": id_query,
            "Livello": livello,
            "Risultati_Attesi": attesi,
            "Risultati_Ottenuti_Da_Query": ottenuti,
            "Accuracy_Recupero": round(accuracy, 4),
            "Risultati_Risposta_LLM": llm_risposti,
            "NLG_Completeness": round(nlg_completeness, 4)
        })

        somma_accuracy += accuracy
        somma_nlg += nlg_completeness

    # Calcolo Medie
    medie = {
        "Coseno": round(somma_coseno / tot_query, 4) if tot_query > 0 else 0,
        "ROUGE-1": round(somma_r1 / tot_query, 4) if tot_query > 0 else 0,
        "ROUGE-2": round(somma_r2 / tot_query, 4) if tot_query > 0 else 0,
        "ROUGE-L": round(somma_rl / tot_query, 4) if tot_query > 0 else 0,
        "Accuracy_Recupero": round(somma_accuracy / tot_query, 4) if tot_query > 0 else 0,
        "NLG_Completeness": round(somma_nlg / tot_query, 4) if tot_query > 0 else 0
    }

    # =-------------------------------------------
    # SALVATAGGIO DEI FILE CSV
    # --------------------------------------------
    # File 1: Sintassi
    path_sintassi = os.path.join(OUTPUT_DIR, f"{nome_scenario}_Sintassi_ROUGE_Coseno.csv")
    with open(path_sintassi, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["ID", "Livello", "Coseno", "ROUGE-1", "ROUGE-2", "ROUGE-L"])
        writer.writeheader()
        writer.writerows(report_sintassi)

    # File 2: Accuracy
    path_accuracy = os.path.join(OUTPUT_DIR, f"{nome_scenario}_Accuracy_Retrieval.csv")
    with open(path_accuracy, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["ID", "Livello", "Risultati_Attesi", "Risultati_Ottenuti_Da_Query", "Accuracy_Recupero", "Risultati_Risposta_LLM", "NLG_Completeness"])
        writer.writeheader()
        writer.writerows(report_accuracy)

    # Stampa Riassunto a schermo per la Tesi
    print(f"\n{'='*50}")
    print(f"REPORT MEDIE: {nome_scenario}")
    print(f"{'='*50}")
    print(f" 🔹 Similarità Coseno : {medie['Coseno']}")
    print(f" 🔹 ROUGE-1           : {medie['ROUGE-1']}")
    print(f" 🔹 ROUGE-L           : {medie['ROUGE-L']}")
    print(f" 🔸 Accuracy Recupero : {medie['Accuracy_Recupero']}")
    print(f" 🔸 NLG Completeness  : {medie['NLG_Completeness']}")
    print(f" -> Salvati 2 file CSV in: {OUTPUT_DIR}\n")

# ==========================================
# ESECUZIONE
# ==========================================
if __name__ == "__main__":
    print("Inizio elaborazione metriche...\n")
    for scenario, file_path in SCENARI.items():
        elabora_scenario(scenario, file_path)
    print("Tutte le metriche sono state elaborate e salvate con successo.")