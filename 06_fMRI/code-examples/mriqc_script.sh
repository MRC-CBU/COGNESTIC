#!/bin/bash

# ============================================================
# MRIQC with Apptainer
#
# The script requres step05_mriqc_subjects.sh, unless you define Project_path and subject here manually.
#
# This script uses MRIQC Singularity image
# To get the latest Docker image (or Singluarity/Apptainer) use: 
# docker pull nipreps/mriqc:latest
#
# ============================================================

# ------------------------------------------------------------
# The passed variables from step03_mriqc_subjects.sh
# ------------------------------------------------------------
PROJECT_PATH=($1)
task_id=$SLURM_ARRAY_TASK_ID

# ------------------------------------------------------------
# Get the list of subjects
# ------------------------------------------------------------
SUBJECT_DIRS=("$PROJECT_PATH"/data/sub-*)
SUBJECT_LIST=("${SUBJECT_DIRS[@]##*/}")

#-----------------------------------------------------------
# Index each subject per job array
subject=${SUBJECT_LIST[$task_id]}
echo "Processing subject: $subject"

# ======================================================================
# MRIQC with Apptainer
# ======================================================================
# Load the apptainer module
module load apptainer

apptainer run \
    -B "$PROJECT_PATH":/MyProject \
    /imaging/local/software/singularity_images/mriqc/mriqc-22.0.1.simg \
    /MyProject/data \
    /MyProject/data/derivatives/mriqc/ \
    --work-dir /MyProject/scratch/mriqc/"$subject" \
    participant \
    --participant-label "${subject#sub-}" \
    --float32 \
    --n_procs 16 --mem_gb 24 --ants-nthreads 16 \
    --modalities T1w bold \
    --no-sub

# Unload the apptainer module    
module unload apptainer

# EACH LINE EXPLINED:
# attaching our project directory to the Apptainer
# the Apptainer/ex-Singularity file
# our BIDS data directory
# output directory
# --work-dir: path where intermediate results should be stored
# analysis_level (participant or group)
# --participant-label: a list of participant identifiers
# --float32: cast the input data to float32 if it’s represented in higher precision (saves space and improves perfomance)
# --n_procs 16 --mem_gb 24 --ants-nthreads 16: options to handle performance
# --modalities: filter input dataset by MRI type
# --no-sub: turn off submission of anonymized quality metrics to MRIQC’s metrics repository
# ======================================================================