# DDI Tutor

A free drug-drug interaction learning tool for new medical students. Search Indian brand
medicines or generic names, add them to a list, and see which combinations interact and how
severe the interaction is. A quiz tab helps students practise severity levels.

**Educational use only. Not for clinical decisions.**

## Data and credits

| Source | Licence | Used for |
|---|---|---|
| [DDInter 2.0](https://ddinter2.scbdd.com/download/) (`data/raw/ddinter_downloads_code_*.csv`) | CC BY-NC-SA 4.0 | interaction pairs and severity |
| A-Z Medicines Dataset of India, Kaggle, by Shudhanshu Singh and Vivek Tiwari (`data/raw/A_Z_medicines_dataset_of_India.csv`) | CC BY-SA 4.0 | brand name to ingredient mapping |
| Extensive A-Z Medicines Dataset of India, Kaggle (`data/raw/Extensive_A_Z_medicines_dataset_of_India.csv`) | Labelled MIT on Kaggle | not used by the app so far |

DDInter must be credited, used non-commercially, and shared under the same licence.
The Kaggle datasets were collected from online pharmacy sites, and their original terms are
unclear. If you are a rights holder and want a file removed, please open an issue.

## Setup (Windows)

Command Prompt:

```bat
python -m venv venv
venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Build the data and run

```bat
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

- "No interaction found" means none is listed in the DDInter files we used. It does not mean the combination is safe.
- Only 8 of the DDInter drug-class files were used (A, B, D, H, L, P, R, V). Some pairs, especially heart and nervous-system drugs, may be missing, so "no interaction found" can be wrong.
- Some pairs are recorded in DDInter with no severity grade. The app shows these as "Unknown".
- About 14% of brand medicines have no ingredient that maps to DDInter. Unmatched ingredients
  are listed in `data/processed/unmatched.csv` and shown in the app as "could not be checked".
- The brand file has two ingredient columns, so medicines with three or more ingredients may show only the first two.
- DDInter says its data may be incomplete or contain errors.
- Severity ignores dose, age, kidney or liver function and other conditions.

## Hosting (free)

Streamlit Community Cloud: connect this GitHub repo, main file `app.py`.
Free-tier limits have not been checked.

## Licence

Code: MIT (see `LICENSE`). Data keeps its own licences, listed above.