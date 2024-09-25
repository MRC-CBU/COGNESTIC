#!/bin/bash

# ============================================================
# MRIQC with Apptainer
#
# Pull the Docker image
# apptainer pull docker://nipreps/mriqc
#
# ============================================================

PROJECT_PATH="/mnt/c/COGNESTIC/05_fMRI/FaceProcessing"
sid="04"

apptainer run \
    -B "$PROJECT_PATH":/MyProject \
    /mnt/c/COGNESTIC/apptainer_images/mriqc_v24.1.0.sif \
    /MyProject/data \
    /MyProject/data/derivatives/mriqc/ \
    --work-dir /MyProject/scratch/mriqc/sub-"$sid" \
    participant \
    --participant_label $sid \
    --float32 \
    --n_procs 16 --mem_gb 24 --ants-nthreads 16 \
    --modalities T1w bold \
    --no-sub