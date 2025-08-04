#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================================================================
# Dace Apšvalka (MRC CBU 2025)
# Subject-level fMRI analysis using Nilearn
# 
# This script requres step06_first_level_analysis.sh, unless you define ds, sID, 
# and output here manually 
#
# ======================================================================

# ======================================================================
# IMPORT REQUIRED PACKAGES
# ======================================================================
import os
import sys
import pandas as pd
import numpy as np
from bids.layout import BIDSLayout
from nilearn.glm.first_level import FirstLevelModel
import time
import warnings
warnings.filterwarnings("ignore")

# ======================================================================
# DEFINE PATHS
# arguments passed from step06_first_level_analysis.sh
# ======================================================================

ds = sys.argv[1] # dataset location
sID = sys.argv[2].split("sub-")[1] # subject id
output = sys.argv[3]

# ds = '/imaging/correia/da05/workshops/FaceRecognition'
# sID = '01'
# output = '/imaging/correia/da05/workshops/FaceRecognition/results_3mm'

# ======================================================================
print("Running first-level analysis for subject " + sID)
start_time = time.time()
print("Started at: " + time.strftime("%H:%M:%S", time.localtime()))

# ======================================================================
# DEFINE PARAMETERS
# =====================================================================
model_name = 'first-level'

bids_path = os.path.join(ds, 'data')

outdir = os.path.join(output, model_name, 'sub-' + sID)
if not os.path.exists(outdir):
    os.makedirs(outdir)

print("BIDS data location: " + bids_path)
print("Output directory: " + outdir)

# ======================================================================
# PERFORM SUBJECT LEVEL GLM ANALYSIS
# ======================================================================

# --- Initialize the BIDS layout and include the derivatives in it
# layout = BIDSLayout(bids_path, derivatives=True)
layout = BIDSLayout(bids_path, derivatives=False)
layout.add_derivatives(os.path.join(ds, 'data', 'derivatives', 'fmriprep'))

# --- Get the preprocessed functional files
bold = layout.get(
    subject=sID, 
    datatype='func', 
    space='MNI152NLin6Asym', 
    res='9',
    desc='preproc', 
    extension='.nii.gz',
    return_type='filename'
    )
print("Found " + str(len(bold)) + " preprocessed functional files")
print("Preprocessed functional files:")
print(*bold, sep="\n")

# --- Get the event files
events = layout.get(
    subject=sID, 
    datatype='func', 
    suffix='events', 
    extension=".tsv", 
    return_type='filename'
    )
print("Found " + str(len(events)) + " event files")

# --- Get the confounds and select which ones to include in the design
confounds = layout.get(
    subject=sID, 
    datatype='func', 
    desc='confounds', 
    extension=".tsv", 
    return_type='filename'
    )
print("Found " + str(len(confounds)) + " confounds files")

# --- Get the brain mask
brain_mask = layout.get(
    subject=sID, 
    datatype='func', 
    suffix='mask', 
    desc='brain', 
    space='MNI152NLin6Asym', 
    res='9',
    extension='.nii.gz',
    return_type='filename'
    )

print("Found " + str(len(brain_mask)) + " brain mask files")

# Check if any of the required data is missing
if len(bold) == 0 or len(events) == 0 or len(confounds) == 0 or len(brain_mask) == 0:
    print("ERROR: Missing required data (BOLD, events, confounds files, or brain mask) for subject " + sID)
    print("BOLD files: " + str(len(bold)))
    print("Event files: " + str(len(events)))
    print("Confound files: " + str(len(confounds)))
    print("Brain mask files: " + str(len(brain_mask)))
    sys.exit(1)

# --- Define which confounds to include in the GLM
confounds_of_interest = ['trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z']

# --- For each run, load the confounds and select the ones of interest
confounds_glm = []
for conf_file in confounds:
    this_conf = pd.read_table(conf_file)
    # only include the confounds of interest that are present in the file
    confounds_of_interest = [conf for conf in confounds_of_interest if conf in this_conf.columns]
    # select the confounds of interest and fill NaN with 0    
    conf_subset = this_conf[confounds_of_interest].fillna(0) # replace NaN with 0
    confounds_glm.append(conf_subset)

# --- Get the TR value
TR = layout.get_tr()

# --- If slice timing correction was applied, get the slice time reference
slice_timing = layout.get_metadata(bold[0])
if slice_timing['SliceTimingCorrected']:
  slice_time_ref = slice_timing['StartTime'] / TR
else:
  slice_time_ref = 0

# --- Define the GLM model
fmri_glm = FirstLevelModel(
    t_r = TR,
    slice_time_ref = slice_time_ref, 
    hrf_model = 'SPM',
    drift_model = 'cosine',
    high_pass = 0.01,
    noise_model = 'ar1',
    smoothing_fwhm = 6, 
    mask_img = brain_mask[0]
    )

# --- Fit the model
fmri_glm = fmri_glm.fit(bold, events, confounds_glm)

# --- Get the design matrices
design_matrices = fmri_glm.design_matrices_

# --- Create contrasts 
events_df = pd.read_table(events[0])
unique_conditions = events_df['trial_type'].unique()

contrast_list = []
nruns = len(design_matrices)

for design_matrix in design_matrices:
    n_columns = design_matrix.shape[1]  # number of predictors in the model
    column_names = design_matrix.columns  # get the names of the columns
    
    # Create an empty dictionary to store contrasts for all conditions
    contrasts = {}
    
    # ------------------------------------------------------------------
    # Create a contrast vector for each condition
    # ------------------------------------------------------------------
    for condition in unique_conditions:
        # Initialize the contrast vector with zeros
        contrast_vector = np.zeros(n_columns)
        
        # Assign 1 to the columns that correspond to the current condition and scale by the number of runs
        for i, col_name in enumerate(column_names):
            if col_name.startswith(condition):
                contrast_vector[i] = 1/nruns
        
        # Store the contrast for the current condition
        contrasts[condition] = contrast_vector
        
    # ------------------------------------------------------------------
    # Create contrast for Faces > Scrambled
    # ------------------------------------------------------------------
    # Calculate the number of "Faces" and "Scrambled" conditions
    num_faces = sum(1 for col_name in column_names if col_name.endswith(('FF', 'UF')))
    num_scrambled = sum(1 for col_name in column_names if col_name.endswith('SF'))
    
    # Initialize the contrast vector with zeros
    contrast_vector = np.zeros(n_columns)
    
    # Assign weights to the contrast vector
    for i, col_name in enumerate(column_names):
        if col_name.endswith(('FF', 'UF')):
            contrast_vector[i] = 1 / num_faces /nruns # weigh the faces conditions
        elif col_name.endswith('SF'):
            contrast_vector[i] = -1 / num_scrambled/nruns  # weigh the scrambled conditions
    
    contrasts['FacesScrambled'] = contrast_vector
    
    # ------------------------------------------------------------------
    # Create effects of interest contrast
    # ------------------------------------------------------------------
    contrasts['EffectsOfInterest'] = np.eye(n_columns)[:len(unique_conditions)]
    
    # Append all contrasts for this design matrix
    contrast_list.append(contrasts)
    
# --- Compute the contrasts and save the results
for contrast_id in contrast_list[0].keys():   
    if contrast_id == 'EffectsOfInterest':
        stats = 'z_score' 
    else:
        stats = 'effect_size'
    stats_map = fmri_glm.compute_contrast(
        [c[contrast_id] for c in contrast_list], 
        output_type = stats)
    # Save results following BIDS standart
    res_name = os.path.basename(bold[0]).split("run")[0]
    # from stats get only the part before _ for the BIDS file name
    stats_suffix = stats.split("_")[0]
    # in contrast_id remove underscores
    contrast_id = contrast_id.replace("_", "")
    # Save the result
    stats_map.to_filename(os.path.join(outdir, res_name + 'desc-' + contrast_id + '_' + stats_suffix + '.nii.gz'))

# ======================================================================
# CREATE THIS MODEL'S dataset_description.json FILE
# This is needed to use the results directory as BIDS data. 
# We will save our model parameters in the file as well, which is very useful.
# ======================================================================

jason_file = os.path.join(output, model_name, "dataset_description.json")

if not os.path.exists(jason_file):
    import json
    import datetime
    from importlib.metadata import version

    bids_version = layout.get_dataset_description()['BIDSVersion']
    nilearn_version = version('nilearn')
    date_created = datetime.datetime.now()
    
    # Data to be written
    content = {
        "Name": "First-level GLM analysis",
        "BIDSVersion": bids_version,
        "DatasetType": "results",
        "GeneratedBy": [
            {
                "Name": "Nilearn",
                "Version": nilearn_version,
                "CodeURL": "https://nilearn.github.io"
            }
        ],    
        "Date": date_created,
        "ConfoundsIncluded": confounds_of_interest,
        "FirstLevelModel": [
            fmri_glm.get_params()
        ], 
    }
    
    # Serializing json
    json_object = json.dumps(content, indent=4, default=str)
    
    # Writing to .json
    with open(jason_file, "w") as outfile:
        outfile.write(json_object)

# ======================================================================
print("Finished first-level analysis for subject " + sID)
print("Finished at: " + time.strftime("%H:%M:%S", time.localtime()))
print("Processing time: " + str(round((time.time() - start_time)/60, 2)) + " minutes")