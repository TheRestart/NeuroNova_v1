import gzip
import io
import numpy as np
import scipy.io

def load_dsi_file(file_path):
    """
    DSI Studio의 .fz 또는 .sz 파일을 로드합니다.
    이 파일들은 gzip으로 압축된 MATLAB (.mat) 파일입니다.
    """
    with gzip.open(file_path, 'rb') as f:
        content = f.read()
        # io.BytesIO를 사용하여 메모리 내에서 .mat 파일을 읽습니다.
        mat_data = scipy.io.loadmat(io.BytesIO(content))
    return mat_data

def extract_src_data(mat_data):
    """
    .sz (Source) 파일에서 DWI 데이터를 추출하고 복원합니다.
    DSI Studio는 마스크 영역의 데이터만 저장하므로 이를 원래의 차원으로 복원해야 합니다.
    """
    dim = mat_data['dimension'][0]  # [x, y, z]
    voxel_size = mat_data['voxel_size'][0]
    mask = mat_data['mask'].flatten()
    
    # 이미지 볼륨(image0, image1, ...)을 찾습니다.
    image_keys = [k for k in mat_data.keys() if k.startswith('image')]
    image_keys.sort(key=lambda x: int(x[5:]) if x[5:].isdigit() else -1)
    
    # slope와 inter를 이용한 스케일링 복원
    # (data * slope + inter)
    slope = mat_data.get('slope', np.array([[1.0]]))[0, 0]
    inter = mat_data.get('inter', np.array([[0.0]]))[0, 0]
    
    num_volumes = len(image_keys)
    full_image = np.zeros((*dim, num_volumes), dtype=np.float32)
    
    for i, key in enumerate(image_keys):
        # 마스크된 평면 데이터를 가져옵니다.
        masked_data = mat_data[key].flatten()
        
        # 원래 크기의 볼륨 생성
        vol = np.zeros(np.prod(dim), dtype=np.float32)
        vol[mask > 0] = masked_data
        
        # 스케일링 적용 및 재배열
        vol = vol.reshape(dim, order='F') # DSI Studio는 Fortran order(Column-major) 사용 가능성 확인 필요
        full_image[..., i] = vol * slope + inter
        
    b_table = mat_data.get('b_table', None)
    
    return {
        'image': full_image,
        'b_table': b_table,
        'voxel_size': voxel_size,
        'dimension': dim
    }

def extract_fib_data(mat_data, key_to_extract=None):
    """
    .fz (Fiber) 파일에서 분석 데이터를 추출합니다.
    key_to_extract가 지정되면 해당 파일의 마스크와 차원을 사용하여 3D 볼륨으로 복원합니다.
    """
    dim = mat_data['dimension'][0]  # [x, y, z]
    mask = mat_data['mask'].flatten()
    
    if key_to_extract and key_to_extract in mat_data:
        data = mat_data[key_to_extract].flatten()
        # slope/inter 적용
        slope_key = f"{key_to_extract}.slope"
        inter_key = f"{key_to_extract}.inter"
        slope = mat_data.get(slope_key, np.array([[1.0]]))[0, 0]
        inter = mat_data.get(inter_key, np.array([[0.0]]))[0, 0]
        
        # 볼륨 복원
        full_vol = np.zeros(np.prod(dim), dtype=np.float32)
        full_vol[mask > 0] = data
        full_vol = full_vol.reshape(dim, order='F')
        return full_vol * slope + inter
        
    result = {}
    for key in mat_data.keys():
        if not key.startswith('__'):
            result[key] = mat_data[key]
    return result

def plot_slice(volume, slice_idx=None, axis=2, title='Slice View', save_path=None):
    """
    matplotlib을 사용하여 볼륨의 슬라이스를 시각화합니다.
    """
    import matplotlib.pyplot as plt
    
    if slice_idx is None:
        slice_idx = volume.shape[axis] // 2
        
    if axis == 0:
        slice_data = volume[slice_idx, :, :]
    elif axis == 1:
        slice_data = volume[:, slice_idx, :]
    else:
        slice_data = volume[:, :, slice_idx]
        
    plt.figure(figsize=(8, 8))
    plt.imshow(slice_data.T, cmap='gray', origin='lower')
    plt.title(f"{title} (Slice {slice_idx})")
    plt.colorbar()
    
    if save_path:
        plt.savefig(save_path)
        print(f"Saved visualization to {save_path}")
    else:
        plt.show()

def save_as_nifti(volume, voxel_size, save_path):
    """
    데이터를 NIfTI (.nii.gz) 형식으로 저장합니다.
    """
    import nibabel as nib
    # DSI Studio 데이터는 보통 LPS 또는 RAS 확인이 필요하지만 
    # 기본적으로 대각 행렬을 사용하여 저장합니다.
    affine = np.diag([*voxel_size, 1.0])
    img = nib.Nifti1Image(volume, affine)
    nib.save(img, save_path)
    print(f"Exported to NIfTI: {save_path}")

def export_b_table(mat_data, base_path):
    """
    .sz 파일에서 bval, bvec 파일을 추출합니다.
    """
    if 'b_table' not in mat_data:
        print("No b_table found in data.")
        return
        
    b_table = mat_data['b_table'] # 4 x N matrix (b, gx, gy, gz)
    bvals = b_table[0, :]
    bvecs = b_table[1:4, :] # 3 x N
    
    np.savetxt(f"{base_path}.bval", bvals[None, :], fmt='%d')
    np.savetxt(f"{base_path}.bvec", bvecs, fmt='%.8f')
    print(f"Exported bval/bvec to {base_path}.bval/bvec")

def visualize_3d_interactive(volume, title='3D Volume', save_path=None):
    """
    Plotly를 사용하여 대화형 3D 볼륨 렌더링을 생성합니다.
    """
    import plotly.graph_objects as go
    
    # 렌더링 부하를 줄이기 위해 다운샘플링 고려 가능
    # 여기서는 원본 데이터를 사용하되 샘플링 간격을 조정할 수 있습니다.
    X, Y, Z = np.mgrid[0:volume.shape[0], 0:volume.shape[1], 0:volume.shape[2]]
    
    fig = go.Figure(data=go.Volume(
        x=X.flatten(),
        y=Y.flatten(),
        z=Z.flatten(),
        value=volume.flatten(),
        isomin=volume.min() + (volume.max() - volume.min()) * 0.1,
        isomax=volume.max(),
        opacity=0.1, # 투명도 조절
        surface_count=20, # 표면 층 개수
        colorscale='Viridis',
    ))
    
    fig.update_layout(title=title)
    
    if save_path:
        fig.write_html(save_path)
        print(f"Interactive 3D visualization saved to {save_path}")
    else:
        fig.show()

if __name__ == "__main__":
    import sys
    import os
    if len(sys.argv) > 1:
        path = sys.argv[1]
        metric = sys.argv[2] if len(sys.argv) > 2 else 'fa0'
        
        print(f"Loading {path}...")
        data = load_dsi_file(path)
        
        if path.endswith('.sz'):
            extracted = extract_src_data(data)
            print(f"Extracted SRC Image Shape: {extracted['image'].shape}")
            
            # NIfTI 저장
            base_name = os.path.splitext(os.path.basename(path))[0]
            save_as_nifti(extracted['image'], extracted['voxel_size'], f"{base_name}.nii.gz")
            
            # b-table 내보내기
            export_b_table(data, base_name)
            
            # 첫 번째 볼륨 시각화
            plot_slice(extracted['image'][..., 0], title=f"SRC Volume 0", save_path="src_preview.png")
            
        elif path.endswith('.fz'):
            print(f"Extracting metric: {metric}")
            try:
                vol = extract_fib_data(data, metric)
                if isinstance(vol, np.ndarray):
                    print(f"Extracted {metric} Volume Shape: {vol.shape}")
                    
                    # NIfTI 저장
                    base_name = os.path.splitext(os.path.basename(path))[0]
                    save_as_nifti(vol, data['voxel_size'][0], f"{base_name}_{metric}.nii.gz")
                    
                    # 슬라이스 시각화
                    plot_slice(vol, title=f"FIB metric: {metric}", save_path=f"{metric}_preview.png")
                    
                    # 대화형 3D 시각화 (용량이 클 수 있어 HTML로 저장)
                    visualize_3d_interactive(vol, title=f"3D: {metric}", save_path=f"{metric}_3d.html")
                else:
                    print(f"Metric {metric} not found or not a volume. Available keys: {[k for k in data.keys() if not k.startswith('__')]}")
            except Exception as e:
                print(f"Error extracting metric: {e}")
    else:
        print("Usage: python dsi_utils.py <file_path.fz/sz> [metric_name]")
        print("Example: python dsi_utils.py data.fz fa0")
