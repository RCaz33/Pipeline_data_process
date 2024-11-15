Application to automatize Raman spectra processing

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
