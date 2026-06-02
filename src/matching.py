import pandas as pd

def check_engin(poste_row, restr_row):

    engin_cols = ["engin_debout", "engin_retract", "engin_frontal"]

    poste_has_engin = any(poste_row[col] == 1 for col in engin_cols)

    if not poste_has_engin:
        return False

    # NOK global
    if restr_row.get("Engin", 0) == 1:
        return True

    # NOK spécifique
    for col in engin_cols:
        if poste_row[col] == 1 and restr_row[col] >= 1:
            return True

    # OK spécial limitation
    if all(restr_row[col] == 0 for col in engin_cols):
        if restr_row.get("limitation_temps_conduite", 0) == 1:
            return False

    return False


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

            # ENGIN
            if check_engin(poste_row, restr_row):
                score += 1

            for col in common_cols:

                if col.startswith("engin"):
                    continue

                if poste_row[col] == 1 and restr_row[col] >= 1:
                    score += 1

            row_result[restr_row["Matricule"]] = score

        results.append(row_result)

    return pd.DataFrame(results)
