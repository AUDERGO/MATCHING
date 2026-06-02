import pandas as pd
from rules import check_engin

def compute_matrix(cotation, restriction):

    results = []

    common_cols = list(set(cotation.columns) & set(restriction.columns))
    for col in ["Poste", "Matricule"]:
        if col in common_cols:
            common_cols.remove(col)

    for _, poste_row in cotation.iterrows():

        row_result = {"Poste": poste_row["Poste"]}

        for _, restr_row in restriction.iterrows():

            score = 0

            # --- ENGIN ---
            engin_block, rule = check_engin(poste_row, restr_row)
            if engin_block:
                score += 1

            # --- AUTRES COLONNES ---
            for col in common_cols:
                if col.startswith("engin"):
                    continue

                if poste_row[col] == 1 and restr_row[col] >= 1:
                    score += 1

            row_result[restr_row["Matricule"]] = score

        results.append(row_result)

    return pd.DataFrame(results)
