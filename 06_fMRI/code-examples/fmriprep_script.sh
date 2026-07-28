#!/bin/sh

# ============================================================
# This script uses fmriprep Apptainer image
# To get the latest Docker image (or Singluarity/Apptainer) use: 
# docker pull nipreps/fmriprep:<latest-version>
# ============================================================

PROJECT_PATH=${1}
subject=${2}

#-----------------------------------------------------------
# Add some info to the job output at the start
#-----------------------------------------------------------
# processing start time
start=$(date +%s)
date
echo Submitted subject: "$subject"

# ======================================================================
# FMRIPrep with Apptainer
# ======================================================================

# Load the apptainer module
module load apptainer

# See the possible fmriprep arguments here: https://fmriprep.org/en/stable/usage.html

apptainer run \
    -B "$PROJECT_PATH":/MyProject \
    /imaging/local/software/singularity_images/fmriprep/fmriprep-24.1.1.sif \
    /MyProject/data \
    /MyProject/data/derivatives/fmriprep\
    participant \
    --fs-license-file /MyProject/freesurfer_license.txt \
    --work-dir /MyProject/scratch/fmriprep \
    --participant-label "$subject" \
    --output-spaces MNI152NLin6Asym:res-2 \
    --fs-no-reconall \
    --nthreads 16 --omp-nthreads 8 \
    --skip-bids-validation \
    --stop-on-first-crash

# Unload the apptainer module    
module unload apptainer

#-----------------------------------------------------------
# Add some info to the job output at the end
#-----------------------------------------------------------
end=$(date +%s)
echo Time elapsed: "$(TZ=UTC0 printf '%(%H:%M:%S)T\n' $((end - start)))"
