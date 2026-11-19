"""
Script di Valutazione Sperimentale Completo per la Crew 3.
Confronta 20 nodi definiti e 20 nodi casuali.
Valuta l'approccio che punta sulla Knowledge dell'LLM e la pipeline dell'agente
Salva metriche, tabelle CSV e grafici a doppio pannello.
"""

import os
import sys
import time
import random
import json
import re
import requests
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from neo4j import GraphDatabase
from crewai import Agent, Crew, Process, Task

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Crew3.agents_crew3 import agente_ricercatore_lod, llm_gemini
from Crew3.tasks_crew3 import task_ricerca_wikidata
from Crew3.tools_crew3 import interroga_wikidata_sparql, ispeziona_qid

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

QID_RE = re.compile(r"^Q\d+$")

# ---------------------------------------------------------------------------------
# 1. CAMPIONI (20 DEFINITI + 20 CASUALI)
# ---------------------------------------------------------------------------------

def recupera_nodi_definiti(per_classe: int = 5) -> list[dict]:
    target_per_classe = {
        "Person": ["Marta Russo", "Simonetta Cesaroni", "Chiara Poggi", "Annamaria Franzoni", "Patrick Lumumba", "Francesco Coco"],
        "Case": ["Delitto di Cogne", "Delitto di Garlasco", "Delitto di Novi Ligure", "Mistero di via Monaci", "Omicidio di Alessandro Floris"],
        "Weapon": ["Coltello da cucina", "Beretta 92", "Kalašnikov", "trapano", "Beretta 7,65 mod. 70"],
        "Location": ["Cogne", "Garlasco", "Testaccio", "Formello", "Calabria"]
    }
    nodi_finali = []
    try:
        with driver.session() as session:
            for label, nomi in target_per_classe.items():
                trovati = []
                for nome in nomi:
                    if len(trovati) >= per_classe:
                        break
                    query = f"""
                    MATCH (n:{label})
                    WHERE toLower(trim(n.name)) = toLower($nome)
                    RETURN n.id AS id, n.name AS name, '{label}' AS label LIMIT 1
                    """
                    res = session.run(query, nome=nome).single()
                    if res:
                        trovati.append({"id": res["id"], "name": res["name"], "label": res["label"]})
                nodi_finali.extend(trovati)
    except Exception as e:
        print(f"[DB ERROR] {e}")
    return nodi_finali

def recupera_nodi_casuali(per_classe: int = 5, seed: int = 42) -> list[dict]:
    random.seed(seed)
    classi = ["Person", "Case", "Weapon", "Location"]
    esclusi = {
        "Person": ["Marta Russo", "Simonetta Cesaroni", "Chiara Poggi", "Annamaria Franzoni", "Patrick Lumumba", "Francesco Coco"],
        "Case": ["Delitto di Cogne", "Delitto di Garlasco", "Delitto di Novi Ligure", "Mistero di via Monaci", "Omicidio di Alessandro Floris"],
        "Weapon": ["Coltello da cucina", "Beretta 92", "Kalašnikov", "trapano", "Beretta 7,65 mod. 70"],
        "Location": ["Cogne", "Garlasco", "Testaccio", "Formello", "Calabria"]
    }
    nodi_finali = []
    try:
        with driver.session() as session:
            for label in classi:
                query = f"""
                MATCH (n:{label})
                WHERE n.name IS NOT NULL AND trim(n.name) <> "" AND NOT n.name IN $escl
                RETURN DISTINCT n.id AS id, n.name AS name, '{label}' AS label
                """
                res = session.run(query, escl=esclusi.get(label, []))
                cand = [{"id": r["id"], "name": r["name"], "label": r["label"]} for r in res]
                cand.sort(key=lambda x: str(x["name"]))
                scelti = random.sample(cand, min(per_classe, len(cand)))
                nodi_finali.extend(scelti)
    except Exception as e:
        print(f"[DB ERROR] {e}")
    return nodi_finali

# -----------------------------------------------------------------------------
# 2. METODI DI RISOLUZIONE
# -----------------------------------------------------------------------------

def cerca_qid_wikidata(nome_entita: str) -> str | None:
    url = "https://www.wikidata.org/w/api.php"
    params = {"action": "wbsearchentities", "format": "json", "language": "it", "search": nome_entita}
    try:
        resp = requests.get(url, params=params, headers={"User-Agent": "GraceMultiAgent/1.0"}, timeout=15)
        data = resp.json()
        if data.get("search"):
            return data["search"][0]["id"]
    except Exception:
        pass
    return None

def metodo_a_llm_sparql(nodo_id: str, nodo_nome: str, nodo_label: str) -> str | None:
    prompt = f"""
    Trova il Q-ID di Wikidata per questa entità:
    ID: "{nodo_id}" | Nome: "{nodo_nome}" | Tipo: "{nodo_label}"
    Scrivi una query SPARQL SELECT per trovare l'item. Restituisci ESCLUSIVAMENTE la query.
    """
    try:
        raw = llm_gemini.call([{"role": "user", "content": prompt}]).strip()
        q_sparql = raw.replace("```sparql", "").replace("```", "").strip()
        res_raw = interroga_wikidata_sparql.run(query=q_sparql)
        if "Errore" in res_raw or res_raw == "[]":
            return None
        res_list = eval(res_raw)
        if res_list:
            for k in res_list[0]:
                val = res_list[0][k].get("value", "")
                if "/entity/Q" in val:
                    return val.split("/entity/")[-1]
    except Exception:
        pass
    return None

def build_crew3_evaluator() -> Crew:
    # Task modificato per costringere l'agente a usare Ispeziona_Wikidata_QID e restituire esplicitamente il flag semantic_shift
    task_valutazione = Task(
        description="""
        Hai ricevuto l'entità "{nome_entita}" (Label nel Knowledge Graph locale: "{label_entita}") associata al Q-ID: {q_id}.
        
        STEP 1: Usa OBBLIGATORIAMENTE il tool 'Ispeziona_Wikidata_QID' passando il Q-ID {q_id} per verificarne etichetta, descrizione e classe (P31).
        STEP 2: Valuta se l'entità trovata su Wikidata è semanticamente coerente con la label attesa ("{label_entita}"). 
        - Se c'è un'incompatibilità evidente (es. una persona associata a un istituto o a un evento estraneo, o un luogo che punta a un'altra categoria errata), considera che si tratta di un "Semantic Shift".
        
        Restituisci un blocco JSON valido con questa struttura esatta:
        Se c'è semantic shift: {"trovato": false, "semantic_shift": true, "reason": "spiegazione"}
        Se è coerente e valido: {"wikidata_id": "{q_id}", "semantic_shift": false, "status": "valido"}
        """,
        expected_output='Un JSON valido contenente la chiave "semantic_shift" (true o false).',
        agent=agente_ricercatore_lod
    )
    return Crew(agents=[agente_ricercatore_lod], tasks=[task_valutazione], process=Process.sequential, verbose=False)

def parse_json(text: str):
    m = re.search(r"\{.*\}", str(text), re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None

# -----------------------------------------------------------------------------------
# 3. ESECUZIONE BENCHMARK
# ----------------------------------------------------------------------------------

def esegui_test_suite(nodi: list[dict], nome_test: str, cartella_out: str):
    print("=" * 75)
    print(f" ESECUZIONE TEST SUITE: {nome_test.upper()} (N={len(nodi)})")
    print("=" * 75)

    crew3_eval = build_crew3_evaluator()

    stats = {
        "totale": len(nodi),
        "successo_a": 0,
        "successo_b": 0,
        "semantic_shift_rilevati_agente": 0,
        "semantic_shift_reali": 0
    }

    ontologia_reale = {
        "Person": ["umano", "human", "essere umano", "donna", "uomo", "persona", "politico"],
        "Location": ["comune", "città", "frazione", "luogo", "stato", "regione", "edificio", "strada", "via"],
        "Weapon": ["arma", "pistola", "coltello", "weapon", "fucile", "firearm", "tool"],
        "Case": ["omicidio", "delitto", "caso", "processo", "strage", "murder", "crime"]
    }

    for idx, n in enumerate(nodi, 1):
        nid, name, label = n["id"], n["name"], n["label"]
        print(f"\n[{idx}/{len(nodi)}] Entità: '{name}' ({label})")

        # Metodo A
        qid_a = metodo_a_llm_sparql(nid, name, label)
        if qid_a:
            stats["successo_a"] += 1
            print(f"  -> Metodo A (LLM + SPARQL) : [MATCH] {qid_a}")
        else:
            print(f"  -> Metodo A (LLM + SPARQL) : [MISS]")

        # Metodo B / Crew3 (API Fuzzy)
        qid_b = cerca_qid_wikidata(name)
        if qid_b:
            stats["successo_b"] += 1
            print(f"  -> Metodo B (API Fuzzy / Crew3) : [MATCH] {qid_b}")

            # Interrogazione dell'agente con il tool Ispeziona_QID
            try:
                res_crew = crew3_eval.kickoff(inputs={"nome_entita": name, "label_entita": label, "q_id": qid_b})
                dati = parse_json(res_crew) or {}
                
                # Rilevamento basato sul verdetto dell'agente
                is_shift_agente = dati.get("semantic_shift") is True
                if is_shift_agente:
                    stats["semantic_shift_rilevati_agente"] += 1
                    print("     [VERDETTO AGENTE] Semantic Shift RILEVATO.")
                else:
                    print("     [VERDETTO AGENTE] Entità COERENTE.")

                # Ground Truth Reale per confronto
                q_isp = f"SELECT ?tipoLabel WHERE {{ wd:{qid_b} wdt:P31 ?tipo . SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'it,en'. }} }}"
                res_isp = interroga_wikidata_sparql.run(query=q_isp)
                tipo_str = res_isp.lower()
                
                attesi = ontologia_reale.get(label, [])
                match_reale = any(kw in tipo_str for kw in attesi) if attesi else True
                if not match_reale:
                    stats["semantic_shift_reali"] += 1
                    print(f"     [GROUND TRUTH] Shift reale confermato (Wikidata P31: {tipo_str})")

            except Exception as e:
                print(f"     [ERROR] Errore esecuzione agent evaluation: {e}")
        else:
            print(f"  -> Metodo B (API Fuzzy / Crew3) : [MISS]")

        time.sleep(2)

    genera_report_e_grafici(stats, nome_test, cartella_out)

def genera_report_e_grafici(stats: dict, titolo: str, cartella: str):
    os.makedirs(cartella, exist_ok=True)
    tot = stats["totale"]
    succ_a = stats["successo_a"]
    succ_b = stats["successo_b"]
    shift_agente = stats["semantic_shift_rilevati_agente"]
    shift_reali = stats["semantic_shift_reali"]

    cov_a = (succ_a / tot * 100) if tot > 0 else 0
    cov_b = (succ_b / tot * 100) if tot > 0 else 0
    
    val_b = succ_b - shift_agente
    net_b_pct = (val_b / tot * 100) if tot > 0 else 0
    shift_rate_agente_pct = (shift_agente / succ_b * 100) if succ_b > 0 else 0

    df = pd.DataFrame({
        "Metrica": [
            "Coverage Metodo A (LLM + SPARQL)",
            "Coverage Metodo B (API Fuzzy / Crew3 Totale)",
            "Coverage Metodo B Netto (Validati dall'Agente)",
            "Semantic Shift Rilevati dall'Agente",
            "Semantic Shift Reali (Ground Truth)"
        ],
        "Valore Assoluto": [
            f"{succ_a}/{tot}", f"{succ_b}/{tot}", f"{val_b}/{tot}", f"{shift_agente}/{succ_b}", f"{shift_reali}/{succ_b}"
        ],
        "Percentuale": [
            f"{cov_a:.2f}%", f"{cov_b:.2f}%", f"{net_b_pct:.2f}%", f"{shift_rate_agente_pct:.2f}%", f"{(shift_reali/succ_b*100 if succ_b>0 else 0):.2f}%"
        ]
    })
    
    csv_path = os.path.join(cartella, "risultati_valutazione.csv")
    df.to_csv(csv_path, index=False)
    print(f"\nTabella salvata in: {csv_path}")
    print(df.to_markdown(index=False))

    # Grafico a Doppio Pannello
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.5), dpi=300, gridspec_kw={'width_ratios': [1.8, 1]})

    labels_l = ['Metodo A\n(LLM + SPARQL)', 'Metodo B\n(Totale Estratti)', 'Metodo B\n(Netto Validi)']
    vals_l = [cov_a, cov_b, net_b_pct]
    counts_l = [f"{succ_a}/{tot}", f"{succ_b}/{tot}", f"{val_b}/{tot}"]
    cols_l = ['#E08250', '#4C72B0', '#55A868']

    bars1 = ax1.bar(labels_l, vals_l, color=cols_l, width=0.52)
    ax1.set_ylim(0, 108)
    ax1.set_ylabel(f'Percentuale sul Campione (N={tot})', fontweight='bold')
    ax1.set_title(f'A) Entity Coverage ({titolo})', fontweight='bold', pad=12)
    ax1.grid(axis='y', linestyle='--', alpha=0.4)
    ax1.set_axisbelow(True)

    for b, v, c in zip(bars1, vals_l, counts_l):
        ax1.text(b.get_x() + b.get_width()/2, v + 2, f'{v:.2f}%\n({c})', ha='center', va='bottom', fontsize=9.5, fontweight='bold')

    valid_b_rate = ((succ_b - shift_agente) / succ_b * 100) if succ_b > 0 else 0
    labels_r = ['Validi\n(Coerenti)', 'Semantic Shift\n(Rilevati)']
    vals_r = [valid_b_rate, shift_rate_agente_pct]
    counts_r = [f"{val_b}/{succ_b}", f"{shift_agente}/{succ_b}"]
    cols_r = ['#55A868', '#C44E52']

    bars2 = ax2.bar(labels_r, vals_r, color=cols_r, width=0.48)
    ax2.set_ylim(0, 108)
    ax2.set_ylabel(f'Percentuale sugli Estratti B (N={succ_b})', fontweight='bold')
    ax2.set_title(f'B) Qualità e Semantic Shift', fontweight='bold', pad=12)
    ax2.grid(axis='y', linestyle='--', alpha=0.4)
    ax2.set_axisbelow(True)

    for b, v, c in zip(bars2, vals_r, counts_r):
        ax2.text(b.get_x() + b.get_width()/2, v + 2, f'{v:.2f}%\n({c})', ha='center', va='bottom', fontsize=9.5, fontweight='bold')

    plt.suptitle(f'Valutazione Sperimentale Crew 3 - {titolo}', fontsize=12.5, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    img_path = os.path.join(cartella, "grafico_valutazione.png")
    plt.savefig(img_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Grafico salvato in: {img_path}\n")

if __name__ == "__main__":
    print("\n" + "#" * 75)
    print(" SUITE DI VALUTAZIONE SPERIMENTALE: DEFINITI (N=20) VS CASUALI (N=20)")
    print("#" * 75 + "\n")

    nodi_def = recupera_nodi_definiti(per_classe=5)
    if nodi_def:
        esegui_test_suite(nodi_def, "20 Nodi Definiti", "risultati_definiti_eval")

    nodi_cas = recupera_nodi_casuali(per_classe=5, seed=42)
    if nodi_cas:
        esegui_test_suite(nodi_cas, "20 Nodi Casuali", "risultati_casuali_eval")