import os
import requests

def upload_dicoms(root_dir):
    orthanc_url = "http://localhost:8042/instances"
    
    count = 0
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".dcm"):
                filepath = os.path.join(root, file)
                with open(filepath, 'rb') as f:
                    response = requests.post(orthanc_url, data=f.read())
                    if response.status_code == 200:
                        count += 1
                        if count % 50 == 0:
                            print(f"Uploaded {count} instances...")
                    else:
                        print(f"Failed to upload {filepath}: {response.status_code}")
    
    print(f"Total upload complete: {count} instances.")

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload DICOM files to Orthanc.")
    parser.add_argument("--dir", required=True, help="Root directory containing DICOM files to upload")
    parser.add_argument("--url", default="http://localhost:8042/instances", help="Orthanc instances URL")
    args = parser.parse_args()

    upload_dicoms(args.dir)
