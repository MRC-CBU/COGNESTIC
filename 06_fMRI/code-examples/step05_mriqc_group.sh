#!/bin/bash

# ======================================================================
# MRIQC group level: aggregate individual subject reports
#
# Run this script after running step04_mriqc_subject.sh and all subjects
# have been processed.
#
# ======================================================================

#-----------------------------------------------------------
# Define paths
#-----------------------------------------------------------
# Your project's root directory
PROJECT_PATH='/home/cognestic/COGNESTIC/06_fMRI/FaceRecognition'

# ======================================================================
# MRIQC with Apptainer
# ======================================================================

apptainer run --cleanenv -B "$PROJECT_PATH":/"$PROJECT_PATH" \
    /cognestic/containers/mriqc-22.0.1.simg \
    "$PROJECT_PATH"/data "$PROJECT_PATH"/data/derivatives/mriqc/ \
    --work-dir "$PROJECT_PATH"/scratch/ \
    group \
    --float32 \
    --n_procs 16 --mem_gb 24 \
    --ants-nthreads 16 \
    --modalities T1w bold \
    --no-sub