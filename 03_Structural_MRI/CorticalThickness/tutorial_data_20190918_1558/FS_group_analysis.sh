#!/bin/bash

#configuration

#setenv TUTORIAL_DATA `pwd`
export TUTORIAL_DATA=`pwd`

#setenv SUBJECTS_DIR $TUTORIAL_DATA/buckner_data/tutorial_subjs/group_analysis_tutorial
export SUBJECTS_DIR= $TUTORIAL_DATA/buckner_data/tutorial_subjs/group_analysis_tutorial

cd $SUBJECTS_DIR

mkdir glm_cognestic

cp glm/*.fsgd glm/*.mtx glm_cognestic

cd glm_cognestic


#run preprocessing: resample each subjects' data into a common space

mris_preproc --fsgd gender_age.fsgd  --target fsaverage --hemi lh --meas thickness --out lh.gender_age.thickness.00.mgh

#run preprocessing: apply smoothing (FWHM 10)

mri_surf2surf --hemi lh --s fsaverage --sval lh.gender_age.thickness.00.mgh --fwhm 10 --cortex --tval lh.gender_age.thickness.10.mgh

#GLM analysis

mri_glmfit --y lh.gender_age.thickness.10.mgh --fsgd gender_age.fsgd dods --C lh-Avg-thickness-age-Cor.mtx --surf fsaverage lh --cortex --glmdir lh.gender_age.glmdir

#visualise uncorrected significance map

cd $SUBJECTS_DIR/glm_cognestic

freeview -f $SUBJECTS_DIR/fsaverage/surf/lh.inflated:annot=aparc.annot:annot_outline=1:overlay=lh.gender_age.glmdir/lh-Avg-thickness-age-Cor/sig.mgh:overlay_threshold=4,5 -viewport 3d -layout 1


#clusterwise correction for multiple comparisons

#repeat initial glm analysis but this time using the flag --eres-save which is needed for permutation analysis

mri_glmfit --y lh.gender_age.thickness.10.mgh --fsgd gender_age.fsgd dods --C lh-Avg-thickness-age-Cor.mtx --surf fsaverage lh --cortex --glmdir lh.gender_age.glmdir --eres-save

#run permutation simulations (tipically 1000 folds, but here set to 100 for speed)

mri_glmfit-sim --glmdir lh.gender_age.glmdir --perm 100 4.0 abs --cwp  0.05 --2spaces

#look at the cluster summary 

less lh.gender_age.glmdir/lh-Avg-thickness-age-Cor/perm.th40.abs.sig.cluster.summary

#visualising the clusters in freeview

freeview -f $SUBJECTS_DIR/fsaverage/surf/lh.inflated:overlay=lh.gender_age.glmdir/lh-Avg-thickness-age-Cor/perm.th40.abs.sig.cluster.mgh:overlay_threshold=2,5:annot=lh.gender_age.glmdir/lh-Avg-thickness-age-Cor/perm.th40.abs.sig.ocn.annot -viewport 3d -layout 1









