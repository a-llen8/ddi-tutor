# DDI Tutor

A free drug-drug interaction learning tool for new medical students. Search Indian brand
medicines or generic names, add them to a list, and see which combinations interact and how
severe the interaction is. A quiz tab helps students practise severity levels.

**Educational use only. Not for clinical decisions.**

## Data and credits

| Source | Licence | Used for |
|---|---|---|
| [DDInter](https://ddinter2.scbdd.com/terms/) (download files, 8 ATC class files; `data/raw/ddinter_downloads_code_*.csv`) | CC BY-NC-SA 4.0 | interaction pairs and severity |
| A-Z Medicines Dataset of India, Kaggle, by Shudhanshu Singh and Vivek Tiwari (`data/raw/A_Z_medicines_dataset_of_India.csv`) | CC BY-SA 4.0 | brand name to ingredient mapping |
| Extensive A-Z Medicines Dataset of India, Kaggle (`data/raw/Extensive_A_Z_medicines_dataset_of_India.csv`) | Labelled MIT on Kaggle | not used by the app so far |

How to cite DDInter: Xiong G, Yang Z, Yi J, et al. DDInter: an online drug-drug interaction database towards improving clinical decision-making and patient safety. Nucleic Acids Research. 2022;50(D1):D1200-D1207. doi:10.1093/nar/gkab880

DDInter data is licensed CC BY-NC-SA 4.0 (the site's own terms: https://ddinter2.scbdd.com/terms/). It must be credited, used non-commercially, and shared under the same licence. The 8 class files were merged and duplicate pairs removed. Derived files in this repo (`data/app/`, `results/`) are shared under the same licence.
The Kaggle datasets were collected from online pharmacy sites, and their original terms are
unclear. If you are a rights holder and want a file removed, please open an issue.

## Setup (Windows)

`requirements.txt` lists the four packages the app needs to run. It is the file a host installs. `requirements-dev.txt` adds what building the data, training the models and running the tests need (pytest, rdkit, scikit-learn, xgboost, requests). The steps below install the dev file, which covers everything.

Command Prompt:

```bat
python -m venv venv
venv\Scripts\activate.bat
python -m pip install -r requirements-dev.txt
```

PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

## Build the data and run

```bat
python -m pipeline.build_pairs       # data/processed/pairs.csv
python -m pipeline.names             # data/processed/brand_generic.csv + match report
python -m pipeline.build_app_data    # data/app/*.csv.gz (committed, used by the app)
python -m pipeline.coverage          # data/app/coverage.csv.gz (which drugs the 8 files cover)
python -m ml.build_predictions       # data/processed/predictions.db (about 2 hours, resumes, not tracked)
streamlit run app.py
python -m pytest
```

## Layout

- `pipeline/build_pairs.py`: merge DDInter files, de-duplicate pairs
- `pipeline/names.py`: map brand ingredients to DDInter names (salts, synonyms)
- `pipeline/build_app_data.py`: small files the hosted app loads
- `pipeline/coverage.py`: which drugs the 8 DDInter class files cover completely
- `pipeline/lookup.py`: search and interaction logic (no UI code)
- `app.py`: Streamlit web app
- `ml/lookup_predictions.py`: look up a pair: documented (with severity), predicted (band), outside the 8 files, no prediction, or name not found with suggestions
- `ml/lookalike.py`: the 5 closest known pairs behind a band
- `ml/spot_pairs.py`: spot-the-pair scoring
- `ml/case_simulator.py`: check 2 to 8 typed drugs against confirmed DDInter pairs
- `ml/random_case.py`: random practice cases
- `ml/srs.py`: spaced repetition scheduler
- `ml/sureness.py`: turns "How sure?" and right or wrong into a scheduler grade
- `ml/progress.py`: progress download and upload, with validation and merge rule
- `ml/dashboard.py`: weak-topic dashboard
- `ml/interact.py`: model for documented versus not documented
- `ml/calibrate.py`, `ml/calibrate_known.py`: calibration of those scores
- `ml/build_predictions.py`: builds the predictions database
- `ml/evaluate.py`: model evaluation
- `ml/popularity.py`: popularity-only baseline check
- `tests/`: pytest suite

## Known limits

- "No record" means no interaction is listed in the 8 DDInter files used here. It does not mean the combination is safe.
- DDInter organises interactions into files by ATC drug class, and publishes 8 of the 14 class
  files (A, B, D, H, L, P, R, V). All 8 are used here. The 6 that are not published are C, G, J,
  M, N and S. A pair of two drugs that both sit outside the 8 files can never appear as
  documented in this project: 1,036 of 1,939 drugs are fully covered and 903 are not, which
  leaves 407,253 pairs invisible here. Digoxin plus Amiodarone is one of them. The app marks
  these pairs and shows no band for them.
- Some pairs are recorded in DDInter with no severity grade. The app shows these as "Unknown".
- About 14% of brand medicines have no ingredient that maps to DDInter. Unmatched ingredients
  are listed in `data/processed/unmatched.csv` and shown in the app as "could not be checked".
- The brand file has two ingredient columns, so medicines with three or more ingredients may show only the first two.
- DDInter says its data may be incomplete or contain errors.
- Severity ignores dose, age, kidney or liver function and other conditions.
- The flashcard scheduler (`ml/srs.py`) follows the SM-2 method, but it was written from memory and has not been checked against the original paper.
- Predictions are labelled "Predicted, not confirmed" and shown as Low, Medium or High bands, never as percentages. A band says how much a pair looks like pairs DDInter lists, by chemical structure. It is not a risk or severity rating. Low does not mean safe.
- Pairs where one or both drugs were not seen in training get no prediction. Drugs with no chemical structure on file also get none.

## Hosting (free)

Streamlit Community Cloud: connect this GitHub repo, main file `app.py`.
Free-tier limits have not been checked.

## Licence

Code: MIT (see `LICENSE`). Data keeps its own licences, listed above.