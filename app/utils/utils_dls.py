import pandas as pd 
import os


def extract_data(lines):
    data = dict()
    n=1
    for line in lines:
        if line.startswith('Samplename'):
            data['Samplename'] = line.split('"')[-2].strip()
        elif line.startswith('Temperature [K]'):
            data['Temperature [K]'] = line.split('\t')[-1].split('\n')[0].strip()
        elif line.startswith('Viscosity [cp]'):
            data['Viscosity [cp]'] = line.split('\t')[-1].split('\n')[0].strip()
        elif line.startswith('Refractive Index'):
            data['Refractive Index'] = line.split('\t')[-1].split('\n')[0].strip()    
        elif line.startswith('Wavelength [nm]'):
            data['Wavelength [nm]'] = line.split('\t')[-1].split('\n')[0].strip()   
        elif line.startswith('Angle [°]'):
            data['Angle [°]'] = line.split('\t')[-1].split('\n')[0].strip()    
        elif line.startswith('Duration [s]'):
            data['Duration [s]'] = line.split('\t')[-1].split('\n')[0].strip()
        elif line.startswith('Runs'):
            data['Runs'] = line.split('\t')[-1].split('\n')[0].strip()
        elif line.startswith('Mode'):
            data['Mode'] = line.split('\t')[-1].split('\n')[0].strip()
        elif line.startswith('MeanCR0 [kHz]'):
            data['MeanCR0 [kHz]'] = line.split('\t')[-1].split('\n')[0].strip()
        elif line.startswith('MeanCR1 [kHz]'):
            data['MeanCR1 [kHz]'] = line.split('\t')[-1].split('\n')[0].strip()        
        elif line.startswith('Monitor Diode'):
            data['Monitor Diode'] = line.split('\t')[-1].split('\n')[0].strip()
            
        elif line.startswith('FluctuationFreq. [1/ms]'):
            if n == 1:
                data['Order1 FluctuationFreq. [1/ms]'] = line.split('\t')[-1].split('\n')[0].strip()
            elif n == 2:
                data['Order2 FluctuationFreq. [1/ms]'] = line.split('\t')[-1].split('\n')[0].strip()    
            elif n == 3:
                data['Order3 FluctuationFreq. [1/ms]'] = line.split('\t')[-1].split('\n')[0].strip()

        elif line.startswith('DiffCoefficient [µm²/s]'):
            if n == 1:
                data['Order1 DiffCoefficient [µm²/s]'] = line.split('\t')[-1].split('\n')[0].strip()
            elif n == 2:
                data['Order2 DiffCoefficient [µm²/s]'] = line.split('\t')[-1].split('\n')[0].strip()    
            elif n == 3:
                data['Order3 DiffCoefficient [µm²/s]'] = line.split('\t')[-1].split('\n')[0].strip()
        
        elif line.startswith('Hydrodyn. Radius [nm]'):
            if n == 1:
                data['Order1 Hydrodyn. Radius [nm]'] = line.split('\t')[-1].split('\n')[0].strip()
            elif n == 2:
                data['Order2 Hydrodyn. Radius [nm]'] = line.split('\t')[-1].split('\n')[0].strip()    
            elif n == 3:
                data['Order3 Hydrodyn. Radius [nm]'] = line.split('\t')[-1].split('\n')[0].strip()
            n+=1
            
        elif line.startswith('Expansion Parameter µ2'):
            if n == 3:
                data['Order2 Expansion Parameter µ2'] = line.split('\t')[-1].split('\n')[0].strip()    
            elif n == 4:
                data['Order3 Expansion Parameter µ2'] = line.split('\t')[-1].split('\n')[0].strip()    
        
        elif line.startswith('Expansion Parameter µ3'):
            data['Order3 Expansion Parameter µ3'] = line.split('\t')[-1].split('\n')[0].strip()    
        
    return pd.Series(data)


class extract_DLS:
    
    
    def __init__(self, path):
        self.path = path
        self.all_data = None
        self.data_ready = None
        self.report=None

    def show_report(self):
        return self.report

    def gather_data(self):
        path = self.path
                
        all_data = pd.DataFrame()
        for folder in os.listdir(path):
            new_path = os.path.join(path,folder)
            if os.path.isdir(new_path):
                
                sample_name = folder
                for file in os.listdir(new_path):
                    file_path = os.path.join(new_path,file)       
                    
                    with open(file_path,'r',encoding='ISO-8859-1') as f:
                        lines = f.readlines()
                        data = extract_data(lines)
                        all_data = pd.concat([all_data,data], axis=1)
                        
        self.all_data = all_data
    
    def generate_report(self):
        to_use = self.all_data.T
        
        # format numeric columns
        not_numeric = ['Samplename','Mode']
        cols = to_use.columns.tolist()
        cols.remove('Samplename')
        cols.remove('Mode')

        for col in cols:
            to_use[col] = to_use[col].astype(float)
                    
        self.data_ready = to_use
        
        
        to_use = self.data_ready
        
        col_to_keep = ['Angle [°]','MeanCR0 [kHz]','Order2 FluctuationFreq. [1/ms]',
        'Order2 DiffCoefficient [µm²/s]', 'Order2 Hydrodyn. Radius [nm]',
        'Order2 Expansion Parameter µ2']
        
        recap = to_use.loc[:,['Samplename']+col_to_keep].sort_values(by='Samplename').groupby('Samplename').agg(['mean','std'])
        
        self.recap = recap
    
    def export_xlsx(self):
        
        to_use = self.data_ready
        recap = self.recap
        sample_date = self.path.split("/")[-1]
        
        col_to_keep = ['Angle [°]','MeanCR0 [kHz]','Order2 FluctuationFreq. [1/ms]',
        'Order2 DiffCoefficient [µm²/s]', 'Order2 Hydrodyn. Radius [nm]',
        'Order2 Expansion Parameter µ2']

        with pd.ExcelWriter(f"data/DLS/data_{sample_date}4.xlsx") as writer:        
            
            for sample in to_use.Samplename.value_counts().index:
                _ = to_use.loc[to_use.Samplename == sample, col_to_keep].sort_values(by='Angle [°]')
                _.to_excel(writer,sheet_name=f'{sample}_raw')
                _.groupby('Angle [°]').agg(['mean','std']).to_excel(writer,sheet_name=f'{sample}_mean')
            recap.to_excel(writer,sheet_name=f'recap') 
    