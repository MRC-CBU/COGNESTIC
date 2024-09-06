#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Dace Apšvalka
# Created Date: 2024-01-27
# =============================================================================
# This script downloads the events.tsv files from the OpenNeuro dataset and
# saves them in the BIDS directory structure.
# The script also fixes the events.tsv files to comply with BIDS.
# !!! It also adds 2TRs to the onset times to account for the dummy scans which were 
# removed in the OpenNeuro version, but not in this re-analysis version!
# =============================================================================

# Import libraries
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ------------------------------------------------------------------------------
# Define variables
# ------------------------------------------------------------------------------
base_url = 'https://openneuro.org/crn/datasets/ds000117/snapshots/1.0.5/files/{subject_id}:ses-mri:func:{subject_id}_ses-mri_task-facerecognition_{run_id}_events.tsv'
bids_dir = '/imaging/correia/da05/workshops/Wakeman-ds/data'

nsubjects = 16
nruns = 9
task_label = 'faceprocessing' # the task lable as I want it to be (in the original dataset it is 'facerecognition')

# ------------------------------------------------------------------------------
# Check if the BIDS directory exists
if not os.path.exists(bids_dir):
    logging.error(f"BIDS directory {bids_dir} does not exist. Please create it first.")
    exit()

#------------------------------------------------------------------------------
# Function to download a file fron OpenNeuro base_url
#------------------------------------------------------------------------------
def download_file(subject_id, run_id, session):
    try:
        url = base_url.format(subject_id=subject_id, run_id=run_id)
        # Change task label my desired lable
        file_path = os.path.join(bids_dir, subject_id, 'func', f"{subject_id}_task-{task_label}_{run_id}_events.tsv")

        with session.get(url, stream=True) as response:
            if response.status_code == 200:
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                logging.info(f"Downloaded {file_path}")
            else:
                logging.error(f"Failed to download {subject_id} {run_id}. Status code: {response.status_code}")
                return None

        return file_path
    except Exception as e:
        logging.error(f"Exception occurred while downloading file for {subject_id} {run_id}: {e}")
        return None

#------------------------------------------------------------------------------
# Fix OpenNeuro event files to comply with BIDS
#------------------------------------------------------------------------------
def fix_events_file(file_path):
    try:
        events = pd.read_csv(file_path, sep='\t')
        # add 4 seconds to the onset times to account for the 2 TRs that were removed in the OpenNeuro version
        events['onset'] = events['onset'] + 4
        # change the column name 'stim_type' to 'trial_type'
        events.rename(columns={"stim_type": "trial_type"}, inplace=True)
        # remove rows with empty 'trial_type'
        events = events[events['trial_type'].notna() & (events['trial_type'] != "")]
        events.to_csv(file_path, sep="\t", index=False)
        logging.info(f"Fixed {file_path}")
    except Exception as e:
        logging.error(f"Exception occurred while fixing file {file_path}: {e}")

# ------------------------------------------------------------------------------
# Both functions combined
# ------------------------------------------------------------------------------
def download_and_fix(subject_id, run_id, session):
    file_path = download_file(subject_id, run_id, session)
    if file_path:
        fix_events_file(file_path)
        
#------------------------------------------------------------------------------
# Main execution
#------------------------------------------------------------------------------
def main():
    with requests.Session() as session:
        adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20, max_retries=Retry(total=5, backoff_factor=0.1))
        session.mount('https://', adapter)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            for subject in range(1, nsubjects+1):
                subject_id = f"sub-{subject:02d}"
                for run in range(1, nruns+1):
                    run_id = f"run-{run:02d}"
                    executor.submit(download_and_fix, subject_id, run_id, session)

if __name__ == "__main__":
    main()