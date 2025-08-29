#!/bin/bash

# ============================================================
# MRIQC for multiple subjects
#
# This script is used to get MRI quality metrics for multiple subjects using MRIQC tool.
# The script calls the 'mriqc_script.sh' bash script for each subject in the "$PROJECT_PATH"/data/sub-*.
#
# Usage:
#   Configure the variables below and run the script: ./step04_mriqc_subjects.sh
#
# ============================================================

# ------------------------------------------------------------
#
# !FILL IN THE VARIABLES BELOW!
#
# ------------------------------------------------------------

# Your project's root directory
PROJECT_PATH='/imaging/correia/da05/workshops/FaceRecognition'

# Location of the mriqc_script bash script
SCRIPT_PATH="$PROJECT_PATH"/code/preprocessing/mriqc_script.sh

# ------------------------------------------------------------
#
# You don't have to change anything below this line!
#
# ------------------------------------------------------------

# ------------------------------------------------------------
# Do some checks before running the script
# ------------------------------------------------------------
echo "Checking if the project directory exists..."
if [ ! -d "$PROJECT_PATH" ]; then
    echo "Project directory does not exist: $PROJECT_PATH"
    exit 1
fi

echo "Checking if the mriqc_script.sh exists..."
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "The script $SCRIPT_PATH does not exist"
    exit 1
fi

#-----------------------------------------------------------
# Get the list of subject for this project
#----------------------------------------------------------- 
SUBJECT_DIRS=("$PROJECT_PATH"/data/sub-*)
# Get the number of directories in the array
n_subjects=${#SUBJECT_DIRS[@]}

# If there are no subjects, exit the script
if [ "$n_subjects" -eq 0 ]; then
    echo "No subjects found in the data directory: $PROJECT_PATH/data"
    exit 1
fi
echo "Found $n_subjects subjects in the data directory."
echo "Submitting jobs..."

#-----------------------------------------------------------
# Where to output job logs
#-----------------------------------------------------------
JOB_DIR="$PROJECT_PATH"/logs/mriqc_job_logs
mkdir -p "$JOB_DIR"
cd "$JOB_DIR" || exit
echo "Outputting job logs to: $JOB_DIR"

# ------------------------------------------------------------
# Submit job tasks for each subject
# ------------------------------------------------------------
sbatch \
    --array=0-$((n_subjects - 1)) \
    --job-name=mriqc \
    --cpus-per-task=16 \
    --time=8:00:00 \
    "$SCRIPT_PATH" "$PROJECT_PATH"