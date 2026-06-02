def build_debug(cotation, restriction):

    rows = []

    for _, poste in cotation.iterrows():
        for _, restr in restriction.iterrows():

            engin_block, rule = check_engin(poste, restr)

            rows.append({
                "Poste": poste["Poste"],
                "Matricule": restr["Matricule"],
                "Bloquant_Engin": engin_block,
                "Regle": rule
            })

    return pd.DataFrame(rows)
