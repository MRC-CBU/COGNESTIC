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
DICOM_PATH='mridata/CBU090928_MR09029'

# Location of the output data (it will be created if it doesn't exist)
OUTPUT_PATH="FaceProcessing/scratch/dicom_discovery"

# Subject ID
SUBJECT_ID='04'

# ------------------------------------------------------------
# Activate the mri environment (or any other environment with heudiconv installed)
# ------------------------------------------------------------
conda activate mri

# ------------------------------------------------------------
# Run the heudiconv
# ------------------------------------------------------------
heudiconv \
    --files "${DICOM_PATH}"/*/*/*.dcm \
    --outdir "${OUTPUT_PATH}" \
    --heuristic convertall \
    --subjects "${SUBJECT_ID}" \
    --converter none \
    --bids \
    --overwrite
# ------------------------------------------------------------

# Deactivate the conda environment
conda deactivate

cp "${OUTPUT_PATH}"/.heudiconv/"${SUBJECT_ID}"/info/dicominfo.tsv "${OUTPUT_PATH}"