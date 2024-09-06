#!/bin/sh

# ============================================================
# This script requires step07_fmriprep.sh, unless you define PROJECT_PATH
# and subject here manually 
#
# This script uses fmriprep Singularity image
# To get the latest Docker image (or Singluarity/Apptainer) use: 
# docker pull nipreps/fmriprep:<latest-version>
# ============================================================


#-----------------------------------------------------------
# The passed variables from step07_fmriprep.sh
#-----------------------------------------------------------
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
# FMRIPrep with Singularity
# ======================================================================

# See the possible fmriprep arguments here: https://fmriprep.org/en/stable/usage.html

singularity run \
    -B "$PROJECT_PATH":/MyProject \
    /imaging/local/software/singularity_images/fmriprep/fmriprep-21.0.1.simg \
    /MyProject/data \
    /MyProject/data/derivatives/fmriprep\
    participant \
    --fs-license-file /MyProject/code/freesurfer_license.txt \
    --work-dir /MyProject/scratch/fmriprep \
    --participant-label "$subject" \
    --output-spaces MNI152NLin2009cAsym:res-2 \
    --dummy-scans 2 \
    --fs-no-reconall \
    --nthreads 16 --omp-nthreads 8 \
    --skip-bids-validation \
    --stop-on-first-crash

#-----------------------------------------------------------
# Add some info to the job output at the end
#-----------------------------------------------------------
end=$(date +%s)
echo Time elapsed: "$(TZ=UTC0 printf '%(%H:%M:%S)T\n' $((end - start)))"
