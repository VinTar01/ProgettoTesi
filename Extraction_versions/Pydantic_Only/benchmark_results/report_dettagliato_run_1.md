# Report Benchmark Dettagliato (Run 1) - Pydantic_Only

| Caso                                      |   Precision |   Recall |   F1-Score |   TP |   FP |   FN |
|:------------------------------------------|------------:|---------:|-----------:|-----:|-----:|-----:|
| delitto_di_cogne (Entità)                 |      0.5    |   0.7778 |     0.6087 |   14 |   14 |    4 |
| delitto_di_cogne (Relazioni)              |      0.3636 |   0.6316 |     0.4615 |   12 |   21 |    7 |
| delitto_di_novi_ligure (Entità)           |      0.625  |   0.4839 |     0.5455 |   15 |    9 |   16 |
| delitto_di_novi_ligure (Relazioni)        |      0.3529 |   0.3243 |     0.338  |   12 |   22 |   25 |
| omicidio_di_alberto_brasili (Entità)      |      0.6471 |   0.2821 |     0.3929 |   11 |    6 |   28 |
| omicidio_di_alberto_brasili (Relazioni)   |      0.3125 |   0.0877 |     0.137  |    5 |   11 |   52 |
| omicidio_di_giulia_cecchettin (Entità)    |      0.44   |   0.4583 |     0.449  |   11 |   14 |   13 |
| omicidio_di_giulia_cecchettin (Relazioni) |      0.4062 |   0.4483 |     0.4262 |   13 |   19 |   16 |
| omicidio_di_marco_vannini (Entità)        |      0.5926 |   0.5161 |     0.5517 |   16 |   11 |   15 |
| omicidio_di_marco_vannini (Relazioni)     |      0.3182 |   0.3333 |     0.3256 |   14 |   30 |   28 |
| omicidio_di_marta_russo (Entità)          |      0.5161 |   0.6154 |     0.5614 |   16 |   15 |   10 |
| omicidio_di_marta_russo (Relazioni)       |      0.2941 |   0.4167 |     0.3448 |   10 |   24 |   14 |

### Tabella Finale Costi e Medie F1 (Run 1)
| Metrica | Valore |
|---|---|
| Media F1-Score Entità | 0.5182 |
| Media F1-Score Relazioni | 0.3389 |
| Tempo medio elaborazione caso | 18.63 s |
| Token totali medi a caso | 11811 |
