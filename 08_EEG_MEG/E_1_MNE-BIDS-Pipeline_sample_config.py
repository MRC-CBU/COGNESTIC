import mne
import os

demo_data_root = os.path.join("/home", "cognestic", "Desktop", "COGNESTIC", "08_EEG_MEG", "MNE-sample-data-bids")

bids_root = os.path.join(demo_data_root, "rawdata")
deriv_root = os.path.join(demo_data_root, "derivatives", "mne-bids-pipeline")
subjects_dir = os.path.join(demo_data_root, "derivatives", "freesurfer", "subjects")

subjects = ["01"]
rename_events = {"Smiley": "Emoji", "Button": "Switch"}
conditions = ["Auditory", "Visual", "Auditory/Left", "Auditory/Right"]
epochs_metadata_query = "index > 0"
contrasts = [("Visual", "Auditory"), ("Auditory/Right", "Auditory/Left")]

time_frequency_conditions = ["Auditory", "Visual"]

ch_types = ["meg", "eeg"]
mf_reference_run = "01"
find_flat_channels_meg = True
find_noisy_channels_meg = True
use_maxwell_filter = True


def noise_cov(bp):
    # Estimate the noise covariance.
    # Use pre-stimulus period as noise source
    bp = bp.copy().update(suffix="epo")
    if not bp.fpath.exists():
        bp.update(split="01")
    epo = mne.read_epochs(bp)
    cov = mne.compute_covariance(epo, rank="info", tmax=0)
    return cov


spatial_filter = "ssp"
n_proj_eog = dict(n_mag=1, n_grad=1, n_eeg=1)
n_proj_ecg = dict(n_mag=1, n_grad=1, n_eeg=0)
ssp_meg = "combined"
ecg_proj_from_average = True
eog_proj_from_average = False
epochs_decim = 4

run_source_estimation = False

n_jobs = 2