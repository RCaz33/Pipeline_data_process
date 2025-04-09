import streamlit as st
from utils.utils_dls import extract_DLS
import pandas as pd

st.set_page_config(page_title="processing_DLS", page_icon=":ghost:")
st.sidebar.header("Etapes :")
st.sidebar.text("""
- Parcours les dossier d'echantillons uniques
- Extrait les données de chaque cahier xlsx
- Agrège les données dans un DataFrame
- Exporte les données dans un classeur excel
- Visualise les distributions de données
""")

st.title("Agregation DLS")
st.header("Sélection du dossier")
st.write("Naviguez vers le dossier, faire un click droit & 'copier en tant que chemin d'acces'")
st.write("Collez le chemin d'accès ci-dessous puis appuyez sur 'Entrée'")
st.write("Autre option : Ctrl + Shift + c ---> Ctrl + v")

# Champ de texte pour entrer le chemin du dossier
folder_path = st.text_input('Entrez le chemin du dossier entre guillements {"}')

# DEBUG IMPORT/EXPORT
# st.text(f"path used: {folder_path.replace("\\","/").replace("C:","/mnt/c")}")
# st.text(f"path in container: {"/app/Disk_mount/"+ "/".join(folder_path.replace("\\","/")[1:-1].split("/")[-2:])}")

if folder_path:
        # for development --> link to NAS
    # folder_path = folder_path.replace("\\","/").replace("Y:","/mnt/CW_Network")[1:-1]
    # for deploiement --> link to Docker folder with the disk mount on RUN
    # folder_path = folder_path.replace("\\","/").replace("C:","/mnt/c")[1:-1]
    folder_path = "/app/Disk_mount/"+ "/".join(folder_path.replace("\\","/")[1:-1].split("/")[-2:])
    sample = folder_path.split("/")[-1]
    data_DLS = extract_DLS(folder_path)
    data_DLS.gather_data()
    data_DLS.generate_report()

    # Button to validate the choice
    if st.button("See report"):
        report = data_DLS.show_report()
        st.subheader("Report means")
        st.table(report)
        
    
    if st.button("Exporter avec echantillons dans tabs"):
        
                     
        to_use = data_DLS.show_ready()
        recap = data_DLS.show_report()
        sample_date = "2025-04-01"
        
        col_to_keep = ['Angle [°]','MeanCR0 [kHz]','Order2 FluctuationFreq. [1/ms]',
        'Order2 DiffCoefficient [µm²/s]', 'Order2 Hydrodyn. Radius [nm]',
        'Order2 Expansion Parameter µ2']

        try:
            with pd.ExcelWriter(f"/app/Disk_mount/DLS_recap_{sample_date}.xlsx") as writer:        
            
                for sample in to_use.Samplename.value_counts().index:
                    _ = to_use.loc[to_use.Samplename == sample, col_to_keep].sort_values(by='Angle [°]')
                    _.to_excel(writer,sheet_name=f'{sample}_raw')
                    _.groupby('Angle [°]').agg(['mean','std']).to_excel(writer,sheet_name=f'{sample}_mean')
                recap.to_excel(writer,sheet_name=f'recap') 
    
            st.success("Fichier récap exporté avec succès")
        except Exception as e:
            st.error(f"Problème pendant l'export: {e}")         
        
            




