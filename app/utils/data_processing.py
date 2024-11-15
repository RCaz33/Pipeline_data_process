
import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt

from pybaselines import Baseline
from scipy.signal import savgol_filter, find_peaks, peak_widths
import scipy

# fonction to fit gaussian peaks , use methdo because doesnt access self 
def _1gaussian(x, amp1,cen1,sigma1):
    return amp1*(1/(sigma1*(np.sqrt(2*np.pi))))*(np.exp((-1.0/2.0)*(((x-cen1)/sigma1)**2)))

def _2gaussian(x, amp1,cen1,sigma1, amp2,cen2,sigma2):
    return amp1*(1/(sigma1*(np.sqrt(2*np.pi))))*(np.exp((-1.0/2.0)*(((x-cen1)/sigma1)**2))) + \
            amp2*(1/(sigma2*(np.sqrt(2*np.pi))))*(np.exp((-1.0/2.0)*(((x-cen2)/sigma2)**2)))


def _1lorentzian(x, amp1, cen1, gamma1):
    return amp1 * (1 / np.pi) * (gamma1 / 2) / ((x - cen1)**2 + (gamma1 / 2)**2)

def _2lorentzian(x, amp1, cen1, gamma1, amp2, cen2, gamma2):
    return amp1 * (1 / np.pi) * (gamma1 / 2) / ((x - cen1)**2 + (gamma1 / 2)**2) + \
           amp2 * (1 / np.pi) * (gamma2 / 2) / ((x - cen2)**2 + (gamma2 / 2)**2)

class Raman_Spectra:
    
    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.all_data = None
        self.sorted_data = None
        self.filtered_data = None
        self.ready_data = None
        self.peaks_ids = None
        self.fitted_curve = None
        
    def __str__(self):
        return f"handeling sample : {self.name}"
    
    def show_sorted(self):
        return self.sorted_data
    
    def show_ready_data(self):
        return self.ready_data
    
    def show_peaks(self):
        return self.peaks_ids
    
    
    def read_folder(self):
        """load all the .csv file in a folder

        Args:
            folder_path (str): path to datafiles
        Returns:
            all_data (pd.DataFrame) : all csv files with wavenumber in index
        """

        all_data = pd.DataFrame()

        for file in os.listdir(self.path):
            if file.lower().endswith('.csv') and not file.lower().startswith("ref hopg"):
                file_path = os.path.join(self.path,file)
                _ = pd.read_csv(file_path,delimiter=";",header=None)
                signal = _.iloc[:,1]
                all_data = pd.concat([all_data,signal],axis=1)

        if not all_data.empty:
            steps = _.iloc[:,0]
            all_data.index = steps

        self.all_data = all_data
        return all_data
    
    
    def Order_data(self):
        """Re-order data by sum of std of peaks 2700 cm-1 and 1600 cm-1

        Args:
            all_data (pd.DataFrame): DataFrame with shape (1764 data_points,n data_traces)
        Returns:
            sorted_data (pd.DataFrame) : all csv files sorted by stds   
        """
        if self.all_data is None or self.all_data.empty:
            raise ValueError("You must read_folder first.")
        
        mask = self.all_data.loc[(self.all_data.index > 2600) & (self.all_data.index < 2800) ,:].std()+\
        self.all_data.loc[(self.all_data.index > 1500) & (self.all_data.index < 1700) ,:].std() # pic G

        _int = self.all_data.T

        _int.index = mask

        self.sorted_data = _int.sort_index().T 
        return _int.sort_index().T 
    
    
    def choix_threshold(self):
        choix_decile = 0.1
        validation = False
        c = sns.color_palette("Spectral",as_cmap=True)

        while not validation:
            
            
            
            decile_1 = np.quantile(self.sorted_data.columns, choix_decile)
            idx = [i for i in range(len(self.sorted_data.columns)) if self.sorted_data.columns[i] > decile_1][0]


            fig,axs=plt.subplots(1,3,figsize=(12,3))

            colors=sns.color_palette("crest", 10)

            _offset = self.sorted_data.iloc[:,idx-5+0].max()
            for i in range(10):
                offset=i*_offset
                (self.sorted_data.iloc[:,idx-5+i]+offset).plot(legend=False,c=colors[i],alpha=0.75,ax=axs[0])

            axs[0].set_title("10 spectres autour de la valeur decile")
            self.sorted_data.iloc[:,idx:].plot(legend=False, cmap=c, alpha = 0.5,ax=axs[1])
            axs[1].set_title("tous les spectres conservés")
            self.sorted_data.mean(axis=1).plot(c='r',alpha=0.75,legend=False,ax=axs[2])
            self.sorted_data.iloc[:,idx:].mean(axis=1).plot(c='b',legend=False,ax=axs[2])
            axs[2].set_title("spectres moyens avt/apres filtrage")


            print(f"avec un decile à {choix_decile*100}%, on utilise {self.sorted_data.shape[1]-idx}/{self.sorted_data.shape[1]} spectres Raman")
            plt.show()
            
            
            
            
            validation = input('OK or not? write OK if OK')
            validation = False if validation != 'OK' else True
            choix_decile = float(input('choice decile'))
            
        self.filtered_data = self.sorted_data.iloc[:,idx:].mean(axis=1)
        
        
        return self.filtered_data
    
    def choix_threshold_auto(self,threshold=0.66):
        """FIlter data gicven a quantile threshold

        Args:
            sorted_data (pd.DataFrame): raman data with wavenumber as index
            threshold (float, optional): Proportion of data to keep. Defaults to 0.66.

        Returns:
            pd.DataFrame: mean() of all raman spectra
        """
        choix_decile = float(threshold)
        decile_1 = np.quantile(self.sorted_data.columns, choix_decile)
        idx = [i for i in range(len(self.sorted_data.columns)) if self.sorted_data.columns[i] > decile_1][0]
        self.filtered_data = self.sorted_data.iloc[:,idx:].mean(axis=1)
        return self.filtered_data
    


    def prepare_data_for_fit(self,debug=False):
        """remove baseline from data

        Args:
            x (np.array): wavenumber
            y (np.array): spectral values

        Returns:
            ready_data (pd.DataFrame): Data with substracted baseline
            peaks_ids (list()) : Pekas identified with scipy and index of peaks to keep
        """

        x = self.filtered_data.index
        y = self.filtered_data.values
        y = savgol_filter(y,window_length=20,polyorder=3)
        baseline_fitter = Baseline(x_data=x)
        bkg_4, params_4 = baseline_fitter.snip(y,max_half_window=40,decreasing=True,smooth_half_window=3)
        y_bsl = (y-bkg_4)

        
        for i in range(5,25)[::-1]:
            peaks, _ = find_peaks(y_bsl,prominence=(i))
            for peak_idx in peaks:
                if (peak_idx > 510) and (peak_idx < 560):
                    break
            else:
                continue
            break
            
       # get index of peaks of interest
        peaks_idxs = list()
        for i,p in enumerate(x[peaks]):
            if ((p > 1300) and (p < 1400)) or ((p > 1550) and (p < 1650)) or ((p > 2650) and (p < 2750)):
                peaks_idxs.append(i)
       
        self.ready_data = pd.DataFrame(y_bsl, index=x)
        self.peaks_ids = list([peaks,peaks_idxs])
        
        if debug==True:
            # peaks identification
            _peaks = self.peaks_ids

            plt.plot(x, self.ready_data.values)
            for i in _peaks[1]:
                plt.axvline(x[_peaks[0][i]], lw=0.5,c='r')
            plt.show()


    # # fonction to fit gaussian peaks , use methdo because doesnt access self 
    # @staticmethod
    # def _1gaussian(x, amp1,cen1,sigma1):
    #     return amp1*(1/(sigma1*(np.sqrt(2*np.pi))))*(np.exp((-1.0/2.0)*(((x-cen1)/sigma1)**2)))
    
    # @staticmethod
    # def _2gaussian(x, amp1,cen1,sigma1, amp2,cen2,sigma2):
    #     return amp1*(1/(sigma1*(np.sqrt(2*np.pi))))*(np.exp((-1.0/2.0)*(((x-cen1)/sigma1)**2))) + \
    #             amp2*(1/(sigma2*(np.sqrt(2*np.pi))))*(np.exp((-1.0/2.0)*(((x-cen2)/sigma2)**2)))

    def fit_peaks_gaussian(self):
        """fit peaks with Gaussian functions

        Args:
            ready_data (pd.DataFrame): data to be fitted
            peaks_ids (list()): peaks and index of peaks to use
 
        Returns:
            results (dict()): peaks attribute with keys "peak_n"
            fitted_curve (dict()) : Gaussain fit of peaks with keys "peak_n"
        """
            

        x = self.ready_data.index
        y_bsl = self.ready_data.values.reshape(-1)
        peaks = self.peaks_ids[0]
        peaks_idxs = self.peaks_ids[1]
        
        results=dict()
        fitted_curve=dict()

        # fit peak D 
        peak1_position = x[peaks[peaks_idxs][0]]
        peak1_height = y_bsl[peaks[peaks_idxs][0]]
             
        popt_gauss, pcov_gauss = scipy.optimize.curve_fit(_1gaussian, x, y_bsl, p0=[peak1_height, peak1_position, 1])
        fitted_peak_1 = _1gaussian(x, *popt_gauss)
        peaks1, _ = find_peaks(fitted_peak_1)
        results_half1 = peak_widths(fitted_peak_1, peaks1, rel_height=0.5)
        results["peak1_D_position"] = x[peaks1[0]] 
        results["peak1_D_FWHM"] = results_half1[0][0]
        results["peak1_D_height"] = fitted_peak_1[peaks1[0]]
        fitted_curve["peak_1"] = fitted_peak_1

        # fit peak 2D
        peak4_position = x[peaks[peaks_idxs][-1:][0]]
        peak4_height = y_bsl[peaks[peaks_idxs][-1:][0]]
        popt_gauss, pcov_gauss = scipy.optimize.curve_fit(_1gaussian, x, y_bsl, p0=[peak4_height, peak4_position, 1])
        fitted_peak_4 = _1gaussian(x, *popt_gauss)
        peaks4, _ = find_peaks(fitted_peak_4)
        results_half4 = peak_widths(fitted_peak_4, peaks4, rel_height=0.5)
        results["peak4_D_position"] = x[peaks4[0]] 
        results["peak4_D_FWHM"] = results_half4[0][0]
        results["peak4_D_height"] = fitted_peak_4[peaks4[0]]
        fitted_curve["peak_4"] = fitted_peak_4

        # fit peaks G & D`
        #initial guess
        amp1 = y_bsl[peaks[peaks_idxs][1]] # 80
        cen1 = x[peaks[peaks_idxs][1]] # 1585
        sigma1 = 1

        if len(peaks_idxs) > 3:
            amp2 = y_bsl[peaks[peaks_idxs][2]] # 20
            cen2 = x[peaks[peaks_idxs][2]] # 1625
            sigma2 = 0.5
        else:
            amp2 = y_bsl[peaks[peaks_idxs][1]] / 4 # 20
            cen2 = x[peaks[peaks_idxs][1]] + 40 # 1625
            sigma2 = 0.5
            
        popt_2gauss, pcov_2gauss = scipy.optimize.curve_fit(_2gaussian, x, y_bsl, p0=[amp1, cen1, sigma1, amp2, cen2, sigma2])
        pars_2 = popt_2gauss[0:3]
        pars_3 = popt_2gauss[3:6]
        fitted_peak_2 = _1gaussian(x, *pars_2)
        fitted_peak_3 = _1gaussian(x, *pars_3)

        peaks2, _ = find_peaks(fitted_peak_2)
        results_half2 = peak_widths(fitted_peak_2, peaks2, rel_height=0.5)
        results["peak2_D_position"] = x[peaks2[0]] 
        results["peak2_D_FWHM"] = results_half2[0][0]
        results["peak2_D_height"] = fitted_peak_2[peaks2[0]]
        fitted_curve["peak_2"] = fitted_peak_2

        peaks3, _ = find_peaks(fitted_peak_3)
        results_half3 = peak_widths(fitted_peak_3, peaks3, rel_height=0.5)
        try:
            results["peak3_D_position"] = x[peaks3[0]] 
            results["peak3_D_FWHM"] = results_half3[0][0]
            results["peak3_D_height"] = fitted_peak_3[peaks3[0]]
            fitted_curve["peak_3"] = fitted_peak_3
        except:
            results["peak3_D_position"] = 0
            results["peak3_D_FWHM"] = 0
            results["peak3_D_height"] = 0
            fitted_curve["peak_3"] = 0

        self.fitted_curve = fitted_curve
        return results, fitted_curve
    
    
    def fit_peaks_lorentzien(self, debug=False):
        """fit peaks with Lorentzien functions

        Args:
            ready_data (pd.DataFrame): data to be fitted
            peaks_ids (list()): peaks and index of peaks to use
 
        Returns:
            results (dict()): peaks attribute with keys "peak_n"
            fitted_curve (dict()) : Lorentz fit of peaks with keys "peak_n"
        """
               
        x = self.ready_data.index
        y_bsl = self.ready_data.values.reshape(-1)
        peaks = self.peaks_ids[0]
        peaks_idxs = self.peaks_ids[1]
        
        results=dict()
        fitted_curve=dict()

        # fit peak D 
        peak1_position = x[peaks[peaks_idxs][0]]
        peak1_height = y_bsl[peaks[peaks_idxs][0]]
                
        popt_gauss, pcov_gauss = scipy.optimize.curve_fit(_1lorentzian, x, y_bsl, p0=[peak1_height, peak1_position, 1])
        fitted_peak_1 = _1lorentzian(x, *popt_gauss)
        peaks1, _ = find_peaks(fitted_peak_1)
        results_half1 = peak_widths(fitted_peak_1, peaks1, rel_height=0.5)
        results["peak1_D_position"] = x[peaks1[0]] 
        results["peak1_D_FWHM"] = results_half1[0][0]
        results["peak1_D_height"] = fitted_peak_1[peaks1[0]]
        fitted_curve["peak_1"] = fitted_peak_1

        # fit peak 2D
        peak4_position = x[peaks[peaks_idxs][-1:][0]]
        peak4_height = y_bsl[peaks[peaks_idxs][-1:][0]]
        popt_gauss, pcov_gauss = scipy.optimize.curve_fit(_1lorentzian, x, y_bsl, p0=[peak4_height, peak4_position, 1])
        fitted_peak_4 = _1lorentzian(x, *popt_gauss)
        peaks4, _ = find_peaks(fitted_peak_4)
        results_half4 = peak_widths(fitted_peak_4, peaks4, rel_height=0.5)
        results["peak4_D_position"] = x[peaks4[0]] 
        results["peak4_D_FWHM"] = results_half4[0][0]
        results["peak4_D_height"] = fitted_peak_4[peaks4[0]]
        fitted_curve["peak_4"] = fitted_peak_4

        # fit peaks G & D`
        
        if debug == True:
            print(self.peaks_ids[0])
            print(self.peaks_ids[1])
            print(self.peaks_ids[0][self.peaks_ids[1][0]])
            print(self.peaks_ids[0][self.peaks_ids[1][1]])
            
        #initial guess
        amp1 = y_bsl[peaks[peaks_idxs][1]] # 80
        cen1 = x[peaks[peaks_idxs][1]] # 1585
        sigma1 = 1

        if len(peaks_idxs) > 3:
            amp2 = y_bsl[peaks[peaks_idxs][2]] # 20
            cen2 = x[peaks[peaks_idxs][2]] # 1625
            sigma2 = 0.5
        else:
            amp2 = y_bsl[peaks[peaks_idxs][1]] / 4 # 20
            cen2 = x[peaks[peaks_idxs][1]] + 40 # 1625
            sigma2 = 0.5
            
        popt_2gauss, pcov_2gauss = scipy.optimize.curve_fit(_2lorentzian, x, y_bsl, p0=[amp1, cen1, sigma1, amp2, cen2, sigma2])
        pars_2 = popt_2gauss[0:3]
        pars_3 = popt_2gauss[3:6]
        fitted_peak_2 = _1lorentzian(x, *pars_2)
        fitted_peak_3 = _1lorentzian(x, *pars_3)

        peaks2, _ = find_peaks(fitted_peak_2)
        results_half2 = peak_widths(fitted_peak_2, peaks2, rel_height=0.5)
        results["peak2_D_position"] = x[peaks2[0]] 
        results["peak2_D_FWHM"] = results_half2[0][0]
        results["peak2_D_height"] = fitted_peak_2[peaks2[0]]
        fitted_curve["peak_2"] = fitted_peak_2

        peaks3, _ = find_peaks(fitted_peak_3)
        results_half3 = peak_widths(fitted_peak_3, peaks3, rel_height=0.5)
        try:
            results["peak3_D_position"] = x[peaks3[0]] 
            results["peak3_D_FWHM"] = results_half3[0][0]
            results["peak3_D_height"] = fitted_peak_3[peaks3[0]]
            fitted_curve["peak_3"] = fitted_peak_3
        except:
            results["peak3_D_position"] = 0
            results["peak3_D_FWHM"] = 0
            results["peak3_D_height"] = 0
            fitted_curve["peak_3"] = 0

        self.fitted_curve = fitted_curve
        return results, fitted_curve
    
    
    
    def Check_fit(self):
        
        if self.ready_data is None or self.fitted_curve is None:
            raise ValueError("You must prepare_data_for_fit and fit_peaks before checking fit")
        
        fig, axs = plt.subplots(1,3, figsize=(18,6))
        x = self.ready_data.index
        axs[0].plot(x, self.fitted_curve['peak_1'])
        axs[0].plot(self.ready_data)
        axs[0].set_xlim(1200,1400)
        
        axs[1].plot(x, self.fitted_curve['peak_2'])
        axs[1].plot(x, self.fitted_curve['peak_3'])
        axs[1].plot(self.ready_data)
        axs[1].set_xlim(1400,1650)
        
        axs[2].plot(x, self.fitted_curve['peak_4'])
        axs[2].plot(self.ready_data)
        axs[2].set_xlim(2500,2800)
        
        plt.show()
