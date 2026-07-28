import os
import subprocess
import time

#------------------------------------------------------------
# Specify the paths
#------------------------------------------------------------
BIDS_PATH = "/imaging/correia/da05/workshops/FaceRecognition/data"
OUTPUT_PATH = "/imaging/correia/da05/workshops/FaceRecognition/data/derivatives/fmriprep"
FREESURFER_LICENSE = "/imaging/correia/da05/workshops/FaceRecognition/freesurfer_license.txt"
WORK_PATH = "/imaging/correia/da05/workshops/FaceRecognition/scratch/fmriprep"

if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)
if not os.path.exists(WORK_PATH):
    os.makedirs(WORK_PATH)

#------------------------------------------------------------
# Function to submit fMRIPrep to sbatch
#------------------------------------------------------------
def submit_fmriprep_job(BIDS_PATH, OUTPUT_PATH, WORK_PATH, FREESURFER_LICENSE, subject):
    # Create a SLURM job script for the subject
    job_script = f"""#!/bin/bash
#SBATCH --job-name=fmriprep_{subject}
#SBATCH --output={WORK_PATH}/fmriprep_{subject}_%j.out
#SBATCH --error={WORK_PATH}/fmriprep_{subject}_%j.err
#SBATCH --time=7-00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8

start=$(date +%s)
date
echo "Submitted subject: {subject}"

# Load the apptainer module
module load apptainer

# Run fMRIPrep
apptainer run \\
    -B {BIDS_PATH}:/data:ro \\
    -B {OUTPUT_PATH}:/out \\
    -B {WORK_PATH}:/work \\
    -B {FREESURFER_LICENSE}:/freesurfer_license.txt:ro \\
    /imaging/local/software/singularity_images/fmriprep/fmriprep-24.1.1.sif \\
    /data /out participant \\
    --participant_label {subject} \\
    --work-dir /work \\
    --fs-license-file /freesurfer_license.txt \\
    --output-space MNI152NLin6Asym:res-2 \\
    --fs-no-reconall \\
    --nthreads 16 --omp-nthreads 8 \\
    --skip-bids-validation \\
    --stop-on-first-crash

# Unload the apptainer module    
module unload apptainer

# processing end time
end=$(date +%s)
date
echo Time elapsed: "$(TZ=UTC0 printf '%(%H:%M:%S)T\n' $((end - start)))"

    """

    # Write the job script to a temporary file
    job_script_file = os.path.join(
        WORK_PATH, f"fmriprep_{subject}.sh")
    with open(job_script_file, "w") as f:
        f.write(job_script)
    
    # Submit the job script to SLURM using sbatch
    try:
        subprocess.run(["sbatch", job_script_file], check=True)
        print(f"Submitted job for subject {subject}")

        # After submission, delete the job script
        os.remove(job_script_file)
        print(f"Deleted job script: {job_script_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error submitting job for subject {subject}: {e}")
        
#------------------------------------------------------------
# Main loop through subjects
#------------------------------------------------------------

# Get all directories that start with 'sub-'
subject_dirs = [d for d in os.listdir(BIDS_PATH) if os.path.isdir(os.path.join(BIDS_PATH, d)) and d.startswith('sub-')]

# Extract the subject IDs by stripping the 'sub-' prefix
SUBJECT_IDs = [d.replace('sub-', '') for d in subject_dirs]

for subject in SUBJECT_IDs:
    # Submit fMRIPrep job to SLURM
    submit_fmriprep_job(BIDS_PATH, OUTPUT_PATH, WORK_PATH, FREESURFER_LICENSE, subject)
    
    # Sleep 1 min 
    # Fmriprep: Workaround for running subjects in parallel 
    # https://neurostars.org/t/updated-fmriprep-workaround-for-running-subjects-in-parallel/6677)
    time.sleep(60)