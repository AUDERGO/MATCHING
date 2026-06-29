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

def compute_matrix(cotation, restriction):

    results = []
    """
    common_cols = list(set(cotation.columns) & set(restriction.columns))
    
    cols_to_exclude = ["posture","engin"]
    
    common_cols = [col for col in common_cols if col not in cols_to_exclude]
    """

    # ✅ Colonnes utilisées UNIQUEMENT pour le matching
    matching_columns = [
        "engin_debout",
        "engin_frontal",
        "engin_retract",
        "engin_tous",
        "membres_inf",
        "poignet",
        "epaule",
        "dos",
        "cervicales",
    ]

    # ✅ vérification sécurité
    missing = [col for col in matching_columns if col not in cotation.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans cotation : {missing}")

    missing_restr = [col for col in matching_columns if col not in restriction.columns]
    if missing_restr:
        raise ValueError(f"Colonnes manquantes dans restriction : {missing_restr}")

    # ✅ on fixe les colonnes utilisées
    common_cols = matching_columns.copy()

    for col in ["Poste", "Matricule"]:
        if col in common_cols:
            common_cols.remove(col)

    for _, poste_row in cotation.iterrows():

        if pd.isna(poste_row["Poste"]) or str(poste_row["Poste"]).strip() == "":
            continue

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

