#!/bin/bash

# ============================================================
# MRIQC with Docker
#
# Pull the Docker image
# docker pull nipreps/mriqc
#
# ============================================================

PROJECT_PATH="/mnt/c/COGNESTIC/05_fMRI/FaceProcessing"

docker run --rm -it \
    -v $PROJECT_PATH:/MyProject \
    nipreps/mriqc \
    /MyProject/data \
    /MyProject/data/derivatives/mriqc/ \
    group \
    --work-dir /MyProject/scratch/mriqc/ \
    --float32 \
    --n_procs 16 --mem_gb 24 --ants-nthreads 16 \
    --modalities T1w bold \
    --no-sub