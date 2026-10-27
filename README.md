# DDI Tutor

A free drug-drug interaction learning tool for new medical students. Search Indian brand
medicines or generic names, add them to a list, and see which combinations interact and how
severe the interaction is. A quiz tab helps students practise severity levels.

**Educational use only. Not for clinical decisions.**

## Data

| Source | Used for |
|---|---|
| DDInter (`data/raw/ddinter_downloads_code_*.csv`) | interaction pairs and severity |
| A-Z Medicines Dataset of India (`data/raw/A_Z_medicines_dataset_of_India.csv`) | brand name to ingredient mapping |

## Setup (Windows PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Build the data and run

```powershell
python -m pipeline.build_pairs       # data/processed/pairs.csv
python -m pipeline.names             # data/processed/brand_generic.csv + match report
python -m pipeline.build_app_data    # data/app/*.csv.gz (committed, used by the app)
streamlit run app.py
pytest
```

## Layout

- `pipeline/build_pairs.py`: merge DDInter files, de-duplicate pairs
- `pipeline/names.py`: map brand ingredients to DDInter names (salts, synonyms)
- `pipeline/build_app_data.py`: small files the hosted app loads
- `pipeline/lookup.py`: search and interaction logic (no UI code)
- `app.py`: Streamlit web app
- `tests/`: pytest suite

## Known limits

- "No interaction found" means none is listed in DDInter, not that the combination is safe.
- About 14% of brand medicines have no ingredient that maps to DDInter; unmatched ingredients
  are listed in `data/processed/unmatched.csv` and shown in the app as "could not be checked".
- Severity ignores dose, age, kidney/liver function and other conditions.

## Hosting (free)

Streamlit Community Cloud: connect this GitHub repo, main file `app.py`.
