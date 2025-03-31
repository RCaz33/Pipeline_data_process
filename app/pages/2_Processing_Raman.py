import streamlit as st
from utils.data_processing import Raman_Spectra, generate_graph
# import os
# from io import StringIO
# from time import sleep
# import seaborn as sns
# import matplotlib.pyplot as plt
# import numpy as np
import pandas as pd

st.set_page_config(page_title="data_processing", page_icon=":dizzy:")
st.sidebar.header("Etapes :")
st.sidebar.text("""
- Charger le dossier
- Reclasser 
- Visualiser les spectres 
- Choisir le seuil de coupure 
- Agréger tous les spectres
- Lisser (SavGol, window_length=20, polyorder=3)
- Ligne de base (snip, max_half_window=40, decreasing=True, smooth_half_window=3)
- Identifier les pics 
- Definir paraetres de fit
- Fitter fonctions gaussiennes / lorentziennes
- Extraire les attributs des pics 
- Afficher les résultats de l'ajustement
- Exporter les données
""")

st.title("Sélection du dossier")
st.write("Naviguez vers le dossier, faire un click droit & 'copier en tant que chemin d'acces'")
st.write("Collez le chemin d'accès ci-dessous puis appuyez sur 'Entrée'")
st.write("Autre option : Ctrl + Shift + c ---> Ctrl + v")

# Champ de texte pour entrer le chemin du dossier
folder_path = st.text_input("Entrez le chemin du fichier")
st.text('folder_path.replace("\\","/").replace("C:","/mnt/c")')
st.text(folder_path.replace("\\","/").replace("C:","/mnt/c"))
st.text("/".join(folder_path.replace("\\","/").split("/")[-2:]))
st.text('"/".join(folder_path.replace("\\","/").split("/")[-2:])')


if folder_path:
        # for development --> link to NAS
    # folder_path = folder_path.replace("\\","/").replace("Y:","/mnt/CW_Network")[1:-1]
    # for deploiement --> link to Docker folder with the disk mount on RUN
    # folder_path = folder_path.replace("\\","/").replace("C:","/mnt/c")[1:-1]
    folder_path = "/app/Disk_mount/"+ "/".join(folder_path.replace("\\","/")[1:-1].split("/")[-2:])
    sample = folder_path.split("/")[-1]
    raman = Raman_Spectra(folder_path, sample)
    raman.read_folder()
    sorted_data = raman.Order_data()

    choix_decile=0
    
    validation=False
    
    decile = st.number_input("Select threshold", min_value=0, max_value=100, value=50, step=1)
    choix_decile = decile / 100

    # Button to validate the choice
    if st.button("Test"):
        generate_graph(sorted_data, choix_decile)
        
    
    if st.button("Valider"):
        raman.choix_threshold_auto(threshold=choix_decile)
        fig = raman.prepare_data_for_fit(debug=True)
        
        # st.title("Sélection automatique des pics pour le fit")
        # st.pyplot(fig)
        
        results_G, fitted_curve_G = raman.fit_peaks_gaussian()
        st.header("resultat fit Gaussien")
        fig_G = raman.Check_fit()
        st.pyplot(fig_G)
        st.subheader("Fit params")
        df_G = pd.DataFrame(list(results_G.items()), columns=['Parameter', 'Value'])
        st.table(df_G)
        
        if st.button("Exporter fits Gaussien"):
            df_G.to_excel(f"/app/Disk_mount/Sample_{sample}__threshold_{decile}__fit_Gaussien.xlsx")
        
        results_L, fitted_curve_L = raman.fit_peaks_lorentzien()
        st.header("resultat fit Laurentzien")
        fig_L = raman.Check_fit()
        st.pyplot(fig_L)
        st.subheader("Fit params")
        df_L = pd.DataFrame(list(results_L.items()), columns=['Parameter', 'Value'])
        st.table(df_L)
        
        st.text(f"/app/Disk_mount/Sample_{sample}__threshold_{decile}__fit_Gaussien.xlsx")
        
        if st.button("Exporter fits Laurentzien"):
            df_L.to_excel(f"/app/Disk_mount/Sample_{sample}__threshold_{decile}__fit_Gaussien.xlsx")

            

        



