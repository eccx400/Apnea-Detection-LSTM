# End-to-End Sleep Apnea Prediction using LSTM 
***
This is a end-to-end apnea detection program using LSTM and built in to a Django webapp, which performs the following steps:
Preprocessing:
   - data normalization, visualization, flatline extraction to generate dataset for training/testing
Training/Inference

## File structure
```
data/:  includes all dataset files (note: raw data files must be of the form <dataset>_<apnea_type>_ex<excerpt>_sr<sample_rate>_sc<scale_factor>.txt
info/:  metadata
neurostim/: django webapp 
flatline_detection.py: flatline detection algorithm
lstm.py: ML model and training/testing
```

 * data/
   * dreams/
       * preprocessing/
          * excerpt1/
            * dreams_osa_ex1_sr8_sc1.txt
          * excerpt2/
       * postprocessing/
          * excerpt1/
            * positive
            * negative
          * excerpt2/
   * mit/
   * dublin/
   * patch/
 * info/
 * neurostim/
 * README.md

- Datasets supported: mit, dreams, ucddb, patch
- types of apnea: obstructive sleep apnea (osa), hypopnea (osahs)



## Installation
 ```bash
 git clone https://github.com/vccheng2001/Apnea-Detection-LSTM.git
 cd Apnea-Detection-LSTM/ 
 git checkout upgrade
 pip3 install -r requirements.txt  (install all dependencies)
 ```
 
## Running the webapp locally
 ```bash

 cd apnea_detection
 cd neurostim
 python3 manage.py runserver 
 
 ```
 
 
