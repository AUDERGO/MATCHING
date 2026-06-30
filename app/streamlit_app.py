import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from src.matching import compute_matrix
from datetime import datetime
import io

st.title("Matching Poste - Personne")

cotation_file = st.file_uploader("Cotation", type=["xlsx"])
restriction_file = st.file_uploader("Restriction", type=["xlsx"])

if cotation_file and restriction_file:

    # =========================
    # 📥 LECTURE
    # =========================

    cotation = pd.read_excel(cotation_file)
    restriction = pd.read_excel(restriction_file)

    # =========================
    # 📊 CAPACITÉ GLOBALE
    # =========================

    nb_personnes_total = restriction["Matricule"].nunique()
    nb_places = cotation["nombre de places"].fillna(0).sum()

    st.write("### 📊 Capacité globale")

    col1, col2 = st.columns(2)
    col1.metric("👤 Nb personnes", nb_personnes_total)
    col2.metric("🏭 Nb places disponibles", int(nb_places))

    # =========================
    # 🧠 MATRICE
    # =========================

    result = compute_matrix(cotation, restriction)

    st.write("### 📊 Matrice de matching")
    st.dataframe(result)

    # =========================
    # 🧮 PREPA INDICATEURS
    # =========================

    df_calc = result.copy()

    if "index" in df_calc.columns:
        df_calc = df_calc.set_index("index")

    # personnes en lignes
    df_calc = df_calc.T.fillna(0)

    # ✅ IMPORTANT : on isole uniquement les colonnes postes
    df_postes = df_calc.copy()

    # =========================
    # 📊 CALCULS CORRECTS
    # =========================

    # nb postes possibles = score == 0
    df_calc["nb_postes_possible"] = (df_postes == 0).sum(axis=1)

    # nb NOK = score > 0
    df_calc["nb_NOK"] = (df_postes > 0).sum(axis=1)

    # =========================
    # 📊 KPI
    # =========================

    nb_personnes = df_calc.shape[0]

    nb_all_ok = (df_calc["nb_NOK"] == 0).sum()
    nb_avec_nok = (df_calc["nb_NOK"] >= 1).sum()

    df_critiques = df_calc[
        (df_calc["nb_postes_possible"] >= 1) &
        (df_calc["nb_postes_possible"] <= 3)
    ]
    nb_critiques = df_critiques.shape[0]
  
    df_aucun_poste = df_calc[
        df_calc["nb_postes_possible"] == 0
    ]
    nb_aucun_poste = df_aucun_poste.shape[0]

    pct_all_ok = (nb_all_ok / nb_personnes) * 100
    pct_avec_nok = (nb_avec_nok / nb_personnes) * 100
    pct_critiques = (nb_critiques / nb_personnes) * 100
    pct_aucun_poste = (nb_aucun_poste / nb_personnes) * 100

    # =========================
    # 📊 AFFICHAGE KPI
    # =========================

    st.write("### 📊 Indicateurs de Match")

    col1, col2 = st.columns(2)

    col1.metric(
        "✅ Pouvant faire tous les postes",
        f"{nb_all_ok} ({pct_all_ok:.1f}%)"
    )

    col2.metric(
        "⚠️ Au moins 1 poste NOK",
        f"{nb_avec_nok} ({pct_avec_nok:.1f}%)"
    )

    col3, col4 = st.columns(2)

    col3.metric(
        "🚨 Cas critiques (1 à 3 postes)",
        f"{nb_critiques} ({pct_critiques:.1f}%)"
    )

    col4.metric(
        "❌ Aucun poste possible",
        f"{nb_aucun_poste} ({pct_aucun_poste:.1f}%)"
    )


    # =========================
    # 🚨 LISTE CRITIQUES
    # =========================

    st.write("### 🚨 Matricules cas critiques (1 à 3 postes possibles)")

    matricules_critiques = df_critiques.index.tolist()

    if len(matricules_critiques) > 0:
        st.warning(
            f"🚨 {nb_critiques} personne(s) disposent de seulement 1 à 3 postes possibles."
        )
        for m in matricules_critiques:
            ligne = restriction[restriction["Matricule"] == m]
            if not ligne.empty:
                nom = ligne.iloc[0]["Nom"]  # adapter si le nom de la colonne est différent
                st.markdown(f"🟠 **{m}** — {nom}")
            else:
                st.markdown(f"🟠 **{m}**")
    else:
        st.success("✅ Aucun cas critique")


    # =========================
    # ❌ LISTE AUCUN POSTE
    # =========================

    st.write("### ❌ Matricules sans aucun poste possible")

    matricules_aucun_poste = df_aucun_poste.index.tolist()

    if len(matricules_aucun_poste) > 0:
        st.error(
            f"❌ {nb_aucun_poste} personne(s) ne peuvent être affectées à aucun poste."
        )
        for m in matricules_aucun_poste:
            ligne = restriction[restriction["Matricule"] == m]
            if not ligne.empty:
                nom = ligne.iloc[0]["Nom"]  # adapter si besoin
                st.markdown(f"🔴 **{m}** — {nom}")
            else:
                st.markdown(f"🔴 **{m}**")
    else:
        st.success("✅ Tout le monde possède au moins un poste compatible.")


    # =========================
    # 📥 EXPORT EXCEL
    # =========================

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        result.to_excel(writer, index=False)

    excel_data = output.getvalue()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

    st.download_button(
        label="📥 Télécharger matrice Excel",
        data=excel_data,
        file_name=f"matrice_matching_{timestamp}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


    # =========================
    # 🔎 ANALYSE DETAILLEE METIER
    # =========================

    st.write("### 🔎 Analyse détaillée")

    # 👉 saisie libre matricule
    matricule = st.text_input("Saisir un matricule")

    # 👉 choix poste
    poste = st.selectbox("Choisir un poste", result["index"])

    if matricule:

        # =========================
        # 🔍 LIGNES SOURCE
        # =========================

        # Ligne personne dans restriction
        ligne_personne_src = restriction[restriction["Matricule"] == matricule]

        # Ligne poste dans cotation
        ligne_poste_src = cotation[cotation["Poste"] == poste]

        if ligne_personne_src.empty:
            st.error("Matricule non trouvé dans le fichier restriction")
        elif ligne_poste_src.empty:
            st.error("Poste non trouvé dans le fichier cotation")
        else:

            ligne_personne_src = ligne_personne_src.iloc[0]
            ligne_poste_src = ligne_poste_src.iloc[0]

            # =========================
            # 👤 DETAIL PERSONNE (1 ligne)
            # =========================

            st.write("### 👤 Détail personne (restriction)")

            st.dataframe(ligne_personne_src.to_frame(name="Valeur"))

            # Affichage du texte précision si existe
            if "precision" in ligne_personne_src.index:
                st.info(f"💬 Précision : {ligne_personne_src['precision']}")

            # =========================
            # 🏭 DETAIL POSTE (1 ligne)
            # =========================

            st.write("### 🏭 Détail poste (cotation)")

            st.dataframe(ligne_poste_src.to_frame(name="Valeur"))

            # =========================
            # 🔁 TABLEAU CROISEMENT SIMPLE
            # =========================

            st.write("### 📊 Analyse croisée")

            # On garde seulement colonnes communes (colonnes métier)
            colonnes_communes = [
                col for col in restriction.columns
                if col in cotation.columns
                and col not in ["Matricule", "Poste", "precision"]
            ]

            data_compare = []

            for col in colonnes_communes:
                val_personne = ligne_personne_src[col]
                val_poste = ligne_poste_src[col]

                # règle : blocage si 1 et 1
                croisement = 1 if (val_personne == 1 and val_poste == 1) else 0

                data_compare.append([col, val_personne, val_poste, croisement])

            df_compare = pd.DataFrame(
                data_compare,
                columns=["Critère", "Personne (0/1)", "Poste (0/1)", "Blocage"]
            )

            # =========================
            # 🎨 VISUALISATION SIMPLE
            # =========================

            def highlight_blocage(row):
                if row["Blocage"] == 1:
                    return ["background-color: red"] * 4
                return [""] * 4

            st.dataframe(df_compare.style.apply(highlight_blocage, axis=1))

            # =========================
            # ✅ RESULTAT GLOBAL
            # =========================

            nb_blocages = df_compare["Blocage"].sum()

            if nb_blocages == 0:
                st.success("✅ OK : aucun blocage")
            else:
                st.error(f"❌ NOK : {nb_blocages} blocage(s) détecté(s)")
