import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator

STRUCT = "data/processed/structures.csv"
OUT_NPZ = "data/processed/fingerprints.npz"
OUT_INFO = "data/processed/fingerprint_info.csv"
LARGE = 100  # heavy atoms; my choice, to review
GEN = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)


def largest_fragment(mol):
    frags = Chem.GetMolFrags(mol, asMols=True)
    return max(frags, key=lambda m: m.GetNumHeavyAtoms())


def featurize(smiles):
    """Return (fingerprint, heavy_atoms, n_fragments) or None if RDKit cannot read it."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    n_frag = len(Chem.GetMolFrags(mol))
    main = largest_fragment(mol)
    fp = np.asarray(GEN.GetFingerprintAsNumPy(main), dtype=np.uint8)
    return fp, main.GetNumHeavyAtoms(), n_frag


if __name__ == "__main__":
    s = pd.read_csv(STRUCT)
    s = s[s["status"] == "found"]
    ids, fps, rows = [], [], []
    for drug_id, drug, smiles in zip(s["drug_id"], s["drug"], s["smiles"]):
        out = featurize(smiles)
        if out is None:
            continue
        fp, heavy, n_frag = out
        ids.append(drug_id)
        fps.append(fp)
        rows.append({"drug_id": drug_id, "drug": drug, "heavy_atoms": heavy,
                     "fragments": n_frag, "large": heavy > LARGE,
                     "empty_fp": int(fp.sum() == 0)})
    np.savez_compressed(OUT_NPZ, drug_ids=np.array(ids), fps=np.vstack(fps))
    info = pd.DataFrame(rows)
    info.to_csv(OUT_INFO, index=False)

    print("drugs with a fingerprint:", len(info))
    print("multi-fragment (salts etc.):", int((info["fragments"] > 1).sum()))
    print("large (>%d heavy atoms):" % LARGE, int(info["large"].sum()))
    print("empty fingerprint:", int(info["empty_fp"].sum()))
    print(info["heavy_atoms"].describe().round(1))
    print("\nlargest 15:")
    print(info.nlargest(15, "heavy_atoms")[["drug", "heavy_atoms"]].to_string(index=False))