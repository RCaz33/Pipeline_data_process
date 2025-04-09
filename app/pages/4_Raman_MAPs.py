import streamlit as st
from utils.utils_maps import get_data, do_ML_magic, get_me_the_graph, get_me_the_other_graph
import pandas as pd

# configuration page
st.set_page_config(page_title="data_processing", page_icon=":dizzy:")
st.sidebar.header("Etapes :")
st.sidebar.text("""
- Charger le dossier
- AGrege données 
- Utilser ML (KMeans) 
- Montrer les groupes
- Montrer les données par groupes
- Exporter les données par groupes
""")

# instructions
st.title("Sélection du dossier")
st.write("Collez le chemin d'accès ci-dessous puis appuyez sur 'Entrée'")
st.write("Raccourci : Ctrl + Shift + c ---> Ctrl + v")

# Champ de texte pour entrer le chemin du dossier
folder_path = st.text_input('Entrez le chemin du dossier entre guillements {"}')

# préparer les données
if folder_path:
    folder_path = "/app/Disk_mount/"+ "/".join(folder_path.replace("\\","/")[1:-1].split("/")[-2:])
    sample = folder_path.split("/")[-1]
    
    u = get_data(folder_path)

    validation=False
    n_clust = st.number_input("Select threshold", min_value=2, max_value=10, value=3, step=1)
    st.text('Preparing the magic')
    groups, weights, kmeans = do_ML_magic(u,n_clust)
    st.success(f"Magic is ready")


   
    if st.button("Magic graphs"):
        get_me_the_graph(groups, n_clust)
        
    if st.button("Look at subset groups"):
        get_me_the_other_graph(groups, kmeans, weights, n_clust)

    if st.button("export graphs"):
        try:
            with pd.ExcelWriter(f"/app/Disk_mount/RAMAN_average_{sample}_groups_{n_clust}.xlsx") as writer: 
                for group in groups['kmeans'].unique():    
                    out = pd.DataFrame()
                    out['mean'] = groups.groupby('kmeans').mean().iloc[group-1,:]
                    out['std_h'] = (groups.groupby('kmeans').mean() + (groups.groupby('kmeans').std()/2)).iloc[group-1,:]
                    out['std_l'] = (groups.groupby('kmeans').mean() - (groups.groupby('kmeans').std()/2)).iloc[group-1,:]
                    out.to_excel(writer,sheet_name=f'group_{group}')

                st.success("Fits exportés avec succès")
        except Exception as e:
                st.error(f"Problème pendant l'export: {e}")         
        
            







