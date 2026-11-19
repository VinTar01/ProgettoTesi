import os, sys, json, time, re
from typing import Tuple
import pandas as pd
import numpy as np
from rapidfuzz import fuzz
from google import genai
from google.genai import types
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
sys.path.append(ROOT_DIR)

load_dotenv(os.path.join(ROOT_DIR, ".env"))

# Import per accedere a prompt.py da una sottocartella
try:
    from Extraction_versions.prompt import PROMPT_BASE, PROMPT_STRUTTURA
except ImportError:
    from Extraction_versions.prompt import PROMPT_BASE_EN as PROMPT_BASE, PROMPT_STRUTTURA_EN as PROMPT_STRUTTURA

client_gemini = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
SIMILARITY_THRESHOLD = 80.0
TOTAL_RUNS = 10

def clean_and_parse_json(raw_text: str) -> dict:
    txt = raw_text.strip()
    if txt.startswith("```json"): txt = txt[7:]
    if txt.startswith("```"): txt = txt[3:]
    if txt.endswith("```"): txt = txt[:-3]
    match = re.search(r'(\{[\s\S]*\})', txt.strip())
    return json.loads(match.group(1)) if match else json.loads(txt.strip())

def normalize_text(text: str) -> str:
    return " ".join(re.sub(r'[^\w\s]', '', (text or "").lower().strip()).split())

def evaluate_pred_vs_gold(gold_data, pred_data):
    # Logica di valutazione
    gold_ents, pred_ents = gold_data.get("entities", []), pred_data.get("entities", [])
    used_p_ents, tp_ent = set(), 0
    for g in gold_ents:
        g_lbl, g_nm = g.get("label", ""), normalize_text(g.get("name", ""))
        for idx, p in enumerate(pred_ents):
            if idx in used_p_ents: continue
            if p.get("label", "") == g_lbl and fuzz.token_sort_ratio(g_nm, normalize_text(p.get("name", ""))) >= SIMILARITY_THRESHOLD:
                used_p_ents.add(idx); tp_ent += 1; break
    fp_ent, fn_ent = len(pred_ents) - len(used_p_ents), len(gold_ents) - tp_ent
    p_ent = tp_ent / (tp_ent + fp_ent) if (tp_ent + fp_ent) else 0.0
    r_ent = tp_ent / (tp_ent + fn_ent) if (tp_ent + fn_ent) else 0.0
    f1_ent = 2 * (p_ent * r_ent) / (p_ent + r_ent) if (p_ent + r_ent) else 0.0

    id_map = {ent.get("id"): normalize_text(ent.get("name", "")) for ent in pred_ents if ent.get("id")}
    pred_rels = [(id_map.get(r.get("source_id"), ""), r.get("type", ""), id_map.get(r.get("target_id"), "")) for r in pred_data.get("relationships", [])]
    gold_id_map = {ent.get("id"): normalize_text(ent.get("name", "")) for ent in gold_ents if ent.get("id")}
    gold_rels = [(gold_id_map.get(r.get("source_id"), ""), r.get("type", ""), gold_id_map.get(r.get("target_id"), "")) for r in gold_data.get("relationships", [])]

    used_p_rels, tp_rel = set(), 0
    for g_s, g_t, g_o in gold_rels:
        for idx, (p_s, p_t, p_o) in enumerate(pred_rels):
            if idx in used_p_rels: continue
            if g_t == p_t and fuzz.token_sort_ratio(g_s, p_s) >= SIMILARITY_THRESHOLD and fuzz.token_sort_ratio(g_o, p_o) >= SIMILARITY_THRESHOLD:
                used_p_rels.add(idx); tp_rel += 1; break
    fp_rel, fn_rel = len(pred_rels) - len(used_p_rels), len(gold_rels) - tp_rel
    p_rel = tp_rel / (tp_rel + fp_rel) if (tp_rel + fp_rel) else 0.0
    r_rel = tp_rel / (tp_rel + fn_rel) if (tp_rel + fn_rel) else 0.0
    f1_rel = 2 * (p_rel * r_rel) / (p_rel + r_rel) if (p_rel + r_rel) else 0.0
    return (p_ent, r_ent, f1_ent, tp_ent, fp_ent, fn_ent), (p_rel, r_rel, f1_rel, tp_rel, fp_rel, fn_rel)

def df_to_markdown_safe(df: pd.DataFrame) -> str:
    try: return df.to_markdown(index=False)
    except Exception:
        lines = ["| " + " | ".join(df.columns) + " |", "| " + " | ".join(["---"] * len(df.columns)) + " |"]
        for _, row in df.iterrows(): lines.append("| " + " | ".join(str(val) for val in row.values) + " |")
        return "\n".join(lines)

def run_pure_llm(testo: str, max_retries=3) -> Tuple[dict, float, int, int]:
    prompt = (PROMPT_BASE + "\n\n" + PROMPT_STRUTTURA).replace("{testo_caso}", testo)
    for attempt in range(1, max_retries + 1):
        start = time.time()
        try:
            resp = client_gemini.models.generate_content(model='gemini-flash-lite-latest', contents=prompt, config=types.GenerateContentConfig(temperature=0))
            elapsed = time.time() - start
            p_tok = getattr(resp.usage_metadata, 'prompt_token_count', 0)
            c_tok = getattr(resp.usage_metadata, 'candidates_token_count', 0)
            return clean_and_parse_json(resp.text), elapsed, p_tok, c_tok
        except Exception as e:
            print(f"      [Pure_LLM - Tentativo {attempt}] Errore: {e}")
            time.sleep(3)
    return {"entities": [], "relationships": []}, 0.0, 0, 0

def main():
    bench_dir = os.path.join(BASE_DIR, "benchmark_results")
    os.makedirs(bench_dir, exist_ok=True)
    with open(os.path.join(ROOT_DIR, "data", "raw", "dataset_cronaca_completo.json"), "r", encoding="utf-8") as f:
        dataset_mem = {c.get("id", "").strip().lower(): c for c in json.load(f)}
    
    gold_cases = {}
    gold_dir = os.path.join(ROOT_DIR, "Extraction_versions", "gold_standard")
    for f in os.listdir(gold_dir):
        if f.endswith(".json"):
            with open(os.path.join(gold_dir, f), "r", encoding="utf-8") as gf:
                gold_cases[f[:-5].replace("gold_standard_", "").strip().lower()] = json.load(gf)

    history_runs = []
    for run_idx in range(1, TOTAL_RUNS + 1):
        print(f"\n>> Esecuzione Run {run_idx}/{TOTAL_RUNS} (Pure_LLM)...")
        run_rows, f1_e_list, f1_r_list, run_times, run_tokens = [], [], [], [], []
        for cid, g_data in gold_cases.items():
            if cid not in dataset_mem: continue
            data, elap, p_tok, c_tok = run_pure_llm(dataset_mem[cid]["text"])
            run_times.append(elap); run_tokens.append(p_tok + c_tok)
            (pe, re, f1e, tpe, fpe, fne), (pr, rr, f1r, tpr, fpr, fnr) = evaluate_pred_vs_gold(g_data, data)
            f1_e_list.append(f1e); f1_r_list.append(f1r)
            
            # registrazione metriche entita e relazioni per la run corrente
            run_rows.append({"Caso": f"{cid} (Entità)", "Precision": round(pe, 4), "Recall": round(re, 4), "F1-Score": round(f1e, 4), "TP": tpe, "FP": fpe, "FN": fne})
            run_rows.append({"Caso": f"{cid} (Relazioni)", "Precision": round(pr, 4), "Recall": round(rr, 4), "F1-Score": round(f1r, 4), "TP": tpr, "FP": fpr, "FN": fnr})
            time.sleep(2)
        
        # Salvataggio CSV ad ogni iterazione
        df_run = pd.DataFrame(run_rows)
        df_run.to_csv(os.path.join(bench_dir, f"tabella_dettagliata_run_{run_idx}.csv"), index=False)
        
        # Salvataggio Markdown solo alla prima run
        if run_idx == 1:
            with open(os.path.join(bench_dir, "report_dettagliato_run_1.md"), "w", encoding="utf-8") as f_out:
                f_out.write(f"# Report Benchmark (Run 1) - Pure_LLM\n\n{df_to_markdown_safe(df_run)}\n")
        
        history_runs.append({
            "Run": f"Run_{run_idx}", "F1_Entita": np.mean(f1_e_list), "F1_Relazioni": np.mean(f1_r_list),
            "Tempo_Medio_s": np.mean(run_times), "Token_Medi": np.mean(run_tokens)
        })
        
    pd.DataFrame(history_runs).to_csv(os.path.join(bench_dir, "serie_storica_10_run.csv"), index=False)
    print("Benchmark Pure_LLM completato.")

if __name__ == "__main__": main()