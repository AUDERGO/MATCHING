import pandas as pd

def check_engin(poste_row, restr_row):

    engin_cols = ["engin_debout", "engin_retract", "engin_frontal"]

    # =========================
    # ✅ 1. Cas interdiction totale (engin_tous)
    # =========================
    poste_has_engin = any(poste_row.get(col, 0) == 1 for col in engin_cols)

    if restr_row.get("engin_tous", 0) == 1 and poste_has_engin:
        return True  # ❌ blocage

    # =========================
    # ✅ 2. Cas standard : restriction spécifique
    # =========================
    for col in engin_cols:
        if poste_row.get(col, 0) == 1:

            # Si la personne ne peut pas utiliser cet engin → blocage
            if restr_row.get(col, 0) == 1:
                return True

            # Sinon c’est OK
            return False

    # =========================
    # ✅ 3. Aucun engin demandé
    # =========================
    return False

def compute_matrix(cotation, restriction):

    results = []

    common_cols = list(set(cotation.columns) & set(restriction.columns))
    
    cols_to_exclude = ["posture","engin"]
    
    common_cols = [col for col in common_cols if col not in cols_to_exclude]

    for col in ["Poste", "Matricule"]:
        if col in common_cols:
            common_cols.remove(col)

    for _, poste_row in cotation.iterrows():

        row_result = {"Poste": poste_row["Poste"]}

        for _, restr_row in restriction.iterrows():

            score = 0
            
            if check_engin(poste_row, restr_row):
                score += 1
            
            for col in common_cols:

                if col.startswith("engin"):
                    continue

                if poste_row[col] == 1 and restr_row[col] >= 1:
                    score += 1

            row_result[restr_row["Matricule"]] = score

        results.append(row_result)

   
    df = pd.DataFrame(results)
    
    df.index = df.index + 1
    
    df = df.rename(columns={"Poste": "index"})

    return df

