#!/bin/bash
#-----------------------------------------------------------
# The script will run the first_level_script.py script for each subject.
#
# You will need a conda environment that contains the required packages.
#
# Usage:
#   Activate the required conda environment.
#   Configure the variables below and run the script: ./step06_first_level_analysis.sh
#-----------------------------------------------------------

# Your project's root directory
PROJECT_PATH='/imaging/correia/da05/workshops/FaceRecognition'

# Where to save the results
OUT_PATH="$PROJECT_PATH"/results

# Location of the first-level python script
SCRIPT_PATH="$PROJECT_PATH"/code/analysis/first_level_script.py

# Path to the job logs
JOB_DIR="$PROJECT_PATH"/logs/first-level_job_logs

# ----------------------------------------------------------
# Get the subject list 
# ----------------------------------------------------------
SUBJECT_DIRS=("$PROJECT_PATH"/data/sub-*)
SUBJECT_LIST=("${SUBJECT_DIRS[@]##*/}") 
# ----------------------------------------------------------

# CD to the job logs directory
mkdir -p "$JOB_DIR"
cd "$JOB_DIR" || exit

# ----------------------------------------------------------
# Do some checks before submitting the job
# ----------------------------------------------------------
echo "Checking if the project directory exists..."
if [ ! -d "$PROJECT_PATH" ]; then
    echo "Project directory does not exist: $PROJECT_PATH"
    exit 1
fi

echo "Checking if the first-level python script exists..."
# Check if the script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "The script $SCRIPT_PATH does not exist"
    exit
fi

#-----------------------------------------------------------
# Submit job for each subject
#-----------------------------------------------------------

# Couldn't use task array because passing a list as an argument is tricky.
# For loop is fine too.
for sub in "${SUBJECT_LIST[@]}"; do
     sbatch \
        --job-name=first_level \
        --output="$JOB_DIR"/first_level_"${sub}".out \
        --error="$JOB_DIR"/first_level_"${sub}".err \
        "$SCRIPT_PATH" "${PROJECT_PATH}" "${sub}" "${OUT_PATH}"
done