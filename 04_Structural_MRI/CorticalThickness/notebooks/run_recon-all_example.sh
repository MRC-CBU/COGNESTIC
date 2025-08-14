!#/bin/bash

export SUBJECTS_DIR=/home/cognestic/COGNESTIC/03_Structural_MRI/CorticalThickness/LiveDemo/FS_SUBJECTS_DIR


recon-all -i bids/sub-CBU130685/anat/CBU130685_CBU_MPRAGE_32chn_20130720140423_3.nii -subject sub_CBU130685 -all 
