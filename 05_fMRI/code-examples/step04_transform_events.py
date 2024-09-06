#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Dace Apšvalka
# Created Date: 2024-08
# =============================================================================
# This script edits events.tsv files acquired from the OpenNeuro dataset. 
# In the OpenNeuro dataset, there are only three conditions: FAMOUS, UNFAMILIAR, and SCRAMBLED.
# Here we split each condition into three events: 
# _1 (first presentation), _2im (second immediate presentation), and _2dl (second delayed presentation).
# =============================================================================

import pandas as pd
from bids.layout import BIDSLayout

bids_dir = '/imaging/correia/da05/workshops/Wakeman-ds/data'

layout = BIDSLayout(bids_dir)

# Get all the events files
events_files = layout.get(suffix='events', extension='tsv', return_type='file')

def transform_events_table(input_file, output_file):
    """
    Transforms the events table by categorizing each trial type into three different events: 
    _1 (first presentation), _2im (second immediate presentation), and _2dl (second delayed presentation).

    Parameters:
    - input_file: Path to the input CSV file containing the events table.
    - output_file: Path to the output CSV file to save the transformed events table.
    """
    # Load the data
    data = pd.read_csv(input_file, delimiter='\t')

    # Initialize dictionaries to track the occurrences of each stimulus file
    stimulus_occurrences = {}

    # List to store the modified rows
    modified_rows = []

    # Iterate through each row in the DataFrame
    for index, row in data.iterrows():
        stim_file = row['stim_file']
        trial_type = row['trial_type']

        if stim_file not in stimulus_occurrences:
            # First occurrence of this stimulus
            stimulus_occurrences[stim_file] = [index]
            new_trial_type = f"{trial_type}_1"
        else:
            # If it's the second occurrence
            if len(stimulus_occurrences[stim_file]) == 1:
                if index == stimulus_occurrences[stim_file][0] + 1:
                    # Immediate repeat
                    new_trial_type = f"{trial_type}_2im"
                else:
                    # Delayed repeat
                    new_trial_type = f"{trial_type}_2dl"
            stimulus_occurrences[stim_file].append(index)

        # Add the modified trial type to the row
        modified_row = row.copy()
        modified_row['trial_type'] = new_trial_type
        modified_rows.append(modified_row)

    # Create a new DataFrame from the modified rows
    modified_data = pd.DataFrame(modified_rows)

    # Save the modified DataFrame to a new CSV file
    modified_data.to_csv(output_file, index=False, sep='\t')

    print(f"The events table has been successfully transformed and saved as '{output_file}'.")

# Example usage:
# transform_events_table('/path/to/input.csv', '/path/to/output.csv')

# For all events files apply the function
for events_file in events_files:
    transform_events_table(events_file, events_file)
