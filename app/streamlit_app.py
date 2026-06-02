import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from src.matching import compute_matrix
from src.debug import build_debug_table

st.title("Matching Ergonomique")

cotation_file = st.file_uploader("Cotation", type=["xlsx"])
restriction_file = st.file_uploader("Restriction", type=["xlsx"])

if cotation_file and restriction_file:

    cotation = pd.read_excel(cotation_file)
    restriction = pd.read_excel(restriction_file)

    result = compute_matrix(cotation, restriction)

    st.write("### Matrice de matching")
    st.dataframe(result)

    st.download_button(
        "Télécharger Excel",
        result.to_csv(index=False),
        "matrice.csv"
    )

    debug_df = build_debug_table(cotation, restriction)
    st.write("### Détail complet (debug)")
    st.dataframe(debug_df)

    st.download_button(
        "Télécharger détail",
        debug_df.to_csv(index=False),
        "debug_matching.csv",
        "text/csv"
    )
