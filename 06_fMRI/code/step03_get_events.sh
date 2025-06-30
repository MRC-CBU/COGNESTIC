#!/bin/bash
# This script downloads event files for a specific subject from the OpenNeuro dataset ds000117.

# -----------------------------------------------------------------------
# Specify the parameters for downloading event files
# -----------------------------------------------------------------------
BIDSPATH="../FaceRecognition/data"
runs_to_download=$(seq -w 01 09)
subject_id="sub-15"


# -----------------------------------------------------------------------
# The output path for the event files
OUTPUT_PATH="${BIDSPATH}/${subject_id}/ses-mri/func"

# Check if the output directory exists; exit otherwise
if [ ! -d "${OUTPUT_PATH}" ]; then
    echo "Output directory ${OUTPUT_PATH} does not exist. Please run the previous steps first."
    exit 1
fi

# Download the event files for the specified subject and runs
echo "Downloading event files for ${subject_id}..."

for run in $runs_to_download; do

    output_file="${OUTPUT_PATH}/${subject_id}_ses-mri_task-facerecognition_run-${run}_events.tsv"

    echo "Downloading run-${run}..."

    curl --create-dirs \
    "https://s3.amazonaws.com/openneuro.org/ds000117/${subject_id}/ses-mri/func/${subject_id}_ses-mri_task-facerecognition_run-${run}_events.tsv" \
    -o "${output_file}" || { echo "Failed to download run-${run}"; exit 1; }

done

echo "Event files downloaded successfully."
# -----------------------------------------------------------------------