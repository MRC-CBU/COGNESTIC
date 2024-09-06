#!/bin/bash

#=============================================================================
# fMRIPrep for multiple subjects
#
# Usage:
#   Configure the variables below and run the script: ./step07_fmriprep.sh
#
# =============================================================================

# ------------------------------------------------------------
#
# !FILL IN THE VARIABLES BELOW!
#
# ------------------------------------------------------------

# Your project's root directory
PROJECT_PATH='/imaging/correia/da05/workshops/Wakeman-ds'

# Location of the fmriprep_script bash script
SCRIPT_PATH="$PROJECT_PATH"/code/preprocessing/fmriprep_script.sh

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

echo "Checking if the fmriprep_script.sh exists..."
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "The script $SCRIPT_PATH does not exist"
    exit 1
fi

#-----------------------------------------------------------
# Where to output jobs
#-----------------------------------------------------------
JOB_DIR="$PROJECT_PATH"/scratch/fmriprep_21/job_logs
mkdir -p "$JOB_DIR"
cd "$JOB_DIR" || exit

#-----------------------------------------------------------
# Call to the fmriprep_script for each subject with 1 minute delay
#-----------------------------------------------------------
for d in "$PROJECT_PATH"/data/sub-*/; do
    sid=$(basename "$d")    
    echo "Submitting job for subject: ${sid}"
    sbatch \
        --job-name=fmriprep \
        --time=7-00:00 \
        --cpus-per-task=8 \
        "$SCRIPT_PATH" "${PROJECT_PATH}" "${sid}"

    sleep 1m   # Fmriprep: Workaround for running subjects in parallel https://neurostars.org/t/updated-fmriprep-workaround-for-running-subjects-in-parallel/6677
done