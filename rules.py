def check_engin(poste_row, restr_row):

    engin_cols = ["engin_debout", "engin_retract", "engin_frontal"]

    # le poste nécessite-t-il un engin ?
    poste_has_engin = any(poste_row[col] == 1 for col in engin_cols)

    if not poste_has_engin:
        return False, "pas_concerne"

    # CAS NOK global
    if restr_row.get("Engin", 0) == 1:
        return True, "engin_global"

    # CAS NOK spécifique
    for col in engin_cols:
        if poste_row[col] == 1 and restr_row[col] >= 1:
            return True, "engin_specifique"

    # CAS OK spécial limitation temps
    if all(restr_row[col] == 0 for col in engin_cols):
        if restr_row.get("limitation_temps_conduite", 0) == 1:
            return False, "ok_limitation"

    return False, "ok"
