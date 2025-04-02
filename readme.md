
Application to automatize Raman spectra processing

Developpment steps
1- Notebook Sprint5_RD_3_Raman.ipynb => code developpment
2- Notebook Sprint6_RD_1_Raman.ipynb => tests + comparisons manual extraction
3- Script Sprint6_RD_Raman_utils.py => Defines class Raman_Spectra to use
4- Notebook Sprint6_RD_1.2_Raman.ipynb => Troubleshooting (noisy spectras, new source of analysis, ...)
 

- parse all the raman spectra (.csv) of a given folder
- sort spectra by the hiegh of a given peak (v1.0 -> uses peak at 2700 cm-1 & 1600 cm-1)
- visualize the aspect of spectra to choose threshold
- choose the cuttoff threshold for removing flat spectras
- aggregate all the spectra with mean function
- smooth the spectra with a savgol filter (v1.0 -> window_length=20, polyorder=3)
- substrtact baseline (v1.0 -> snip method with max_half_window=40, decreasing=True, smooth_half_window=3)
- identifies peaks (automatic setting of prominence argument in find_peaks method from Scipy)
- refine peaks to select only 4 peaks of interest (D band, G band, 2D band, D' band)
	* if D' peak not found we set its peak position at 40 cm-1 more than peak G
- use peaks position and height to fit Gaussian or Lorentzian curves
- get peaks attribute (using Scipy find_peaks and peak_widths method on fitted curves)
- display fitting results
- export the spectra used for fitting and peaks attributes



Building docker image:


INSTALLATION :

1 - PULL image from Git

2 - Navigate to app_streamlit

3 - Build docker image [ docker build -t <NAME_IMAGE> . ]
	--> may need to change user ID in the dockerfile to allow writing on disk : "RUN groupadd -g ${GROUP_ID} <group_name>" "RUN useradd -u ${USER_ID} -g <group_name> -m <user_session_name>" 
	==> run "id" in terminal to get the ids

4 - Prepare run with CREDENTIALS for AZURE (-e LANGUAGE_ENDPOINT="..." -e LANGUAGE_KEY="...")

5 - Prepare run  MAP a VOLUME for File Persistence (-v <path_on_host>:<path_in_container>)

6 - Prepare run with PORT mapping for accessibility (-p <host_port>:<container_port>)

7 - Start container [ docker run -d -e <> -e <> -p<> -v <> <NAME_IMAGE>]

8 - Exemple [ docker run -d -p 8008:8501 -v "/mnt/CW_Network/3- R&D Process/8-Approches data & algos/88_Raman_spetra":/app/export preprocess_raman ]