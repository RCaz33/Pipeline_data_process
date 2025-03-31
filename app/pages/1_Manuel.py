import streamlit as st

st.set_page_config(page_title="Manuel utilisation", page_icon=":dizzy:")
st.sidebar.header("Etapes :")
st.sidebar.text("""
- Charger le dossier
- Choisir le seuil de coupure 
- Calculer le fit des pics
- Exporter les données
""")

st.title("Sélection du dossier")
st.write("Naviguez vers le dossier, faire un click droit & 'copier en tant que chemin d'acces'")
st.write("Autre option : Ctrl + Shift + c ---> Ctrl + v")
st.image("images/select_folder.jpg",caption="Selectionner un dossier contenant les fichiers d'analyse Raman pour un échantillon")

st.write("Appuyez sur 'Entrée' après avoir collé le chemin d'accès à votre dossier")
st.image("images/press_enter.jpg",caption="Appuyez sur 'Entrée' après avoir collé le lien ")

st.title("Sélection du seuil de coupure")
st.write("Cliquez sur 'Test' afin de visualiser le seuil de coupure")
st.write("Changez le seuil au besoin en tapant au clavier ou avec les boutons + / - et cliquez sur 'Test' pour recalculer")
st.write("Gauche : visualisation du seuil de coupure. Centre : Tous les spoecytres conservés. Droite :spectre raman avant (rouge) et apres(bleu) filtartion des données")
st.image("images/select_threshold.jpg",caption="Selectionner un seuil de coupure pour exclure les données trop bruitées")

st.title("Visualisation des fits et export des données")
st.write("Cliquez sur 'Exporter' afin d'enregistrer les données dans un fichier excel 'nom_de_batch__threshold__parametres_fit.xlsx")
st.image("images/resultat_fit.jpg",caption="Exporter le resultat du fit avec le bouton 'Exporter'")


