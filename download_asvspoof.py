import os
import requests
import zipfile
import io

# Directory to store dataset
DATASET_DIR = "dataset"
ASVSPOOF_URL = "https://datashare.is.ed.ac.uk/bitstream/handle/10283/3336/LA.zip" # Official 2019 Logic Access
# Note: This file is 6.4GB. 

def setup_directories():
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)
        print(f"Created directory: {DATASET_DIR}")
    else:
        print(f"Directory exists: {DATASET_DIR}")

def instructions():
    print("="*60)
    print("ASVspoof 2019 Dataset Setup")
    print("="*60)
    print(f"The full dataset is approximately 6.4GB.")
    print(f"We recommend you download it manually if you have a slow connection.")
    print(f"\nDirect Link: {ASVSPOOF_URL}")
    print(f"\nINSTRUCTIONS:")
    print(f"1. Download the zip file.")
    print(f"2. Extract it into the '{os.path.abspath(DATASET_DIR)}' folder.")
    print(f"3. Ensure the structure looks like:")
    print(f"   {DATASET_DIR}/LA/ASVspoof2019_LA_train/flac/... (Audio files)")
    print(f"   {DATASET_DIR}/LA/ASVspoof2019_LA_cm_protocols/ASVspoof2019.LA.cm.train.trn.txt (Labels)")
    print("="*60)

def download_sample():
    # Since we can't easily download 6GB in a demo script without risk of timeout,
    # This function is a placeholder for where a 'sample' downloader would go 
    # if a smaller subset URL existed. 
    # For now, we print instructions.
    pass

if __name__ == "__main__":
    setup_directories()
    instructions()
    # verify_setup()
