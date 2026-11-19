import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt

# Configurazione dei percorsi dinamici
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Directory 'evaluation'
EXTRACTION_DIR = os.path.abspath(os.path.join(BASE_DIR, "..")) # Torna a 'Extraction_versions'





#SFRUTTA GLI OUTPUT DEI TEST DI OGNI VERSIONE PER GENERARE I GRAFICI DELLE  RUN DI OGNUNA

PIPELINES = [
    "Pure_LLM", 
    "Pydantic_Only", 
    "ReAct_Only", 
    "ReAct_Pydantic(Crew1)"
]

def genera_grafici_locali():
    print("="*80)
    print(" GENERAZIONE GRAFICI DI STABILITÀ SULLE 10 RUN ")
    print("="*80)
    
    for pipe_name in PIPELINES:
        bench_dir = os.path.join(EXTRACTION_DIR, pipe_name, "benchmark_results")
        csv_path = os.path.join(bench_dir, "serie_storica_10_run.csv")
        
        if not os.path.exists(csv_path):
            print(f"[SKIP] File serie storica non trovato per la pipeline: {pipe_name}\n(Percorso cercato: {csv_path})")
            continue
            
        # Lettura dello storico delle 10 run
        df = pd.read_csv(csv_path)
        
        # Pulizia dell'asse X (trasforma "Run_1" in 1)
        x_labels = df["Run"].str.replace("Run_", "").astype(int)
        
        # ---------------------------------------------------------
        # GRAFICO 1: Andamento F1-Score 
        # ---------------------------------------------------------
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Tarccia e metriche principali garantite
        if "F1_Entita" in df.columns:
            ax.plot(x_labels, df["F1_Entita"], marker='o', label="F1 Entità", color="#4C72B0", linewidth=2.5)
        if "F1_Relazioni" in df.columns:
            ax.plot(x_labels, df["F1_Relazioni"], marker='s', label="F1 Relazioni", color="#DD8452", linewidth=2.5)
        
        # Traccia Precision e Recall secondarie solo se presenti nel CSV
        optional_metrics = [
            ("Precision_Entita", "#4C72B0", "Precision Entità", '--'),
            ("Recall_Entita", "#4C72B0", "Recall Entità", ':'),
            ("Precision_Relazioni", "#DD8452", "Precision Relazioni", '--'),
            ("Recall_Relazioni", "#DD8452", "Recall Relazioni", ':')
        ]
        
        for col, color, lbl, ls in optional_metrics:
            if col in df.columns:
                ax.plot(x_labels, df[col], marker='.', color=color, linewidth=1, linestyle=ls, alpha=0.5, label=lbl)
        
        ax.set_title(f'Andamento Accuratezza nelle 10 Run - {pipe_name}', fontsize=14, pad=15)
        ax.set_xlabel('Numero Run', fontsize=12)
        ax.set_ylabel('Score (0.0 - 1.0)', fontsize=12)
        ax.set_ylim(0, 1.05)
        ax.set_xticks(x_labels)
        ax.grid(True, linestyle='--', alpha=0.6)
        
        ax.legend(loc='lower left', bbox_to_anchor=(1.02, 0), borderaxespad=0.)
        
        out_path_f1 = os.path.join(bench_dir, "grafico_andamento_f1.png")
        plt.tight_layout()
        plt.savefig(out_path_f1, dpi=300, bbox_inches="tight")
        plt.close()
        
        # ---------------------------------------------------------
        # GRAFICO 2: Andamento Costi (Tempo vs Token)
        # ---------------------------------------------------------
        if "Tempo_Medio_s" in df.columns and "Token_Medi" in df.columns:
            fig, ax1 = plt.subplots(figsize=(10, 6))
            
            color_time = '#55A868' # Verde
            ax1.set_title(f'Andamento Costi Computazionali nelle 10 Run - {pipe_name}', fontsize=14, pad=15)
            ax1.set_xlabel('Numero Run', fontsize=12)
            ax1.set_ylabel('Tempo Medio per Caso (secondi)', color=color_time, fontsize=12)
            ax1.plot(x_labels, df["Tempo_Medio_s"], marker='o', color=color_time, label="Tempo (s)", linewidth=2.5)
            ax1.tick_params(axis='y', labelcolor=color_time)
            ax1.set_xticks(x_labels)
            ax1.grid(True, linestyle='--', alpha=0.6)
            
            ax2 = ax1.twinx()  
            color_tok = '#C44E52' # Rosso scuro
            ax2.set_ylabel('Token Medi Consumati', color=color_tok, fontsize=12)
            ax2.plot(x_labels, df["Token_Medi"], marker='s', color=color_tok, label="Token", linewidth=2.5, linestyle='-.')
            ax2.tick_params(axis='y', labelcolor=color_tok)
            
            lines_1, labels_1 = ax1.get_legend_handles_labels()
            lines_2, labels_2 = ax2.get_legend_handles_labels()
            ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right')
            
            out_path_costi = os.path.join(bench_dir, "grafico_andamento_costi.png")
            plt.tight_layout()
            plt.savefig(out_path_costi, dpi=300)
            plt.close()
        
        print(f"[OK] Grafici salvati con successo per: {pipe_name}")
        print(f"     -> {out_path_f1}\n")

if __name__ == "__main__":
    genera_grafici_locali()