import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from src.matching import compute_matrix
from src.debug import build_debug_table

st.title("Matching Poste - Personne")

cotation_file = st.file_uploader("Cotation", type=["xlsx"])
restriction_file = st.file_uploader("Restriction", type=["xlsx"])

if cotation_file and restriction_file:

    cotation = pd.read_excel(cotation_file)
    restriction = pd.read_excel(restriction_file)

    result = compute_matrix(cotation, restriction)

    st.write("### Matrice de matching")
    st.dataframe(result)

    # =========================
    # 📊 INDICATEURS AUTOMATIQUES
    # =========================

    df_calc = result.copy()

    # On met les postes en index
    if "index" in df_calc.columns:
        df_calc = df_calc.set_index("index")

    # TRANSPOSE : on veut personnes en lignes
    df_calc = df_calc.T
    df_calc = df_calc.fillna(0)

    nb_postes = df_calc.shape[1]

    # Nombre de NOK par personne
    df_calc["nb_NOK"] = df_calc.sum(axis=1)

    # Nombre de postes possibles
    df_calc["nb_postes_possible"] = nb_postes - df_calc["nb_NOK"]

    # Calculs taux
    nb_all_ok = (df_calc["nb_NOK"] == 0).sum()
    nb_avec_nok = (df_calc["nb_NOK"] >= 1).sum()

    nb_critiques = df_calc[
        (df_calc["nb_postes_possible"] >= 1) &
        (df_calc["nb_postes_possible"] <= 3)
    ].shape[0]

    # Affichage
    st.write("### 📊 Indicateurs de Match")

    col1, col2, col3 = st.columns(3)

    col1.metric("✅ 0 NOK (tous postes)", nb_all_ok)
    col2.metric("⚠️ ≥ 1 NOK", nb_avec_nok)
    col3.metric("🚨 1 à 3 postes possibles", nb_critiques)

    import io

    # =========================
    # 🔎 ANALYSE DETAILLEE COMPLETE
    # =========================

    st.write("### 🔎 Analyse détaillée")

    df_analyse = result.copy()

    # Postes en index
    if "index" in df_analyse.columns:
        df_analyse = df_analyse.set_index("index")

    # Transpose : personnes en lignes
    df_analyse = df_analyse.T
    df_analyse = df_analyse.fillna(0)

    # Sélection utilisateur
    matricule = st.selectbox("Choisir un matricule", df_analyse.index)
    poste = st.selectbox("Choisir un poste", df_analyse.columns)

    # Valeur de matching
    match_value = df_analyse.loc[matricule, poste]

    # =========================
    # ✅ RESULTAT GLOBAL
    # =========================

    st.write("### ✅ Résultat du matching")

    if match_value == 0:
        st.success("✅ Compatible")
    else:
        st.error("❌ NOK (blocage)")

    # =========================
    # DETAIL PERSONNE
    # =========================

    st.write("### 👤 Détail personne")

    ligne_personne = df_analyse.loc[matricule]
    st.dataframe(ligne_personne.to_frame(name="Valeur"))

    # =========================
    # 🏭 DETAIL POSTE
    # =========================

    st.write("### 🏭 Détail poste")

    df_poste_vue = result.copy()

    if "index" in df_poste_vue.columns:
        df_poste_vue = df_poste_vue.set_index("index")

    ligne_poste = df_poste_vue.loc[poste]

    st.dataframe(ligne_poste.to_frame(name="Valeur"))

    # =========================
    # ANALYSE DES BLOCAGES
    # =========================

    st.write("### Analyse des blocages")

    if match_value == 0:
        st.success("✅ Aucun blocage : personne compatible avec ce poste")

    else:
        st.error("❌ NOK : cette personne ne peut pas occuper ce poste")

        st.info("👉 Voir le détail dans le tableau debug ci-dessous pour comprendre la cause exacte")


    # =========================
    # 🎨 VUE COMPARATIVE (TRÈS UTILE)
    # =========================

    st.write("### 📊 Comparaison personne vs poste")

    df_compare = pd.DataFrame({
        "Personne": ligne_personne,
        "Poste": ligne_poste
    })

    def highlight_blocages(row):
        if row["Personne"] == 1 and row["Poste"] == 1:
            return ["background-color: red"] * 2
        return [""] * 2

    st.dataframe(df_compare.style.apply(highlight_blocages, axis=1))


    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        result.to_excel(writer, index=False)
        
    excel_data = output.getvalue()
    
    st.download_button(
        label="📥 Télécharger matrice Excel",
        data=excel_data,
        file_name="matrice_matching.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    debug_df = build_debug_table(cotation, restriction)

    st.write("### 🔎 Détail complet (debug brut)")
    st.dataframe(debug_df)

    
    output_debug = io.BytesIO()
    
    with pd.ExcelWriter(output_debug, engine='openpyxl') as writer:
        debug_df.to_excel(writer, index=False)
        
    excel_debug = output_debug.getvalue()
    
    st.download_button(
        label="📥 Télécharger debug Excel",
        data=excel_debug,
        file_name="debug_matching.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
  
