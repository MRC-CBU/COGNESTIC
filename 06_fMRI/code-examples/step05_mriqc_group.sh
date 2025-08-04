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
PROJECT_PATH='/imaging/correia/da05/workshops/FaceRecognition'

# ======================================================================
# MRIQC with Apptainer
# ======================================================================
# Load the apptainer module
module load apptainer

apptainer run --cleanenv -B "$PROJECT_PATH":/"$PROJECT_PATH" \
    /imaging/local/software/singularity_images/mriqc/mriqc-22.0.1.simg \
    "$PROJECT_PATH"/data "$PROJECT_PATH"/data/derivatives/mriqc/ \
    --work-dir "$PROJECT_PATH"/scratch/ \
    group \
    --float32 \
    --n_procs 16 --mem_gb 24 \
    --ants-nthreads 16 \
    --modalities T1w bold \
    --no-sub

# Unload the apptainer module    
module unload apptainer