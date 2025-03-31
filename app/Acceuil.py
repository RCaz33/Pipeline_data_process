import streamlit as st

st.set_page_config(
    page_title="Acceuil",
    page_icon="👋",
)

st.write("# Analyse de spectre Raman")

st.sidebar.success("Choisir quoi faire ici :point_up:")


st.subheader("Ce que fait cet outil:")
st.text(
    """
- analyse tous les spectres raman (.csv) d'un dossier donné
- trier les spectres en fonction de l'intensité d'un pic donné (v1.0 -> utilise les pics à 2700 cm-1 & 1600 cm-1)
- visualiser l'aspect des spectres pour choisir le seuil
- choisir le seuil de coupure pour éliminer les spectres plats
- agréger tous les spectres avec la fonction moyenne
- lisser les spectres avec un filtre savgol (v1.0 -> window_length=20, polyorder=3)
- substrtact baseline (v1.0 -> snip method with max_half_window=40, decreasing=True, smooth_half_window=3)
- identifie les pics (réglage automatique de l'argument prominence dans la méthode find_peaks de Scipy)
- affine les pics pour ne sélectionner que 4 pics d'intérêt (bande D, bande G, bande 2D, bande D')
	* si le pic D' n'est pas trouvé, nous fixons sa position à 40 cm-1 de plus que le pic G
- utiliser la position et la hauteur des pics pour ajuster les courbes gaussiennes ou lorentziennes
- obtenir l'attribut des pics (en utilisant les méthodes Scipy find_peaks et peak_widths sur les courbes ajustées)
- afficher les résultats de l'ajustement
- exporter les spectres utilisés pour l'ajustement et les attributs des pics
""")

st.subheader("Ce que ne fait pas cet outil:")
st.markdown(
    """- l'interpretation des resultats ==> [Raman .. properties of graphene](https://www.nature.com/articles/nnano.2013.46)
- la préparation de tes tes échantillons 
- ta liste de courses ...
""")