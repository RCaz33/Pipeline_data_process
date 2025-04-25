# 📊 Aggregate & Preprocess Raman and DLS Data

This project provides a **Streamlit web interface** and **data processing backend** to prepare **Raman spectroscopy** and **Dynamic Light Scattering (DLS)** data for analysis. It supports **visualization, filtering, peak fitting**, and **report generation**, all within a user-friendly app deployable via Docker.

---

## 🧬 Data Flow Overview

### 🔬 Raman Workflow
1. Upload CSV files from folder
2. Reclassify spectra
3. Visualize individual spectra
4. Select signal-to-noise cutoff
5. Aggregate all valid spectra
6. Smooth spectra (SavGol filter: `window_length=20`, `polyorder=3`)
7. Correct baseline (SNIP: `max_half_window=40`, `decreasing=True`, `smooth_half_window=3`)
8. Identify peak regions
9. Define fitting parameters
10. Fit with **Gaussian** / **Lorentzian** models
11. Extract peak features
12. Display fit results
13. Export processed data

### 💧 DLS Workflow
1. Traverse folder of sample `.xlsx` files
2. Extract raw data from each report
3. Aggregate data into unified DataFrame
4. Visualize distributions
5. Export summary Excel file

---

## 🖥️ Application Structure

```bash
/app
│
├── pages/
│   ├── 1_manuel.py           # Guide: how to use app & endpoints
│   ├── 2_Process_Raman.py    # Raman page: upload → filter → fit → export
│   └── 3_Ag_DLS.py           # DLS page: upload → extract → aggregate → export
│
└── utils/
    ├── data_processing.py    # Raman processing functions and classes
    │   ├── generate_graph()
    │   ├── _1gaussian(), _1lorentzian()
    │   ├── deconvolution helpers
    │   └── Raman_Spectra class
    └── utils_dls.py          # DLS processing helpers
        ├── extract_data()
        └── extract_DLS class
```

---

## 🚀 Getting Started with Docker

### 🔧 Installation Steps
1. **Pull** the project from GitHub  
2. Navigate to the `/app` directory  
3. Build the Docker image:

```bash
docker build -t <YOUR_IMAGE_NAME> .
```

4. Prepare for run:
   - Map a **volume** for file persistence:  
     `-v /your/host/path:/app/container/path`
   - Map a **port** for app access:  
     `-p <host_port>:8501`

5. Start the container:

```bash
docker run -d -p 8008:8501 -v "/mnt/your/local/path":/app/container/path <YOUR_IMAGE_NAME>
```

---

## 📚 How to Use

Once the container is running, open your browser at:

```
http://localhost:8008
```

- Use **Page 1** for usage instructions
- Use **Page 2** to process Raman data
- Use **Page 3** to process DLS reports

---

## 📤 Output

- Peak fitting results (CSV/Excel)
- Summary reports for DLS
- Visualization of fits and distributions

---

## 🛠 Dependencies

This app uses:

- `streamlit`
- `numpy`, `pandas`, `scipy`, `sklearn`
- `matplotlib`, `seaborn`
- `openpyxl`
- `os`, `glob`, `re` (for file handling)

All dependencies are baked into the Docker image.

---

## 📄 License

This project is licensed under the MIT License.
