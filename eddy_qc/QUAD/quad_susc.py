import glob
import os
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from eddy_qc.utils import fslpy
import seaborn
seaborn.set()


#=========================================================================================
# QUAD - Susceptibility distortions
# Matteo Bastiani
# 01-06-2017, FMRIB, Oxford
#=========================================================================================

def main(pdf, data, eddy):
    """
    Generate page of the single subject report pdf that contains 3 example slices (1 axial, 
    1 coronal and 1 sagittal) from the estimated displacement field (if provided). 
    Same projections are shown for averaged b0s with coherent PE direction.
    
    Arguments:
        - pdf: qc pdf file
        - data: data dictionary containg information about the dataset
        - eddy: EDDY dictionary containg useful qc information
    """
    #================================================
    # Prepare figure
    plt.figure(figsize=(8.27,11.69))   # Standard portrait A4 sizes
    plt.suptitle('Subject ' + data['subj_id'],fontsize=10, fontweight='bold')

    # Projections of undistorted b0 volumes averaged according to their PE direction
    count = 0
    for i in range(0, data['no_PE_dirs']):
        # Compute average b=x volume
        # fslpy.select_dwi_vols(data=data['subj_id'], bvals=data['bvals_id'], output=data['qc_path'] + "/avg_b" + str(b), b=b, m=True)
        idxs_b0_pe=np.where(np.array(data['eddy_idxs'] == data['unique_pedirs'][i]) * np.array(data['bvals'] == 0))
        vol = nib.Nifti1Image(np.mean(data['eddy_epi'].get_data()[..., idxs_b0_pe], axis=3), data['eddy_epi'].get_affine(), data['eddy_epi'].header)
        nib.save(vol, data['qc_path'] + "/avg_b0_pe" + str(i) + ".nii.gz")
        vol = vol.get_data()
        i_max = np.round(np.mean(vol[:,:,:][data['mask'] != 0.0])+3*np.std(vol[:,:,:][data['mask'] != 0.0]))
        fslpy.slicer(data['qc_path'] + "/avg_b0_pe" + str(i), a=data['qc_path'] + "/avg_b0_pe" + str(i) + ".png", i=(0, i_max))
        img=mpimg.imread(data['qc_path'] + "/avg_b0_pe" + str(i) + ".png")
        ax = plt.subplot2grid((1+data['no_PE_dirs'], 1), (count, 0))
        im = ax.imshow(img, interpolation='none', cmap="gray", vmin = 0, vmax=i_max)
        plt.colorbar(im, ax = ax)
        ax.grid(False)
        ax.axis('off')
        ax.set_title("Average b0 signal (PE=[" + np.array_str(data['eddy_para'][4*i:4*i+3]) + "])")
        count+=1
        data['eddy_epi'].uncache()
        del vol
    
    # Projections of voxel displacement map
    fieldImg = nib.load(eddy['fieldFile'])
    vol = nib.Nifti1Image((fieldImg.get_data())*data['eddy_para'][3], fieldImg.get_affine(), fieldImg.header)
    nib.save(vol, data['qc_path'] + "/vdm.nii.gz")
    vol = vol.get_data()
    i_max = np.round(np.mean(vol[:,:,:][data['mask'] != 0.0])+3*np.std(vol[:,:,:][data['mask'] != 0.0]))
    fslpy.slicer(data['qc_path'] + "/vdm", a=data['qc_path'] + "/vdm.png", i=(-i_max, i_max))
    img=mpimg.imread(data['qc_path'] + "/vdm.png")
    ax = plt.subplot2grid((1+data['no_PE_dirs'], 1), (count, 0))
    im = ax.imshow(img, interpolation='none', cmap="gray", vmin = -i_max, vmax=i_max)
    plt.colorbar(im, ax = ax)
    ax.grid(False)
    ax.axis('off')
    ax.set_title("Voxel displacement map")
    fieldImg.uncache()
    del vol


    # Clear temporary volume files
    for f in glob.glob(data['qc_path'] + "/*.nii.gz"):
        os.remove(f)

    # Format figure, save and close it
    plt.tight_layout(h_pad=1, pad=4)
    plt.savefig(pdf, format='pdf')
    plt.close()
    