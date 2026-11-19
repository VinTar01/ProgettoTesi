import os
import pandas as pd

# ==========================================
# CONFIGURAZIONE DEI PERCORSI
# ==========================================
# Definiamo la cartella di lavoro dei test rouge
BASE_DIR = os.path.join("Crew4", "test_rouge", "risultati")
OUTPUT_DIR = os.path.join(BASE_DIR, "risultati")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def unifica_e_analizza(parte1_nome, parte2_nome, nome_output):
    path_1 = os.path.join(BASE_DIR, parte1_nome)
    path_2 = os.path.join(BASE_DIR, parte2_nome)
    path_output = os.path.join(OUTPUT_DIR, nome_output)

    if not os.path.exists(path_1) or not os.path.exists(path_2):
        print(f"Impossibile trovare i file {parte1_nome} o {parte2_nome} in {BASE_DIR}")
        return

    # 1. Caricamento dei file CSV
    df1 = pd.read_csv(path_1)
    df2 = pd.read_csv(path_2)

    # 2. Unificazione
    df_unito = pd.concat([df1, df2], ignore_index=True)

    # 3. Ordinamento logico per ID (EASY -> MEDIUM -> HARD)
    def sort_key(row_id):
        parts = str(row_id).split('_')
        prefix = parts[0]
        try:
            num = int(parts[1])
        except (IndexError, ValueError):
            num = 0
        prefix_order = {'EASY': 1, 'MEDIUM': 2, 'HARD': 3}
        return (prefix_order.get(prefix, 4), num)

    df_unito['sort_key'] = df_unito['ID'].apply(sort_key)
    df_unito = df_unito.sort_values('sort_key').drop(columns=['sort_key']).reset_index(drop=True)

    # 4. Salvataggio del file unificato
    df_unito.to_csv(path_output, index=False, encoding='utf-8')

    # 5. Calcolo dei totali e delle medie corrette
    tot_attesi = df_unito['Risultati_Attesi'].sum()
    tot_ottenuti = df_unito['Risultati_Ottenuti_Da_Query'].sum()
    media_accuracy = df_unito['Accuracy_Recupero'].mean()
    media_completeness = df_unito['NLG_Completeness'].mean()

    # 6. Output a schermo dei risultati
    print("=" * 60)
    print(f"REPORT RIEPILOGATIVO UNIFICATO: {nome_output}")
    print("=" * 60)
    print(f" 🔹 Totale Complessivo Risultati Attesi       : {tot_attesi}")
    print(f" 🔹 Totale Complessivo Risultati Ottenuti     : {tot_ottenuti}")
    print(f" 🔸 Media Complessiva Accuracy di Recupero    : {media_accuracy:.4f} (~{media_accuracy*100:.2f}%)")
    print(f" 🔸 Media Complessiva NLG Completeness        : {media_completeness:.4f} (~{media_completeness*100:.2f}%)")
    print(f" Salvato con successo in: {path_output}\n")

if __name__ == "__main__":
    print("Inizio unificazione dei dataset Accuracy & Retrieval...\n")
    
    # Unificazione per LLM + Pydantic
    unifica_e_analizza(
        "LLM_Pydantic_Parte1_Accuracy_Retrieval.csv", 
        "LLM_Pydantic_Parte2_Accuracy_Retrieval.csv", 
        "LLM_Pydantic_Unificato_Accuracy_Retrieval.csv"
    )

    # Unificazione per ReAct
    unifica_e_analizza(
        "React_Parte1_Accuracy_Retrieval.csv", 
        "React_Parte2_Accuracy_Retrieval.csv", 
        "React_Unificato_Accuracy_Retrieval.csv"
    )