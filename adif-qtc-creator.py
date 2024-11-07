#!/usr/bin/python

import adif_io
import pickle
import os
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Parse ADIF file in batches.")
parser.add_argument("-f", "--file", required=True, help="Path to the ADIF file")
parser.add_argument("-b", "--batch", type=int, default=10, help="Number of QSOs per batch")
args = parser.parse_args()

file_path = args.file
batch_size = args.batch
state_file = f"/var/tmp/{file_path.replace("/","_")}_state.pkl"  # Unique state file for each ADIF file

# Load processed index if state file exists
if os.path.exists(state_file):
    with open(state_file, 'rb') as f:
        start_index = pickle.load(f)
else:
    start_index = 0

# Parse the ADIF file
with open(file_path, 'r') as file:
    logbook_data, _ = adif_io.read_from_string(file.read())

# Determine the batch to process
end_index = start_index + batch_size
current_batch = logbook_data[start_index:end_index]

# Check if there are enough QSOs in the current batch
if len(current_batch) < batch_size:
    print("Warning: Not enough QSOs remaining for a full batch.")
else:
    # Display the batch
    batch_number = (start_index // batch_size) + 1
    print(f"QTC {batch_number}/{batch_size}")
    for qso in current_batch:
        time_on = qso.get("TIME_ON", "")[:4]  # Keep only HHMM
        call = qso.get("CALL", "")
        srx = qso.get("SRX", "")
        print(f"{time_on} {call} {srx}")
    print(f"PSE QSL for QTC {batch_number}/{batch_size}\n")

    # Update and save the processed index
    start_index = end_index
    with open(state_file, 'wb') as f:
        pickle.dump(start_index, f)
