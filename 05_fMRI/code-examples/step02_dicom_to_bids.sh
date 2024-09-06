#!/bin/bash

# ============================================================
# This script is used to discover DICOM files using HeuDiConv.
#
# Usage: ./step01_dicom_discover.sh
# 
# It is assumed that you have a conda environment called 'mri' available (check with 'conda env list'). 
# If not, create a conda environment with the heudiconv and dcm2niix packages installed.
# For example: 
# ============================================================

# ------------------------------------------------------------
# Define your paths
# ------------------------------------------------------------

# Path to the raw DICOM files
DICOM_PATH='../mridata/CBU090928_MR09029'

# Location of the output data (it will be created if it doesn't exist)
OUTPUT_PATH="../FaceProcessing/data"

# Subject ID
SUBJECT_ID='04'

HEURISTIC_FILE="bids_heuristic.py"

# ------------------------------------------------------------
# Activate the mri environment (or any other environment with heudiconv installed)
# ------------------------------------------------------------
#conda activate mri

# ------------------------------------------------------------
# Run the heudiconv
# ------------------------------------------------------------
heudiconv \
    --files "${DICOM_PATH}"/*/*/*.dcm \
    --outdir "${OUTPUT_PATH}" \
    --heuristic "$HEURISTIC_FILE" \
    --subjects "${SUBJECT_ID}" \
    --converter dcm2niix \
    --bids \
    --overwrite
# ------------------------------------------------------------

# Deactivate the conda environment
#conda deactivate