#!/bin/bash

#configuration

export TUTORIAL_DATA=`pwd`

export SUBJECTS_DIR=$TUTORIAL_DATA/buckner_data/tutorial_subjs

cd $SUBJECTS_DIR

#viewing volumes and surfaces in freeview

freeview -v good_output/mri/T1.mgz good_output/mri/wm.mgz good_output/mri/brainmask.mgz good_output/mri/aseg.mgz:colormap=lut:opacity=0.2 -f good_output/surf/lh.white:edgecolor=blue good_output/surf/lh.pial:edgecolor=red good_output/surf/rh.white:edgecolor=blue good_output/surf/rh.pial:edgecolor=red

#viewing surfaces in 3D using freeview

freeview -f  good_output/surf/lh.pial:annot=aparc.annot:name=pial_aparc:visible=0 good_output/surf/lh.pial:annot=aparc.a2009s.annot:name=pial_aparc_des:visible=0 good_output/surf/lh.inflated:overlay=lh.thickness:overlay_threshold=0.1,3::name=inflated_thickness:visible=0 good_output/surf/lh.inflated:visible=0 good_output/surf/lh.white:visible=0 good_output/surf/lh.pial --viewport 3d


