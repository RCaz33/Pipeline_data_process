# Agregate data and prepare for analysis


Data flow Raman :
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

Data flow DLS:
- Parcours les dossier d'echantillons uniques
- Extrait les données de chaque cahier xlsx
- Agrège les données dans un DataFrame
- Exporte les données dans un classeur excel
- Visualise les distributions de données


App\
|\
|--pages\
|   |--1_manuel.py : Streamlit page, Explain how to use endpoints\
|   |--2_Process_Raman.py : Streamlit page, preprocess data\
|   |   upload all the .csv file from a folder, \
|   |   filter from S/N ratio, \
|   |   fit peaks using Gaussian and Lorentzien function, \
|   |   export fit results\
|   |--3_Ag_DLS.py : Streamlit page, preprocess data\
|       upload and decode raw files, \
|       extract relevant information, \
|       agregate info from all files in folder, \
|       export report as excel file\
|--utils\
    |--data_processing.py : Python script, helper functions for Raman\
    |   generate_graph : function to inspect quality of filter parameter\
    |   _1gaussian, _1lorentzian: functions to fit 1 pic\
    |   _1gaussian, _1lorentzian: functions to deconvolute and fit 2 pics\
    |   Raman_Spectra: python class, contains methods to process data\
    |--utils_dls.py : Python script, helper functino for DLS\
        extract_data: function to isolate relevant data for the report\
        extract_DLS: python class, contains methods to process data\
\
\
\
Building docker image:

INSTALLATION :\
1 - PULL image from Git\
2 - Navigate to the folder "app"\
3 - Build docker image [ docker build -t <NAME_IMAGE> . ]\
4 - Prepare run  MAP a VOLUME for File Persistence (-v <path_on_host>:<path_in_container>)\
5 - Prepare run with PORT mapping for accessibility (-p <host_port>:<container_port>)\
6 - Start container [ docker run -d -e <> -e <> -p<> -v <> <NAME_IMAGE>]\
7 - Exemple [ docker run -d -p 8008:8501 -v "/mnt/your/loca/path":/app/container/path ]\