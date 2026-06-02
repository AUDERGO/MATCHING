import pandas as pd

def build_debug_table(cotation, restriction):

    rows = []

    # colonnes engin
    engin_cols = ["engin_debout", "engin_retract", "engin_frontal"]

    # colonnes communes
    common_cols = list(set(cotation.columns) & set(restriction.columns))

    for col in ["Poste", "Matricule"]:
        if col in common_cols:
            common_cols.remove(col)

    for _, poste_row in cotation.iterrows():
        for _, restr_row in restriction.iterrows():

            poste = poste_row["Poste"]
            matricule = restr_row["Matricule"]

            # ======================================================
            # 🔎 1. LOGIQUE ENGIN (GLOBAL + DÉTAIL)
            # ======================================================

            # récupérer valeurs
            poste_engins = {col: poste_row.get(col, 0) for col in engin_cols}
            restr_engins = {col: restr_row.get(col, 0) for col in engin_cols}

            engin_global = restr_row.get("Engin", 0)
            limitation = restr_row.get("limitation_temps_conduite", 0)

            poste_has_engin = any(v == 1 for v in poste_engins.values())

            # appliquer logique métier
            if poste_has_engin:

                if engin_global == 1:
                    if limitation == 1 and all(restr_engins[col] == 0 for col in engin_cols):
                        engin_result = "OK"
                        engin_reason = "limitation_temps_ignore_engin"
                    
                    else:
                        engin_result = "BLOQUANT"
                        engin_reason = "engin_global"

                elif any(poste_engins[col] == 1 and restr_engins[col] >= 1 for col in engin_cols):
                    engin_result = "BLOQUANT"
                    engin_reason = "engin_specifique"

                elif all(restr_engins[col] == 0 for col in engin_cols) and limitation == 1:
                    engin_result = "OK"
                    engin_reason = "limitation_temps"

                else:
                    engin_result = "OK"
                    engin_reason = "ok"

            else:
                engin_result = "OK"
                engin_reason = "poste_sans_engin"

            # 👉 ligne globale ENGIN
            rows.append({
                "Poste": poste,
                "Matricule": matricule,
                "Type": "ENGIN_GLOBAL",
                "Colonne": "ENGIN",
                "Poste_val": poste_engins,
                "Restr_val": f"global={engin_global}, detail={restr_engins}",
                "Resultat": engin_result,
                "Raison": engin_reason
            })

            # 👉 détail ligne par ligne des engins
            for col in engin_cols:
                rows.append({
                    "Poste": poste,
                    "Matricule": matricule,
                    "Type": "ENGIN_DETAIL",
                    "Colonne": col,
                    "Poste_val": poste_row.get(col, 0),
                    "Restr_val": restr_row.get(col, 0),
                    "Resultat": "INFO",
                    "Raison": "detail_engin"
                })

            # ======================================================
            # 🔎 2. AUTRES CONTRAINTES (STANDARD)
            # ======================================================

            for col in common_cols:

                # exclure colonnes engin déjà traitées
                if col in engin_cols:
                    continue
                if col == "Engin":
                    continue
                if col == "limitation_temps_conduite":
                    continue

                poste_val = poste_row.get(col, 0)
                restr_val = restr_row.get(col, 0)

                bloquant = (poste_val == 1 and restr_val >= 1)

                rows.append({
                    "Poste": poste,
                    "Matricule": matricule,
                    "Type": "STANDARD",
                    "Colonne": col,
                    "Poste_val": poste_val,
                    "Restr_val": restr_val,
                    "Resultat": "BLOQUANT" if bloquant else "OK",
                    "Raison": "regle_standard"
                })

    df = pd.DataFrame(rows)

    # index propre
    df.index = df.index + 1

    return df
