#!/bin/bash

# ============================================================
# This script is used to discover DICOM files using HeuDiConv.
#
# Usage: 
#   1. Activate the conda environment that contains heudiconv and dcm2niix.
#       conda ativate mri 
#   2. cd to the directory where this script is located
#   3. Run the script:
#       ./step02_dicom_to_bids.sh
#  
# ============================================================

# ------------------------------------------------------------
# Define your paths
# ------------------------------------------------------------

# Change directory to the location of this script
cd "$(dirname "$0")" || exit

# Path to the raw DICOM files
DICOM_PATH='../mridata/CBU090962_MR09029' # define either full path or relative to the script

# Location of the output data (it will be created if it doesn't exist)
OUTPUT_PATH='../FaceRecognition/data'

# Subject ID
SUBJECT_ID='15'

# Heuristic file for BIDS conversion
HEURISTIC_FILE='bids_heuristic.py'

# Check if heuristic file exists
if [[ ! -f "$HEURISTIC_FILE" ]]; then
    echo "Heuristic file '$HEURISTIC_FILE' not found!"
    exit 1
fi

# ------------------------------------------------------------
# Run the heudiconv
# ------------------------------------------------------------
heudiconv \
    --files "${DICOM_PATH}" \
    --outdir "${OUTPUT_PATH}" \
    --heuristic "$HEURISTIC_FILE" \
    --subjects "${SUBJECT_ID}" \
    --converter dcm2niix \
    --bids
# ------------------------------------------------------------

# HeudiConv parameters:
# --files: Files or directories containing files to process
# --outdir: Output directory
# --heuristic: Name of a known heuristic or path to the Python script containing heuristic
# --subjects: Subject ID
# --converter : dicom to nii converter (dcm2niix or none)
# --bids: Flag for output into BIDS structure
# 
# For a full list of parameters, see: https://heudiconv.readthedocs.io/en/latest/usage.html 