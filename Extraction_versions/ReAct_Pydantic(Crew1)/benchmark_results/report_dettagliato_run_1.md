# Report Benchmark Dettagliato (Run 1) - ReAct_Pydantic

| Caso                                      |   Precision |   Recall |   F1-Score |   TP |   FP |   FN |
|:------------------------------------------|------------:|---------:|-----------:|-----:|-----:|-----:|
| delitto_di_cogne (Entità)                 |      0.4138 |   0.6667 |     0.5106 |   12 |   17 |    6 |
| delitto_di_cogne (Relazioni)              |      0.375  |   0.4737 |     0.4186 |    9 |   15 |   10 |
| delitto_di_novi_ligure (Entità)           |      0.5862 |   0.5484 |     0.5667 |   17 |   12 |   14 |
| delitto_di_novi_ligure (Relazioni)        |      0.4167 |   0.4054 |     0.411  |   15 |   21 |   22 |
| omicidio_di_alberto_brasili (Entità)      |      0.9167 |   0.2821 |     0.4314 |   11 |    1 |   28 |
| omicidio_di_alberto_brasili (Relazioni)   |      0.4545 |   0.0877 |     0.1471 |    5 |    6 |   52 |
| omicidio_di_giulia_cecchettin (Entità)    |      0.1846 |   0.5    |     0.2697 |   12 |   53 |   12 |
| omicidio_di_giulia_cecchettin (Relazioni) |      0.1912 |   0.4483 |     0.268  |   13 |   55 |   16 |
| omicidio_di_marco_vannini (Entità)        |      0.6154 |   0.5161 |     0.5614 |   16 |   10 |   15 |
| omicidio_di_marco_vannini (Relazioni)     |      0.28   |   0.3333 |     0.3043 |   14 |   36 |   28 |
| omicidio_di_marta_russo (Entità)          |      0.4615 |   0.6923 |     0.5538 |   18 |   21 |    8 |
| omicidio_di_marta_russo (Relazioni)       |      0.275  |   0.4583 |     0.3437 |   11 |   29 |   13 |

### Tabella Finale Costi e Medie F1 (Run 1)
| Metrica | Valore |
|---|---|
| Media F1-Score Entità | 0.4823 |
| Media F1-Score Relazioni | 0.3155 |
| Tempo medio elaborazione caso | 13.20 s |
| Token totali medi a caso | 17548 |
