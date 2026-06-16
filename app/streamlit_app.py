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

    import io
    
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

    import io
    
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
    
  
