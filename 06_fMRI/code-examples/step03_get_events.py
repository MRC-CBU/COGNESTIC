"""
This script downloads event files for a specific subject from the OpenNeuro dataset ds000117.
"""
import os
import urllib.request
from pathlib import Path

# Change to the directory where this script is located
os.chdir(Path(__file__).parent)

# -----------------------------------------------------------------------
# Specify the parameters for downloading event files
# -----------------------------------------------------------------------
BIDS_PATH = "../FaceRecognition/data"
SUBJECT_ID = "sub-15"
RUNS = [f"{i:02d}" for i in range(1, 10)]  # Runs 01 to 09

# -----------------------------------------------------------------------
# The output path for the event files
output_dir = Path(BIDS_PATH) / SUBJECT_ID / "ses-mri" / "func"

# Check if the output directory exists; exit otherwise
if not output_dir.exists():
    raise FileNotFoundError(f"{output_dir} does not exist. Create it first.")

# Download the event files for the specified subject and runs
for run in RUNS:
    file_name = f"{SUBJECT_ID}_ses-mri_task-facerecognition_run-{run}_events.tsv"
    url = f"https://s3.amazonaws.com/openneuro.org/ds000117/{SUBJECT_ID}/ses-mri/func/{file_name}"
    output_file = output_dir / file_name

    print(f"Downloading {file_name}...")

    try:
        urllib.request.urlretrieve(url, output_file)
    except Exception as e:
        print(f"Error downloading {file_name}: {e}")
        break
else:  # if for loop completes without break
    print("All files downloaded successfully.")