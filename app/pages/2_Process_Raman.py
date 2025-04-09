import streamlit as st
from utils.data_processing import Raman_Spectra, generate_graph
import pandas as pd

# configuration page
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

# instructions
st.title("Sélection du dossier")
st.write("Collez le chemin d'accès ci-dessous puis appuyez sur 'Entrée'")
st.write("Naviguez vers le dossier")
st.write("Option1 : click droit & 'copier en tant que chemin d'acces'")
st.write("Option2 : Ctrl + Shift + c ---> Ctrl + v")

# Champ de texte pour entrer le chemin du dossier
folder_path = st.text_input('Entrez le chemin du dossier entre guillements {"}')

# préparer les données
if folder_path:
    folder_path = "/app/Disk_mount/"+ "/".join(folder_path.replace("\\","/")[1:-1].split("/")[-2:])
    sample = folder_path.split("/")[-1]
    raman = Raman_Spectra(folder_path, sample)
    raman.read_folder()
    sorted_data = raman.Order_data()

    choix_decile=0
    validation=False
    decile = st.number_input("Select threshold", min_value=0, max_value=100, value=50, step=1)
    choix_decile = decile / 100
    st.session_state['raman'] = raman

    # Button to validate the choice
    if st.button("Test"):
        generate_graph(sorted_data, choix_decile)
        st.success(f"Le threshold choisi est {choix_decile}")
        _ = raman.choix_threshold_auto(threshold=choix_decile)
        _ = raman.prepare_data_for_fit()
        

        # visualiser l'impact de la selection de données
        col1, col2 = st.columns(2)
        # fit Gaussian
        with col1:
            results_G, fitted_curve_G = raman.fit_peaks_gaussian()
            st.header("fit Gaussien")
            fig_G = raman.Check_fit()
            st.pyplot(fig_G)
            st.subheader("Fit params")
            df_G = pd.DataFrame(list(results_G.items()), columns=['Parameter', 'Value'])
            st.table(df_G)
            st.session_state['results_G'] = results_G 
        # fit Laurentzien
        with col2:   
            results_L, fitted_curve_L = raman.fit_peaks_lorentzien()
            st.header("fit Laurentzien")
            fig_L = raman.Check_fit()
            st.pyplot(fig_L)
            st.subheader("Fit params")
            df_L = pd.DataFrame(list(results_L.items()), columns=['Parameter', 'Value'])
            st.table(df_L)
            st.session_state['results_L'] = results_L 

    # exporter les données agrégées      
    if st.button("Exporter fits"):
        
        # prepare data for fit
        raman = Raman_Spectra(folder_path, sample)
        _ = raman.read_folder()
        _ = raman.Order_data()
        _ = raman.choix_threshold_auto(threshold=choix_decile)
        _ = raman.prepare_data_for_fit()
        
        # fit
        results_G, fitted_curve_G = raman.fit_peaks_gaussian()
        results_L, fitted_curve_L = raman.fit_peaks_lorentzien()  
        results_G = st.session_state['results_G']
        results_L = st.session_state['results_L']
        df_G = pd.DataFrame(list(results_G.items()), columns=['Parameter', 'Value'])
        df_L = pd.DataFrame(list(results_L.items()), columns=['Parameter', 'Value'])

        # export
        try:
            with pd.ExcelWriter(f"/app/Disk_mount/RAMAN_{sample}_fit_threshold_{choix_decile}.xlsx") as writer:        
                df_G.to_excel(writer,sheet_name=f'Gaussian') 
                df_L.to_excel(writer,sheet_name='Lorentzien')
                st.success("Fits exportés avec succès")
        except Exception as e:
                st.error(f"Problème pendant l'export: {e}")         
        
            







