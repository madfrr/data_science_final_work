# Unsupervised Fraud Detection on Bitcoin Wallets

> Portuguese notes: [README_pt.md](README_pt.md)

Final project (Data Science MBA) that applies **graph-mining and unsupervised anomaly detection** to the [Elliptic++](https://github.com/git-disl/EllipticPlusPlus) Bitcoin dataset, to see whether illicit wallets can be found without labels.

## What was done

The project follows the CRISP-DM steps:

1. **Data extraction:** the Elliptic++ files (wallets, transactions and edge lists) are downloaded from Google Drive, filtered to the relevant columns and saved as Parquet.
2. **Validation & EDA:** consistency checks, histograms and boxplots for every feature (`results/figures/`).
3. **Graph modelling:** wallet-to-wallet transactions are converted into a temporal edge list (`source, destination, measure = BTC amount, timestamp = time step`), the same input format CallMine and FraudGuess use for phone calls and card payments.
4. **Feature engineering:** [tgraph](https://github.com/mtcazzolato/tgraph-spot) extracts static (degree, weighted degree, core) and temporal (inter-arrival time, call count, measure statistics) features for each wallet. Two feature sets were evaluated:
   - **config_1**: only tgraph features.
   - **config_2**: the same structural features, with the temporal ones replaced by their Elliptic++ equivalents (block intervals, number of txs, median BTC sent/received).
5. **Anomaly detection:** [CallMine](https://github.com/mtcazzolato/callmine) (LookOut, for explainable pair plots) and **Gen2Out** (anomaly scores per wallet).
6. **Evaluation:** the scores are ranked and compared with the Elliptic++ labels (illicit vs. licit) using AUC-ROC, Average Precision, Precision@k and Recall@k.

### Results (Gen2Out, licit vs. illicit wallets)

| Feature set | AUC-ROC | Average Precision |
|-------------|---------|-------------------|
| config_1    | 0.680   | 0.077             |
| config_2    | 0.661   | 0.080             |

Illicit wallets make up about 5.4% of the labelled set (14,266 of 265,354). The scores separate the classes moderately, but precision at the top of the ranking is still low. Full output is in `results/scores/`, and the plots are in `results/figures/metrics/`.

**Next step:** use SHAP values from supervised models to choose better features, then feed them back into the unsupervised pipeline (an explainable feature-selection loop).

## Project structure

```
.
├── run.py                  # Entry point (python run.py)
├── config.py               # Paths, feature-set files and CallMine setups
├── requirements.txt
├── src/
│   ├── main.py             # Pipeline orchestration
│   ├── extract.py          # Downloads Elliptic++ from Google Drive
│   ├── extract_selected_columns.py  # Column selection/renaming → Parquet
│   ├── validations.py      # Data consistency checks
│   ├── transform/          # Edge-list creation, tgraph features, feature sets
│   ├── analysis/           # Histograms, boxplots
│   ├── algorithms.py       # Runs CallMine and Gen2Out
│   ├── metrics.py, metrics_a.py     # Ranking-based evaluation
│   └── scripts_elliptic_article/    # Reference notebooks from Elliptic++
├── callmine/               # Vendored CallMine (tgraph, LookOut, Gen2Out)
├── results/
│   ├── figures/            # EDA, CallMine pair plots, metric curves
│   ├── scores/             # Gen2Out scores and metric logs
│   └── notas/              # Notes, data dictionary, validation output
└── docs/                   # Reference papers
```

## Running

```bash
pip install -r requirements.txt
python run.py
```

Data is downloaded to `src/data/` the first time you run it. Steps that have already run are skipped. To run a single stage, comment or uncomment it in `src/main.py`. Tested with Python 3.10.

## References

- Weber et al., *Anti-Money Laundering in Bitcoin*, KDD 2019 / Elliptic++ (Elmougy & Liu, KDD 2023)
- Cazzolato et al., *CallMine: A Visual Graph Mining System for Detecting Phone Call Fraud*, CIKM 2023
- Cordeiro et al., *FraudGuess: Spotting and Explaining New Types of Fraud in Million-Scale Financial Data*, 2025
- Lee et al., *Gen2Out: Detecting and Ranking Generalized Anomalies*, 2021
- Gupta et al., *LookOut on Time-Evolving Graphs*, 2018
- Akoglu et al., *Graph-based Anomaly Detection and Description: A Survey*, DMKD 2015
