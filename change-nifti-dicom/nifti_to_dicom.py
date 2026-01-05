#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import uuid
import numpy as np
import nibabel as nib
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid
from datetime import datetime


# ---------------------------
# 🔹 상대 경로 하드코딩 설정
# ---------------------------

# 스크립트 파일 기준 기준 디렉터리
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# NIfTI 파일들이 들어있는 폴더 (상대경로 ../ai_data)
NIFTI_ROOT = os.path.normpath(os.path.join(BASE_DIR, "./sub-0005-nifti"))

# 변환된 dicom 출력 폴더 (../ai_data/dicom_out)
OUTPUT_ROOT = os.path.normpath(os.path.join(BASE_DIR, "./sub-0005-dicom"))



def normalize_to_uint16(data):
    data = np.asarray(data, dtype=np.float32)
    dmin = np.nanmin(data)
    dmax = np.nanmax(data)
    if dmax <= dmin:
        return np.zeros_like(data, dtype=np.uint16)
    norm = (data - dmin) / (dmax - dmin)
    return (norm * 65535).astype(np.uint16)


def nifti_to_slices(data):
    data = np.asarray(data)
    if data.ndim == 2:
        return [data]
    elif data.ndim == 3:
        return [data[:, :, i] for i in range(data.shape[2])]
    elif data.ndim == 4:
        x, y, z, t = data.shape
        reshaped = data.reshape(x, y, z * t)
        return [reshaped[:, :, i] for i in range(reshaped.shape[2])]
    else:
        raise ValueError(f"지원하지 않는 차원: {data.shape}")


def create_dicom_from_slice(slice_2d, study_uid, series_uid,
                            patient_name="Anon", patient_id="0000",
                            modality="MR", series_description="", instance_number=1):

    now = datetime.now()
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.MRImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.ImplementationClassUID = generate_uid()
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

    ds = FileDataset("", {}, file_meta=file_meta, preamble=b"\0" * 128)

    ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID

    ds.PatientName = patient_name
    ds.PatientID = patient_id

    ds.StudyInstanceUID = study_uid
    ds.SeriesInstanceUID = series_uid
    ds.StudyDate = now.strftime("%Y%m%d")
    ds.StudyTime = now.strftime("%H%M%S")
    ds.SeriesDescription = series_description
    ds.Modality = modality
    ds.InstanceNumber = instance_number

    rows, cols = slice_2d.shape
    ds.Rows = rows
    ds.Columns = cols
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 0

    ds.PixelData = slice_2d.astype(np.uint16).tobytes()

    ds.ImagePositionPatient = [0.0, 0.0, float(instance_number)]
    ds.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
    ds.PixelSpacing = [1.0, 1.0]
    ds.SliceThickness = 1.0

    return ds


def convert_nifti_file(nifti_path, output_root):
    base_name = os.path.basename(nifti_path)

    if base_name.endswith(".nii.gz"):
        folder_name = base_name[:-7]
    elif base_name.endswith(".nii"):
        folder_name = base_name[:-4]
    else:
        folder_name = os.path.splitext(base_name)[0]

    out_dir = os.path.join(output_root, folder_name)
    os.makedirs(out_dir, exist_ok=True)

    img = nib.load(nifti_path)
    data = normalize_to_uint16(img.get_fdata())
    slices = nifti_to_slices(data)

    study_uid = generate_uid()
    series_uid = generate_uid()

    for idx, slc in enumerate(slices, start=1):
        ds = create_dicom_from_slice(
            slice_2d=slc,
            study_uid=study_uid,
            series_uid=series_uid,
            series_description=folder_name,
            instance_number=idx,
        )

        dicom_path = os.path.join(out_dir, f"IM_{idx:04d}.dcm")
        ds.save_as(dicom_path, write_like_original=False)

    print(f"[OK] {base_name} → {len(slices)} DICOM saved → {out_dir}")


def run_conversion():
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    if not os.path.isdir(NIFTI_ROOT):
        print(f"[ERROR] NIfTI 폴더가 없습니다: {NIFTI_ROOT}")
        return

    for root, _, files in os.walk(NIFTI_ROOT):
        for f in files:
            lf = f.lower()
            if lf.endswith(".nii") or lf.endswith(".nii.gz"):
                convert_nifti_file(os.path.join(root, f), OUTPUT_ROOT)


if __name__ == "__main__":
    print(f"NIFTI_ROOT  = {NIFTI_ROOT}")
    print(f"OUTPUT_ROOT = {OUTPUT_ROOT}")
    run_conversion()
