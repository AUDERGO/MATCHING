import pandas as pd
from src.matching import check_engin

def build_debug_table(cotation, restriction):

    rows = []

    common_cols = list(set(cotation.columns) & set(restriction.columns))

    for col in ["Poste", "Matricule"]:
        if col in common_cols:
            common_cols.remove(col)

    for _, poste_row in cotation.iterrows():
        for _, restr_row in restriction.iterrows():

            poste = poste_row["Poste"]
            matricule = restr_row["Matricule"]

            # --- ENGIN ---
            engin_block = check_engin(poste_row, restr_row)

            rows.append({
                "Poste": poste,
                "Matricule": matricule,
                "Colonne": "ENGIN_GLOBAL",
                "Poste_val": "voir colonnes engin",
                "Restr_val": restr_row.get("Engin", 0),
                "Resultat": "BLOQUANT" if engin_block else "OK"
            })

            # --- AUTRES COLONNES ---
            for col in common_cols:

                poste_val = poste_row[col]
                restr_val = restr_row[col]

                if col.startswith("engin"):
                    continue

                bloquant = (poste_val == 1 and restr_val >= 1)

                rows.append({
                    "Poste": poste,
                    "Matricule": matricule,
                    "Colonne": col,
                    "Poste_val": poste_val,
                    "Restr_val": restr_val,
                    "Resultat": "BLOQUANT" if bloquant else "OK"
                })

    df = pd.DataFrame(rows)

    # index propre
    df.index = df.index + 1

    return df
