import nibabel as nib
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ExplicitVRLittleEndian
import datetime
import os
import uuid

def convert_nii_to_dicom(nii_path, output_dir, patient_name, study_description, series_description):
    # Load NIfTI file
    img = nib.load(nii_path)
    data = img.get_fdata()
    
    # Normalize data for 16-bit integer (typical for MRI DICOM)
    # This is a simple linear normalization
    data = data - np.min(data)
    if np.max(data) > 0:
        data = (data / np.max(data) * 65535).astype(np.uint16)
    else:
        data = data.astype(np.uint16)

    # Output directory for this series
    series_dir = os.path.join(output_dir, patient_name, study_description, series_description)
    os.makedirs(series_dir, exist_ok=True)

    # Basic UIDs for the study/series
    study_instance_uid = pydicom.uid.generate_uid()
    series_instance_uid = pydicom.uid.generate_uid()
    
    # Iterate through slices (assuming 3rd dimension is slices)
    # Handle different orientations if necessary, but keep it simple for now
    num_slices = data.shape[2]
    
    for i in range(num_slices):
        slice_data = data[:, :, i].astype(np.uint16)
        
        # Create DICOM metadata
        file_meta = Dataset()
        file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.4' # MR Image Storage
        file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
        file_meta.ImplementationClassUID = pydicom.uid.generate_uid()
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

        filename = f"slice_{i:03d}.dcm"
        filepath = os.path.join(series_dir, filename)
        ds = FileDataset(filepath, {}, file_meta=file_meta, preamble=b"\0" * 128)
        ds.is_little_endian = True
        ds.is_implicit_VR = False

        # Standard DICOM tags
        ds.PatientName = patient_name
        ds.PatientID = patient_name.replace("sub-", "")
        ds.ContentDate = datetime.datetime.now().strftime('%Y%m%d')
        ds.ContentTime = datetime.datetime.now().strftime('%H%M%S.%f')
        ds.StudyInstanceUID = study_instance_uid
        ds.SeriesInstanceUID = series_instance_uid
        ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
        ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
        
        ds.Modality = "MR"
        ds.StudyDescription = study_description
        ds.SeriesDescription = series_description
        ds.InstanceNumber = str(i + 1)
        
        # Image Pixel data
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.PixelRepresentation = 0
        ds.HighBit = 15
        ds.BitsStored = 16
        ds.BitsAllocated = 16
        ds.Rows = slice_data.shape[0]
        ds.Cols = slice_data.shape[1]
        ds.PixelData = slice_data.tobytes()

        ds.save_as(filepath)
    
    print(f"Converted {nii_path} to {num_slices} DICOM slices in {series_dir}")

import argparse

def main():
    parser = argparse.ArgumentParser(description="Convert NIfTI files to DICOM series.")
    parser.add_argument("--source", required=True, help="Root directory containing subject folders (e.g., /path/to/sub)")
    parser.add_argument("--output", required=True, help="Output directory for DICOM files")
    args = parser.parse_args()

    source_base = args.source
    output_base = args.output

    if not os.path.exists(source_base):
        print(f"Error: Source directory '{source_base}' does not exist.")
        return

    # Automatically find all sub-* directories
    subjects = [d for d in os.listdir(source_base) if os.path.isdir(os.path.join(source_base, d)) and d.startswith("sub-")]

    if not subjects:
        print(f"No subject directories (starting with 'sub-') found in {source_base}")
        return

    for sub in subjects:
        sub_path = os.path.join(source_base, sub)
        
        for file in os.listdir(sub_path):
            if file.endswith(".nii.gz"):
                nii_path = os.path.join(sub_path, file)
                # cleanup filename to be used as series description
                series_desc = file.replace(f"{sub}_", "").replace(".nii.gz", "")
                
                convert_nii_to_dicom(
                    nii_path=nii_path,
                    output_dir=output_base,
                    patient_name=sub,
                    study_description="Brain MRI Restoration",
                    series_description=series_desc
                )

if __name__ == "__main__":
    main()
