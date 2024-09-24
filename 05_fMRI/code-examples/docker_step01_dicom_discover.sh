#!/bin/bash

DICOM_PATH="/mnt/c/COGNESTIC/05_fMRI/mridata/CBU090928_MR09029/20090824_164906"
PROJECT_PATH="/mnt/c/COGNESTIC/05_fMRI/FaceProcessing"

sid="04"

docker run --rm -it \
    -v $DICOM_PATH:/DICOM_PATH \
    -v $PROJECT_PATH:/MyProject \
    nipy/heudiconv \
    --files /DICOM_PATH \
    --outdir /MyProject/scratch/dicom_discovery/ \
    --heuristic convertall\
    --subjects $sid \
    --converter none \
    --bids \
    --overwrite