import os
import sys
import json
import time
import re
from typing import Dict, List, Tuple, Set

import pandas as pd
import numpy as np
from rapidfuzz import fuzz
from dotenv import load_dotenv

# Configurazione percorsi
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
sys.path.append(ROOT_DIR)

load_dotenv(os.path.join(ROOT_DIR, ".env"))

# Import specifici del progetto (Prompt, CrewAI e Schemi)
try:
    from Extraction_versions.prompt import PROMPT_BASE
except ImportError:
    from Extraction_versions.prompt import PROMPT_BASE_EN as PROMPT_BASE

from schemas import SchemaGrafo
from crewai import Crew, Process, Agent, LLM, Task
from crewai.tools import BaseTool
from pydantic import Field

# Costanti
SIMILARITY_THRESHOLD = 80.0
TOTAL_RUNS = 10
GOLD_DIR = os.path.join(ROOT_DIR, "Extraction_versions", "gold_standard")
DATASET_PATH = os.path.join(ROOT_DIR, "data", "raw", "dataset_cronaca_completo.json")
BENCH_DIR = os.path.join(BASE_DIR, "benchmark_results")
os.makedirs(BENCH_DIR, exist_ok=True)

class BenchmarkCaseReaderTool(BaseTool):
    name: str = "read_case_document"
    description: str = "Use this tool to read the text of a true crime case."
    dataset_dict: dict = Field(..., description="Dizionario dei casi")
    
    def _run(self, title: str) -> str:
        t_clean = title.lower().strip()
        for cid, caso in self.dataset_dict.items():
            if caso.get("title", "").lower().strip() == t_clean or cid.lower() == t_clean: 
                return caso["text"]
        return "Error: Case not found."

def get_crew_tokens(crew_obj) -> Tuple[int, int]:
    metrics = getattr(crew_obj, 'usage_metrics', None)
    if not metrics: 
        return 0, 0
    if isinstance(metrics, dict): 
        return metrics.get('prompt_tokens', 0), metrics.get('completion_tokens', 0)
    return getattr(metrics, 'prompt_tokens', 0), getattr(metrics, 'completion_tokens', 0)

def clean_and_parse_json(raw_text: str) -> dict:
    txt = raw_text.strip()
    if txt.startswith("```json"): txt = txt[7:]
    if txt.startswith("```"): txt = txt[3:]
    if txt.endswith("```"): txt = txt[:-3]
    match = re.search(r'(\{[\s\S]*\})', txt.strip())
    return json.loads(match.group(1)) if match else json.loads(txt.strip())

def normalize_text(text: str) -> str:
    if not text: return ""
    text = re.sub(r'[^\w\s]', '', text.lower().strip())
    return " ".join(text.split())

def evaluate_pred_vs_gold(gold_data: dict, pred_data: dict):
    gold_ents = gold_data.get("entities", [])
    pred_ents = pred_data.get("entities", [])
    
    used_p_ents = set()
    tp_ent = 0
    for g in gold_ents:
        g_lbl = g.get("label", "")
        g_nm = normalize_text(g.get("name", ""))
        for idx, p in enumerate(pred_ents):
            if idx in used_p_ents: continue
            if p.get("label", "") == g_lbl and fuzz.token_sort_ratio(g_nm, normalize_text(p.get("name", ""))) >= SIMILARITY_THRESHOLD:
                used_p_ents.add(idx)
                tp_ent += 1
                break
    fp_ent = len(pred_ents) - len(used_p_ents)
    fn_ent = len(gold_ents) - tp_ent
    p_ent = tp_ent / (tp_ent + fp_ent) if (tp_ent + fp_ent) else 0.0
    r_ent = tp_ent / (tp_ent + fn_ent) if (tp_ent + fn_ent) else 0.0
    f1_ent = 2 * (p_ent * r_ent) / (p_ent + r_ent) if (p_ent + r_ent) else 0.0

    id_map = {ent.get("id"): normalize_text(ent.get("name", "")) for ent in pred_ents if ent.get("id")}
    pred_rels = [(id_map.get(r.get("source_id"), ""), r.get("type", ""), id_map.get(r.get("target_id"), "")) for r in pred_data.get("relationships", [])]
    
    gold_id_map = {ent.get("id"): normalize_text(ent.get("name", "")) for ent in gold_ents if ent.get("id")}
    gold_rels = [(gold_id_map.get(r.get("source_id"), ""), r.get("type", ""), gold_id_map.get(r.get("target_id"), "")) for r in gold_data.get("relationships", [])]

    used_p_rels = set()
    tp_rel = 0
    for g_s, g_t, g_o in gold_rels:
        for idx, (p_s, p_t, p_o) in enumerate(pred_rels):
            if idx in used_p_rels: continue
            if g_t == p_t and fuzz.token_sort_ratio(g_s, p_s) >= SIMILARITY_THRESHOLD and fuzz.token_sort_ratio(g_o, p_o) >= SIMILARITY_THRESHOLD:
                used_p_rels.add(idx)
                tp_rel += 1
                break
    fp_rel = len(pred_rels) - len(used_p_rels)
    fn_rel = len(gold_rels) - tp_rel
    p_rel = tp_rel / (tp_rel + fp_rel) if (tp_rel + fp_rel) else 0.0
    r_rel = tp_rel / (tp_rel + fn_rel) if (tp_rel + fn_rel) else 0.0
    f1_rel = 2 * (p_rel * r_rel) / (p_rel + r_rel) if (p_rel + r_rel) else 0.0

    return (p_ent, r_ent, f1_ent, tp_ent, fp_ent, fn_ent), (p_rel, r_rel, f1_rel, tp_rel, fp_rel, fn_rel)

def df_to_markdown_safe(df: pd.DataFrame) -> str:
    try:
        return df.to_markdown(index=False)
    except Exception:
        headers = list(df.columns)
        lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
        for _, row in df.iterrows():
            lines.append("| " + " | ".join(str(val) for val in row.values) + " |")
        return "\n".join(lines)

def run_react_pydantic(case_title: str, dataset_mem: dict, max_retries=3) -> Tuple[dict, float, int, int]:
    total_elapsed = 0.0
    total_p_tok = 0
    total_c_tok = 0
    
    for attempt in range(1, max_retries + 1):
        start = time.time()
        try:
            reader = BenchmarkCaseReaderTool(dataset_dict=dataset_mem)
            gemini_llm = LLM(model="gemini/gemini-flash-lite-latest", temperature=0, api_key=os.environ.get("GEMINI_API_KEY"))
            agent = Agent(role="Analyst", goal="Extract KG", backstory="Analyst", tools=[reader], llm=gemini_llm, verbose=False)
            prompt = PROMPT_BASE.replace("{testo_caso}", f"Use read_case_document for '{case_title}'")
            task = Task(description=prompt, expected_output="JSON matching SchemaGrafo", agent=agent, output_json=SchemaGrafo)
            crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
            
            crew.kickoff()
            
            elapsed = time.time() - start
            total_elapsed += elapsed
            
            p_tok, c_tok = get_crew_tokens(crew)
            total_p_tok += p_tok
            total_c_tok += c_tok
            
            if task.output and getattr(task.output, 'json_dict', None):
                data = json.loads(task.output.json_dict) if isinstance(task.output.json_dict, str) else task.output.json_dict
            else:
                data = clean_and_parse_json(str(task.output.raw))
                
            if not isinstance(data, dict) or "entities" not in data: 
                raise ValueError("Schema non rispettato")
                
            return data, total_elapsed, total_p_tok, total_c_tok
        except Exception as e:
            elapsed = time.time() - start
            total_elapsed += elapsed
            try:
                p_tok, c_tok = get_crew_tokens(crew)
                total_p_tok += p_tok
                total_c_tok += c_tok
            except:
                pass
            print(f"      [ReAct_Pydantic - Tentativo {attempt}/{max_retries}] Errore: {e}")
            time.sleep(3)
            
    return {"entities": [], "relationships": []}, total_elapsed, total_p_tok, total_c_tok

def main():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        full_dataset = json.load(f)
    
    dataset_mem = {}
    for c in full_dataset:
        cid = c.get("id", "").strip().lower()
        title = c.get("title", "").strip().lower()
        dataset_mem[cid] = c
        dataset_mem[title] = c

    gold_cases = {}
    for f in os.listdir(GOLD_DIR):
        if f.endswith(".json"):
            cid = f[:-5].replace("gold_standard_", "").strip().lower()
            with open(os.path.join(GOLD_DIR, f), "r", encoding="utf-8") as gf:
                gold_cases[cid] = json.load(gf)

    print(f"Casi Gold Standard caricati per ReAct_Pydantic: {len(gold_cases)} ({list(gold_cases.keys())})")

    history_runs = []

    for run_idx in range(1, TOTAL_RUNS + 1):
        print(f"\n>> Esecuzione Run {run_idx}/{TOTAL_RUNS} (ReAct_Pydantic)...")
        
        run_rows = []
        run_times, run_tokens = [], []
        f1_e_list, f1_r_list = [], []
        p_e_list, r_e_list = [], []
        p_r_list, r_r_list = [], []

        for cid, g_data in gold_cases.items():
            caso = dataset_mem.get(cid)
            if not caso:
                for k, val in dataset_mem.items():
                    if cid in k or k in cid:
                        caso = val
                        break
            if not caso:
                continue

            title = caso.get("title", cid)
            data, elap, p_tok, c_tok = run_react_pydantic(title, dataset_mem)
            
            run_times.append(elap)
            run_tokens.append(p_tok + c_tok)

            (pe, re, f1e, tpe, fpe, fne), (pr, rr, f1r, tpr, fpr, fnr) = evaluate_pred_vs_gold(g_data, data)
            
            f1_e_list.append(f1e)
            f1_r_list.append(f1r)
            p_e_list.append(pe)
            r_e_list.append(re)
            p_r_list.append(pr)
            r_r_list.append(rr)

            run_rows.append({"Caso": f"{cid} (Entità)", "Precision": round(pe, 4), "Recall": round(re, 4), "F1-Score": round(f1e, 4), "TP": tpe, "FP": fpe, "FN": fne})
            run_rows.append({"Caso": f"{cid} (Relazioni)", "Precision": round(pr, 4), "Recall": round(rr, 4), "F1-Score": round(f1r, 4), "TP": tpr, "FP": fpr, "FN": fnr})

            print(f"  [{cid}] F1-Ent: {f1e:.3f} | F1-Rel: {f1r:.3f} | Tempo: {elap:.2f}s")
            time.sleep(2)

        # Salvataggio CSV ad ogni iterazione
        df_run = pd.DataFrame(run_rows)
        df_run.to_csv(os.path.join(BENCH_DIR, f"tabella_dettagliata_run_{run_idx}.csv"), index=False)

        if run_idx == 1:
            avg_t_r1 = float(np.mean(run_times)) if run_times else 0.0
            avg_tok_r1 = float(np.mean(run_tokens)) if run_tokens else 0.0
            
            with open(os.path.join(BENCH_DIR, "report_dettagliato_run_1.md"), "w", encoding="utf-8") as f_out:
                f_out.write(f"# Report Benchmark Dettagliato (Run 1) - ReAct_Pydantic\n\n")
                f_out.write(df_to_markdown_safe(df_run))
                f_out.write("\n\n### Tabella Finale Costi e Medie F1 (Run 1)\n")
                f_out.write(f"| Metrica | Valore |\n|---|---|\n")
                f_out.write(f"| Media F1-Score Entità | {np.mean(f1_e_list) if f1_e_list else 0:.4f} |\n")
                f_out.write(f"| Media F1-Score Relazioni | {np.mean(f1_r_list) if f1_r_list else 0:.4f} |\n")
                f_out.write(f"| Tempo medio elaborazione caso | {avg_t_r1:.2f} s |\n")
                f_out.write(f"| Token totali medi a caso | {avg_tok_r1:.0f} |\n")
            
            print(f"  [OK] Tabella e report della Run 1 salvati in: {BENCH_DIR}")

        history_runs.append({
            "Run": f"Run_{run_idx}",
            "F1_Entita": float(np.mean(f1_e_list)) if f1_e_list else 0.0,
            "Precision_Entita": float(np.mean(p_e_list)) if p_e_list else 0.0,
            "Recall_Entita": float(np.mean(r_e_list)) if r_e_list else 0.0,
            "F1_Relazioni": float(np.mean(f1_r_list)) if f1_r_list else 0.0,
            "Precision_Relazioni": float(np.mean(p_r_list)) if p_r_list else 0.0,
            "Recall_Relazioni": float(np.mean(r_r_list)) if r_r_list else 0.0,
            "Tempo_Medio_s": float(np.mean(run_times)) if run_times else 0.0,
            "Token_Medi": float(np.mean(run_tokens)) if run_tokens else 0.0
        })

    pd.DataFrame(history_runs).to_csv(os.path.join(BENCH_DIR, "serie_storica_10_run.csv"), index=False)
    print("\nBenchmark ReAct_Pydantic completato.")

if __name__ == "__main__":
    main()