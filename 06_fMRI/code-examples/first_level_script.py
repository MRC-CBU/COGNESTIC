#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================================================================
# Dace Apšvalka (MRC CBU 2026)
# Subject-level fMRI analysis using Nilearn
# 
# Example usage:
#   python first_level_script.py /path/to/bids/dataset sub-01 /path/to/output
# 
# Or use step07_first_level_analysis.sh for batch processing of multiple subjects using SLURM.
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
from nilearn.interfaces.fmriprep import load_confounds
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

# t-contrast definitions for the first-level model
contrast_definitions = {
    "Faces_Scrambled": {
        "positive_patterns": ["FF", "UF"],
        "negative_patterns": ["SF"],
    },
    "DelFF": {
        "positive_patterns": ["DelFF"],
    },
    "DelSF": {
        "positive_patterns": ["DelSF"],
    },
    "DelUF": {
        "positive_patterns": ["DelUF"],
    },
    "ImmFF": {
        "positive_patterns": ["ImmFF"],
    },
    "ImmSF": {
        "positive_patterns": ["ImmSF"],
    },
    "ImmUF": {
        "positive_patterns": ["ImmUF"],
    },
    "IniFF": {
        "positive_patterns": ["IniFF"],
    },
    "IniSF": {
        "positive_patterns": ["IniSF"],
    },
    "IniUF": {
        "positive_patterns": ["IniUF"],
    },
    
}

# Conditions for the effects of interest F-contrast
conditions_of_interest = [
    "DelFF", "DelSF", "DelUF",
    "ImmFF", "ImmSF", "ImmUF",
    "IniFF", "IniSF", "IniUF",
]

# ======================================================================
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

# --- Get the brain mask
brain_mask = layout.get(
    subject=sID, 
    datatype='anat', 
    suffix='mask', 
    desc='brain', 
    space='MNI152NLin6Asym', 
    res='9',
    extension='.nii.gz',
    return_type='filename'
    )

print("Found " + str(len(brain_mask)) + " brain mask files")

# Check if any of the required data is missing
if len(bold) == 0 or len(events) == 0 or len(brain_mask) == 0:
    print("ERROR: Missing required data (BOLD, events, or brain mask) for subject " + sID)
    print("BOLD files: " + str(len(bold)))
    print("Event files: " + str(len(events)))
    print("Brain mask files: " + str(len(brain_mask)))
    sys.exit(1)


# --- Define which confounds to include in the GLM
confounds_for_glm, sample_masks = load_confounds(
    bold, # list of fMRIPrep-preprocessed BOLD files
    strategy=("motion",), # can be multiple strategies
    motion="basic"
)
# Prepare sample masks for FirstLevelModel.fit()
if all(mask is None for mask in sample_masks):
    sample_masks_for_glm = None
else:
    sample_masks_for_glm = [
        np.arange(len(confounds), dtype=int)
        if mask is None
        else mask
        for confounds, mask in zip(confounds_for_glm, sample_masks)
    ]

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
fmri_glm = fmri_glm.fit(
    bold, 
    events=events, 
    confounds=confounds_for_glm,
    sample_masks=sample_masks_for_glm
    )

# --- Get the design matrices
design_matrices = fmri_glm.design_matrices_

# --- Create contrasts 
# t-contrast helper function
def create_contrast_vector(
    design_matrix,
    include_patterns=None,
    exclude_patterns=None,
    positive_patterns=None,
    negative_patterns=None,
):
    """
    Create a contrast vector based on design-matrix column-name patterns.

    Positive columns are assigned weights summing to +1.
    Negative columns are assigned weights summing to -1.

    Thus, when both sets are present, the contrast represents:
        mean(positive conditions) - mean(negative conditions)

    Parameters
    ----------
    design_matrix : pandas.DataFrame
        Design matrix for one run.

    include_patterns : list of str, optional
        If supplied, matching columns must also contain at least one of
        these patterns.

    exclude_patterns : list of str, optional
        Matching columns containing any of these patterns are excluded.

    positive_patterns : list of str, optional
        Patterns identifying regressors receiving positive weights.

    negative_patterns : list of str, optional
        Patterns identifying regressors receiving negative weights.

    Returns
    -------
    contrast_vector : numpy.ndarray
        Contrast vector with one value per design-matrix column.
    """
    column_names = design_matrix.columns
    contrast_vector = np.zeros(len(column_names), dtype=float)

    def find_matching_columns(patterns):
        if not patterns:
            return []

        matches = []

        for index, column_name in enumerate(column_names):
            if not any(pattern in column_name for pattern in patterns):
                continue

            if include_patterns and not any(
                pattern in column_name for pattern in include_patterns
            ):
                continue

            if exclude_patterns and any(
                pattern in column_name for pattern in exclude_patterns
            ):
                continue

            matches.append(index)

        return matches

    positive_cols = find_matching_columns(positive_patterns)
    negative_cols = find_matching_columns(negative_patterns)

    overlapping_cols = set(positive_cols) & set(negative_cols)
    if overlapping_cols:
        overlapping_names = [
            column_names[index] for index in sorted(overlapping_cols)
        ]
        raise ValueError(
            "Some columns match both the positive and negative patterns: "
            f"{overlapping_names}"
        )

    if positive_patterns and not positive_cols:
        raise ValueError(
            "No design-matrix columns matched the positive patterns."
        )

    if negative_patterns and not negative_cols:
        raise ValueError(
            "No design-matrix columns matched the negative patterns."
        )

    if positive_cols:
        contrast_vector[positive_cols] = 1 / len(positive_cols)

    if negative_cols:
        contrast_vector[negative_cols] = -1 / len(negative_cols)

    return contrast_vector

# F-contrast helper function
def create_effects_of_interest_matrix(
    design_matrix,
    conditions_of_interest,
):
    """Create an F-contrast testing all conditions of interest."""

    missing_conditions = [
        condition
        for condition in conditions_of_interest
        if condition not in design_matrix.columns
    ]

    if missing_conditions:
        raise ValueError(
            "Conditions missing from the design matrix: "
            f"{missing_conditions}"
        )

    return np.vstack([
        (design_matrix.columns == condition).astype(float)
        for condition in conditions_of_interest
    ])

# Generate the t-contrast vectors
contrasts = {}

for contrast_name, parameters in contrast_definitions.items():
    print(f"\nCreating contrast: {contrast_name}")

    contrast_vectors = [
        create_contrast_vector(
            design_matrix,
            **parameters,
        )
        for design_matrix in design_matrices
    ]

    contrasts[contrast_name] = contrast_vectors
    
    # Add the effects of interest F-contrast
    contrasts["EffectsOfInterest"] = [
    create_effects_of_interest_matrix(
        design_matrix,
        conditions_of_interest,
    )
    for design_matrix in design_matrices
    ]

    
# --- Compute the contrasts and save the results
for contrast_id in contrasts.keys():   
    if contrast_id == 'EffectsOfInterest':
        stats = 'z_score' 
    else:
        stats = 'effect_size'
    stats_map = fmri_glm.compute_contrast(
        contrasts[contrast_id], 
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
        "ConfoundsIncluded": confounds_for_glm[0].columns.tolist(),
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