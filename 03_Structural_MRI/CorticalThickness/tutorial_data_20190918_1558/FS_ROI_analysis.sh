#!/bin/bash

#configuration

#setenv TUTORIAL_DATA `pwd`
export TUTORIAL_DATA=`pwd`

#setenv SUBJECTS_DIR $TUTORIAL_DATA/buckner_data/tutorial_subjs/group_analysis_tutorial
export SUBJECTS_DIR=$TUTORIAL_DATA/buckner_data/tutorial_subjs/group_analysis_tutorial

cd $SUBJECTS_DIR

#open FreeSurferColorLUT.txt for inspection alonside the visualisation of the parcellation using the Desikan/Killian in freeview
gedit $FREESURFER_HOME/FreeSurferColorLUT.txt &

#look at automatic parcellation using the Desikan/Killian atlas parcellation for subject 004
freeview -v 004/mri/orig.mgz 004/mri/aparc+aseg.mgz:colormap=lut:opacity=0.4 -f 004/surf/lh.white:annot=aparc.annot

#open aseg.stats for inspection
gedit $SUBJECTS_DIR/004/stats/aseg.stats

#open lh.aparc.stats for inspection
gedit $SUBJECTS_DIR/004/stats/lh.aparc.stats

#create a table of segmentation volumes for the specified subjects
asegstats2table --subjects 004 021 040 067 080 092 --tablefile aseg.vol.table

#create a table of mean thickness for the ROIs in the Desikan/Killian parcellation atlas
aparcstats2table --hemi lh --subjects 004 021 040 067 080 092 --parc aparc --meas thickness -t lh.aparc.thickness.table













