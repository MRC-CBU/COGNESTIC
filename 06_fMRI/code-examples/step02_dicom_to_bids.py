"""
This script converts DICOM files to BIDS format using HeuDiConv.

Usage: 
  1. Activate the conda environment: conda activate mri 
  2. Run the script: python step02_dicom_to_bids.py
"""

import subprocess
import os

# Change to the directory where this script is located
script_directory = os.path.dirname(__file__)
os.chdir(script_directory)

# ------------------------------------------------------------
# Define your paths
# ------------------------------------------------------------

# Path to the raw DICOM files
DICOM_PATH = '../mridata/CBU090962_MR09029' # define either full path or relative to the script

# Location of the output data (it will be created if it doesn't exist)
OUTPUT_PATH = '../FaceRecognition/data'

# Subject ID
SUBJECT_ID = '15'

# Heuristic file for BIDS conversion
HEURISTIC_FILE = 'bids_heuristic.py'

# Check if heuristic file exists
if not os.path.exists(HEURISTIC_FILE):
    print(f"Error: Heuristic file '{HEURISTIC_FILE}' not found!")
    exit()

# ------------------------------------------------------------
# Run heudiconv
# ------------------------------------------------------------

# Bash command to run heudiconv
command = [
    'heudiconv',
    '--files', DICOM_PATH,
    '--outdir', OUTPUT_PATH,
    '--heuristic', HEURISTIC_FILE,
    '--subjects', SUBJECT_ID,
    '--converter', 'dcm2niix',
    '--bids'
]

print("Running command:", ' '.join(command))

# Run the command
subprocess.run(command)
